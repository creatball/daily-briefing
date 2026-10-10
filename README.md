# 每日综合简报网站

本地交付日期：2026-10-10。用户已选择「仅自己访问，需要登录」，已有 GitHub 账户。尚未连接账户、创建仓库、部署网站或改动原 ChatGPT 定时任务。

## 已完成

- 手机单列阅读、桌面目录、跟随系统 / 浅色 / 深色、大字阅读。
- 按日本日期选择当天简报；当天缺稿时展示最新已发布一期并提示，不把昨天标为今天。未来日期不会自动成为首页。
- 历史选择、可收藏的 `?date=YYYY-MM-DD` 地址、浏览器前进 / 后退。
- UTF-8，IPA 专用字体回退，正文图片、图注、HTTPS 来源链接，折叠复习答案。
- 单文件 HTML 导入、日期去重、图片迁移、来源检查、GitHub 构建校验工作流。
- 默认构建不含演示内容；`--demo` 才加入独立样本。样本日期 2000-01-01 / 02，仅验证版式，不是真实历史简报。

原对话的读取结果只有 `sandbox:/mnt/data/...html` 附件链接，未提供附件本体。因此真实简报为 0 份；旧对话中新闻没有当成已验证资料转存。需上传现有 HTML 后才能完成实际内容兼容性验证。

## 本地使用

要求 Python 3.11+。不依赖第三方 Python 包。

```powershell
python build.py --demo
python -m http.server 8765 --bind 127.0.0.1 --directory dist
```

电脑打开 `http://127.0.0.1:8765/?demo=1`。这个本机地址不是手机公网网址。交付目录另有不需要服务器的「每日简报网站_离线预览.html」。

正式内容：把 HTML 放进 `incoming/`，文件名含 `YYYY-MM-DD`，例如 `每日综合简报_2026-10-10.html`。相对图片放在 HTML 附近、保持原相对路径。每次更新后运行：

```powershell
python -m unittest discover -s tests
python build.py
```

只发布 `dist/`。`incoming/` 留在私有仓库，不直接成为站点下载目录。构建前完整验证所有文件；失败时不更新上一份构建。构建会重建项目自己的 `dist/`，不要在里面手动保存原件。

导入器保留正文结构，移除原脚本、内联样式、表单及嵌入页面，并使用统一阅读样式。原文不是逐像素还原。HTTPS 链接原样保留；本地 PNG/JPEG/GIF/WebP/AVIF 会复制到按日期隔离的资源目录；HTTPS 图片不下载，仍依赖源站可用性。支持常见 base64 内嵌图片。临时 `sandbox:` 图片、缺失本地图片、内部 ChatGPT 引用、非 HTTPS 外链会阻止构建并指出位置，需在原文件中改为真实可用来源。脚本驱动内容、视频、SVG 图像等未实现，实际文件需检查是否包含这类元素。

IPA 回退顺序包括 Charis SIL / Doulos SIL / Noto Sans / Segoe UI / DejaVu Sans。已在 Windows Edge 检查 IPA 字符；iOS / Android 实机未验证。如目标设备仍缺字，应再加入获许可的本地 IPA 字体文件及许可证。

## 适合你的托管方案

推荐：**GitHub 私有仓库 + Cloudflare Pages + Cloudflare Access，仅允许你的指定登录邮箱**。

| 方案 | 手机访问 | 访问保护 | 成本与结论 |
| --- | --- | --- | --- |
| GitHub 普通 Pages | HTTPS 网址 | 通常公开；私有仓库不等于私有网站 | 公开仓库可用免费 Pages，但不符合本次仅自己访问要求 |
| GitHub Enterprise Cloud 私有 Pages | HTTPS + 账户权限 | 组织私有项目站点支持权限控制 | 若已有企业计划可评估，不建议只为一份简报购买 |
| Cloudflare Pages + Access | HTTPS + 登录 | 配置精确邮箱允许规则，其他人拒绝 | 推荐；单用户通常可在免费额度内，无需先买域名 |

Cloudflare Pages 免费计划列有每月 500 次构建，Access 免费计划上限 50 用户；每天一次发布通常足够。GitHub 私有仓库 Actions 受账户额度约束。自定义域名、超额服务和未来 API 生成另计，不承诺所有账户永远零费用。

