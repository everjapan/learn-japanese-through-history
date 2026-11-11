# 对接当前阅读项目

定位当前实际仓库：本地目录 `learn-japanese-through-japanese`，Git 远程仓库名 `learn-japanese-through-history`。不要依赖某台电脑的绝对路径。

- `articles/`：无注音日文 Markdown；`translations/`：逐段日中对照及个人知识点；`readings/`：可独立切换假名和中文的 HTML；`audio/`：Nanami MP3 及内容缓存；`texts/`：纯文本、注音文本及可复现的文章 JSON。
- 五个目录统一 `<三位起始页码>-<日文标题>`。2026-11-11 用户要求一次迁移：旧 001–035 分别改为 198、200、…、266；旧 036《人類のルーツ》改为 022。后续新图片以实际页码为准，不能永久沿用旧序号换算。
- 用户指定的编号与旧来源页码不一致时保留 `pages`，可另用 `numbering_note` 说明；不能伪称已核对未提供的图片。
- `texts/<stem>.json` 使用 article-format 的数据格式，补充 `group`（例如原始时代、江户时代、幕末与近现代）。`speech` 可选，专用于已核对的日文朗读读音文本。
- 本 skill 内的 `scripts/build_project.py` 复用 `build_reading.py` 排版，默认生成音频并同步合集。依赖在项目外安装：`python3 -m venv <temp-env>`，再用该环境的 pip 安装 `edge-tts mutagen`。脚本不自动安装依赖。
- 重跑时先读取并保留既有 Markdown 批注。网页更新使用核对过的 JSON；不把个人知识点自动放进网页或音频。
- 所有本地文件链接使用相对路径，适配离线访问及 `https://everjapan.com/learn-japanese-through-history/`。不修改站点域名、CNAME 或发布设置。
- 原始照片、虚拟环境、临时录音及日志不放进仓库。技能不授予提交、推送或发布权限。
