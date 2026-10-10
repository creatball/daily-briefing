"""Build a static briefing site from UTF-8 HTML. Python 3.11+, standard library only."""
from __future__ import annotations
import argparse
import base64
import datetime as dt
import hashlib
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import shutil
from urllib.parse import urlsplit, unquote, quote

ROOT = Path(__file__).resolve().parent
ALLOWED = set('p div span section article header footer main h1 h2 h3 h4 h5 h6 ul ol li a img figure figcaption strong b em i u s small sub sup blockquote br hr table thead tbody tfoot tr td th caption details summary code pre ruby rt rp time dl dt dd'.split())
VOID = {'img', 'br', 'hr'}
DROP = set('head script style iframe object embed svg math template form button input textarea select noscript'.split())
RASTER = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.avif'}

class ArticleParser(HTMLParser):
    def __init__(self, source: Path, date: str):
        super().__init__(convert_charrefs=True)
        self.source, self.date = source, date
        self.parts, self.errors, self.assets = [], [], {}
        self.stack = []
        self.suppressed = []
        self.source_links = 0

    def safe_url(self, value, image=False):
        value = value.strip()
        if any(ord(c) < 32 for c in value):
            self.errors.append('URL contains control characters'); return None
        if value.startswith('#') and not image:
            return '#article-' + value[1:]
        parsed = urlsplit(value)
        if parsed.scheme == 'https' and parsed.netloc and not parsed.username and not parsed.password:
            if not image: self.source_links += 1
            return value
        if image and re.fullmatch(r'data:image/(?:png|jpeg|gif|webp);base64,[A-Za-z0-9+/=\s]+', value):
            try: base64.b64decode(value.split(',',1)[1], validate=True)
            except ValueError: self.errors.append('Invalid embedded image'); return None
            return value
        if image and not parsed.scheme and not parsed.netloc and not value.startswith(('/', '\\')):
            source = (self.source.parent / unquote(parsed.path)).resolve()
            if source.is_relative_to(self.source.parent.resolve()) and source.is_file() and source.suffix.lower() in RASTER:
                raw=source.read_bytes()
                target=f'assets/{self.date}/{hashlib.sha256(raw).hexdigest()[:20]}{source.suffix.lower()}'
                self.assets[target]=raw
                return './'+target
        self.errors.append('Unpublishable image or link: '+value[:120])
        return None

    def handle_starttag(self, tag, attrs):
        if self.suppressed:
            if tag not in {'meta','link','input','embed','br','hr','img','source','wbr'}: self.suppressed.append(tag)
            return
        if tag in DROP:
            if tag not in {'input','embed'}: self.suppressed.append(tag)
            return
        if tag not in ALLOWED: return
        data=dict(attrs); out=[]
        if data.get('id'): out.append(('id', 'article-'+data['id']))
        if data.get('lang'): out.append(('lang',data['lang']))
        if 'ipa' in (data.get('class') or '').split(): out.append(('class','ipa'))
        if tag=='a':
            href=self.safe_url(data.get('href',''))
            if href: out.extend([('href',href),('rel','noopener noreferrer')])
        if tag=='img':
            src=self.safe_url(data.get('src',''),True)
            if not src: return
            out.extend([('src',src),('alt',data.get('alt') or '简报配图'),('loading','lazy'),('decoding','async'),('referrerpolicy','no-referrer')])
        for attr in ('colspan','rowspan'):
            if tag in {'td','th'} and re.fullmatch(r'[1-9][0-9]?',data.get(attr) or ''):out.append((attr,data[attr]))
        attributes=''.join(' '+k+'="'+html.escape(v,quote=True)+'"' for k,v in out)
        self.parts.append('<'+tag+attributes+'>')
        if tag not in VOID:self.stack.append(tag)

    def handle_startendtag(self,tag,attrs):
        self.handle_starttag(tag,attrs)
        if tag not in VOID:self.handle_endtag(tag)

    def handle_endtag(self,tag):
        if self.suppressed:
            if tag in self.suppressed:
                index=len(self.suppressed)-1-self.suppressed[::-1].index(tag)
                del self.suppressed[index:]
            return
        if tag in self.stack:
            while self.stack:
                current=self.stack.pop();self.parts.append('</'+current+'>')
                if current==tag:break

    def handle_data(self,data):
        if not self.suppressed:self.parts.append(html.escape(data))

    def result(self):
        while self.stack:self.parts.append('</'+self.stack.pop()+'>')
        return ''.join(self.parts)

