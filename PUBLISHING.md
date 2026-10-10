# 简报发布

UTF-8 HTML 放入 `incoming/YYYY-MM-DD.html`，关联本地图片放在 incoming 下相对路径。提交到 main 后，Publish daily briefing 工作流验证内容并部署 GitHub Pages。历史 HTML 保留。

仓库 Settings → Pages → Source 应选 GitHub Actions。网页和仓库均公开。

尚未连接原 ChatGPT 定时任务；本工作流不读取 ChatGPT 附件、不生成新闻。没有真实 HTML 时保留明确标注的版式预览。原定时任务只有在具备仓库写入工具且无人值守上传验证通过后，才算自动发布接通。
