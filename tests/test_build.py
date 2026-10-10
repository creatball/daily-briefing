import importlib.util
from pathlib import Path
import tempfile
import unittest

spec=importlib.util.spec_from_file_location('builder',Path(__file__).resolve().parents[1]/'build.py')
builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)

class ImportTests(unittest.TestCase):
    def convert(self, body, name='2026-10-10.html'):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/name;path.write_text(body,encoding='utf-8')
            return builder.convert(path)

    def test_utf8_and_ipa(self):
        data,_,_=self.convert('<h2>日本語・中文</h2><p class="ipa">/ˈlevərɪdʒ θ ð æ ŋ/</p>')
        self.assertIn('日本語・中文',data['html']);self.assertIn('ˈlevərɪdʒ',data['html'])

    def test_script_and_attributes_removed(self):
        data,_,_=self.convert('<head><style>body{}</style></head><script>alert(1)</script><p onclick="bad()" style="color:red">Text</p><svg onload="bad()"><text>hidden</text></svg>')
        self.assertEqual(data['html'],'<p>Text</p>')

    def test_bad_url_blocks_build(self):
        for url in ['javascript:alert(1)','sandbox:/mnt/data/a.png','file:///etc/passwd','//evil.example/x','data:text/html,hello']:
            with self.subTest(url=url),self.assertRaises(ValueError):self.convert(f'<p>text</p><a href="{url}">source</a>')

    def test_source_link_retained(self):
        data,_,notes=self.convert('<p>Text <a href="https://example.com/a?x=1&amp;y=2">来源</a></p>')
        self.assertIn('https://example.com/a?x=1&amp;y=2',data['html']);self.assertEqual(notes,[])

    def test_anchors_scoped(self):
        data,_,_=self.convert('<a href="#article">go</a><h2 id="article">section</h2>')
        self.assertIn('href="#article-article"',data['html']);self.assertIn('id="article-article"',data['html'])

    def test_date_validated(self):
        with self.assertRaises(ValueError):self.convert('<p>x</p>','2026-02-30.html')

    def test_unresolved_citation_fails(self):
        with self.assertRaises(ValueError):self.convert('<p>:chatgpt-content-reference{index="1"}</p>')

    def test_local_image_retained(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);(root/'picture.png').write_bytes(b'fixture-image')
            (root/'2026-10-10.html').write_text('<p>Text</p><img src="picture.png" alt="test">',encoding='utf-8')
            data,assets,_=builder.convert(root/'2026-10-10.html')
            self.assertEqual(len(assets),1);self.assertIn('assets/2026-10-10/',data['html'])

    def test_image_path_traversal_rejected(self):
        with self.assertRaises(ValueError):self.convert('<p>x</p><img src="../secret.png">')

    def test_build_failure_keeps_previous_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);(root/'incoming').mkdir();(root/'dist').mkdir()
            (root/'dist/index.html').write_text('previous')
            (root/'incoming/2026-10-10.html').write_text('<p>bad</p><img src="sandbox:/x">')
            with self.assertRaises(ValueError):builder.build(root)
            self.assertEqual((root/'dist/index.html').read_text(),'previous')

    def test_duplicate_date_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);(root/'incoming').mkdir()
            for name in ['2026-10-10.html','daily_2026-10-10.html']:(root/'incoming'/name).write_text('<p>text</p>')
            with self.assertRaisesRegex(ValueError,'Duplicate date'):builder.build(root)

if __name__=='__main__':unittest.main()