def convert(source):
    match=re.search(r'(\d{4}-\d{2}-\d{2})',source.stem)
    if not match:raise ValueError(f'{source.name}: filename needs YYYY-MM-DD')
    date=match[1];dt.date.fromisoformat(date)
    raw=source.read_text(encoding='utf-8-sig',errors='strict')
    if re.search(r'chatgpt-content-reference|sandbox:|\ue200|\ue202',raw):
        raise ValueError(f'{source.name}: unresolved ChatGPT citation or sandbox file; replace with a real HTTPS source/image')
    parser=ArticleParser(source,date);parser.feed(raw);parser.close();body=parser.result()
    if not re.sub('<[^>]+>','',body).strip():raise ValueError(f'{source.name}: empty article')
    if parser.errors:raise ValueError(source.name+':\n  '+'\n  '.join(parser.errors))
    record={'date':date,'title':'每日综合简报','html':body,'importedAt':dt.datetime.now(dt.timezone.utc).isoformat(),'sha256':hashlib.sha256(source.read_bytes()).hexdigest()}
    warnings=[]
    if not parser.source_links:warnings.append(f'{date}: no external HTTPS sources found; check content before publication')
    return record,parser.assets,warnings

def build(root=ROOT, demo=False):
    root=root.resolve();incoming=root/'incoming';site=root/'site';dist=root/'dist'
    records=[];assets={};warnings=[];dates=set()
    for source in sorted(incoming.glob('*.html')):
        record,media,notes=convert(source)
        if record['date'] in dates:raise ValueError('Duplicate date: '+record['date'])
        dates.add(record['date']);records.append(record);assets.update(media);warnings.extend(notes)
    # Parse every input before replacing an existing build. Never publish a partial issue.
    if dist.is_symlink() or (hasattr(dist,'is_junction') and dist.is_junction()):raise ValueError('dist must not be a link')
    if dist.exists():
        if dist.resolve().parent != root or dist.name!='dist':raise ValueError('Invalid output path')
        shutil.rmtree(dist)
    shutil.copytree(site,dist)
    (dist/'data').mkdir(exist_ok=True)
    def write_json(path,data):path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    for record in records:write_json(dist/'data'/f"{record['date']}.json",record)
    write_json(dist/'data/index.json',{'timezone':'Asia/Tokyo','issues':[{'date':x['date'],'title':x['title']} for x in sorted(records,key=lambda x:x['date'],reverse=True)]})
    for target,raw in assets.items():
        path=dist/target;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
    if demo:
        target=dist/'data/demo';target.mkdir()
        issues=[]
        for source in sorted((root/'examples').glob('*.html')):
            record,media,_=convert(source);record['title']='每天，一点新的视角';record.pop('importedAt',None)
            write_json(target/f"{record['date']}.json",record);issues.append({'date':record['date'],'title':record['title']})
            for name,raw in media.items():
                path=dist/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
        write_json(target/'index.json',{'issues':issues})
    (dist/'.nojekyll').touch()
    for warning in warnings:print('WARNING:',warning)
    print(f'Built {len(records)} real issues'+(' and isolated demo data' if demo else '')+' into '+str(dist))
    return records

if __name__=='__main__':
    cli=argparse.ArgumentParser();cli.add_argument('--demo',action='store_true',help='Include clearly labeled, separate demonstration issues');args=cli.parse_args()
    try:build(demo=args.demo)
    except (ValueError,UnicodeError,OSError) as error:raise SystemExit(str(error))