官方依据：[GitHub 发布来源与公开性](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)、[私有 Pages 的企业要求](https://docs.github.com/en/enterprise-cloud%40latest/pages/getting-started-with-github-pages/changing-the-visibility-of-your-github-pages-site)、[Pages 免费额度](https://developers.cloudflare.com/pages/platform/limits/)、[Access 价格](https://www.cloudflare.com/plans/zero-trust-services/)。核实于 2026-10-10。

## 部署顺序（尚未执行）

1. 用户确认 Cloudflare 方案，确认 GitHub 用户名、私有仓库和 Cloudflare 账户；确认唯一允许登录的邮箱。通过账户连接登录，不在聊天或仓库里粘贴密码 / Token。
2. 先创建只含空页面的私有仓库和 Pages 项目，尚不放真实简报。构建命令 `python -m unittest discover -s tests && python build.py`，输出目录 `dist`，Python 3.13。
3. 按官方步骤把正式 `<项目>.pages.dev` 与所有预览 `*.<项目>.pages.dev` 都放到 Access 后面。只保护预览域名不够。若加自定义域名，也配置独立 Access 应用。
4. Access 的 Allow 只指定你的精确邮箱；不设 Everyone / Bypass。用允许的账户确认登录成功，用无痕未登录访问确认所有内容路径需要认证。
5. 核验首页、`/data/index.json`、具体日期 JSON、图片路径、正式域名和每个预览别名均受保护。`robots.txt`、noindex 和前端界面均不提供认证能力。
6. 保护有效后才提交真实 HTML，连接 Git 提交自动构建并发布。测试手机登录、历史日期、IPA 和图片。

依据：[Cloudflare 正式与预览域名的 Access 配置](https://developers.cloudflare.com/pages/platform/known-issues/#enable-access-on-your-pagesdev-domain)。本地网站没有实现或验证登录，访问保护依赖部署时配置。

仓库内 `.github/workflows/validate.yml` 只校验和生成私有仓库内的构建产物，不发布。`deployment/github-pages.yml.disabled` 是对比用途的公开发布模板，放在非工作流目录且禁用；本次私密方案不要启用。Cloudflare 的 Git 集成在确认后使用，不需要该 Pages 模板。

## 每天如何更新

当前事实：原对话称日本时间 08:50 启动，用户说明约 08:55 完成。这里未读取真实任务配置或运行记录，因此该时间是预期而不是在线 SLA。原任务不会因制作网站自动获得仓库写入权限。

### 路线 A：先接入原 HTML，上传后自动发布

每天从原 ChatGPT 对话下载 HTML → 在 GitHub 私有仓库的 `incoming/` 上传该文件及必要图片 → 提交触发校验 / Cloudflare 构建 → 登录网站查看。支持从手机浏览器操作 GitHub 文件上传。此路线保留现有生成方式，上传步骤仍是人工。

### 路线 B：保留 ChatGPT 生成，验证写入通道后全自动

官方说明，网页版定时任务可使用该聊天可用的连接工具，但不会持久保存本地文件夹。是否可以无人值守写入这个私有仓库，取决于原任务运行环境、插件能力、账户授权与写入确认机制；目前未验证，不能保证现有任务能直接自动同步。

先在原任务环境中做一次普通手动运行：生成测试 HTML → 用已授权的工具写入指定私有仓库 → 确认不需要逐次交互审批 → 构建通过 → 登录站点可读。验证后才能把发布步骤纳入原定时任务。上传必须发生在生成成功之后，不能固定到 08:55 就假定附件已就绪。生成失败时保留上一期、报告失败，不发布空文件。

`sandbox:/mnt/data/…` 是聊天内附件定位，不是供 GitHub Actions 匿名抓取的持久公开 URL。没有找到可直接导出原 ChatGPT 任务附件的已验证通道。[OpenAI 官方定时任务说明](https://learn.chatgpt.com/docs/automations)并不证明本账户已具备写入权限。

### 路线 C：独立生成与发布

若路线 B 不支持无人值守写入，可另建云端生成流程：日本时间 08:50 启动采集和生成，验证成功后立即提交 / 发布。GitHub Actions 的 UTC cron 对应 `50 23 * * *`（日本次日 08:50）；简报日期必须显式按 Asia/Tokyo 计算。建议设置生成超时、有限重试、每日日期幂等，约 09:10 检查当天文件是否出现，仅失败时通知。

Actions 定时任务可能延迟，不能保证 08:55 精确完成。若只是 08:58 重建站点，而生成物还留在 ChatGPT 内，网站不会更新。优先用“生成成功 → 写入 → push 触发发布”，定时检查只负责发现缺稿。[GitHub 调度限制](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule)。

迁移生成流程需要恢复完整简报提示词、新闻 / 天气来源和个人单词本访问，API 费用与密钥需另行确认；不是自动继承 ChatGPT 订阅或 Library 数据。OpenAI API 的 `response.completed` webhook 属于 API 项目事件，不能当成原 ChatGPT 聊天附件的导出接口。[OpenAI API Webhooks](https://developers.openai.com/api/docs/guides/webhooks)。

未创建额外定时任务，也未启用 API 调用或付费服务。

## 验证与限制

已执行：11 项导入 / 安全 URL / 来源 / 日期 / 失败保留测试；JavaScript 语法检查；本机 Edge 无头浏览器 320 / 390 / 1440 像素视口的布局、主题、字号、历史、刷新、返回、缺稿、图片、折叠答案、离线预览检查。截图在上一级交付目录。

尚未验证：原始 HTML 的实际版式与全部内容、真实新闻来源有效性、iOS Safari / Android 真机、云端构建、账户授权、Access 登录、每日无人值守发布、08:55 完成时间。测试数据和版式图片不能作为这些项目的通过证据。
