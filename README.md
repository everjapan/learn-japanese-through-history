# 读历史学日语

37 篇日本史短文：原始时代 2 篇、江户时代 10 篇、幕末与近现代 25 篇。每篇提供无注音 Markdown 原文、可切换假名的阅读页，以及 Nanami 日语朗读。

《人類のルーツ》和《旧石器時代人の生活》附逐段中文翻译，默认显示，可用“隐藏中文翻译”按钮收起；假名可独立切换。[人类的起源](readings/022-%E4%BA%BA%E9%A1%9E%E3%81%AE%E3%83%AB%E3%83%BC%E3%83%84.html) · [旧石器时代人们的生活](readings/024-%E6%97%A7%E7%9F%B3%E5%99%A8%E6%99%82%E4%BB%A3%E4%BA%BA%E3%81%AE%E7%94%9F%E6%B4%BB.html) · [日中对照文本](translations/)。

## 阅读与批注

- [打开阅读合集](https://everjapan.com/learn-japanese-through-history/)：阅读、调速与连续播放；也可在下载仓库后，用浏览器打开此文件离线使用。
- [Markdown 原文目录](articles/)：每篇一个 `.md` 文件，保留标题、副标题与正文段落，不含 furigana。可直接在段落后添加批注，或在文末新增“批注”小节。
- 编辑 Markdown 不会覆盖现有注音页面或重新生成音频；正文校订如需同步到朗读，应另行更新对应文件。

## 网站发布

网站地址：<https://everjapan.com/learn-japanese-through-history/>。

组织主站 `everjapan.github.io` 已绑定 `everjapan.com`。本仓库已启用 GitHub Pages，继承主站域名并使用仓库名称作为子路径。无需为本仓库另设 CNAME 或 DNS。

Pages 设置：Settings → Pages → Deploy from a branch → `main` → `/ (root)`。`.nojekyll` 让 GitHub 直接发布现有静态文件；之后推送到 `main` 即可更新。

本仓库公开发布，GitHub Pages 从 `main` 分支根目录部署。仓库中的文章、音频及提交的批注均公开可见。

参考：[GitHub 官方自定义域名及套餐说明](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/about-custom-domains-and-github-pages)。

## 文件目录

| 目录 / 文件 | 内容 |
| --- | --- |
| `articles/` | 37 篇无注音 Markdown，供批注 |
| `translations/` | 日中对照 Markdown |
| `readings/` | 37 个注音阅读页 |
| `audio/` | 37 个 MP3 朗读音频 |
| `texts/` | 原文与注音纯文本 |
| `catalog.json` | 标题、副标题、页码及音频时长 |
| `index.html` | 阅读与连续播放合集入口 |

所有网页资源使用相对路径，适用于项目子路径与本地离线阅读。正文沿用图片中的用字，文章内容不含插图、图说或练习题。音频使用 `ja-JP-NanamiNeural`，生成语速为 `-5%`。

## 常用流程

- 图片导入：使用 `$japanese-image-reading`，按图片页码生成原文、逐段翻译、Nanami 日语朗读和可切换假名／中文的阅读页，并更新合集。
- 知识点解释：在 `translations/` 中列出待解释条目后，使用 `$japanese-reading-notes` 补全；保留已有笔记和加粗标记。

两个 skill 的项目版本分别位于 [.agents/skills/japanese-image-reading/](.agents/skills/japanese-image-reading/SKILL.md) 和 [.agents/skills/japanese-reading-notes/](.agents/skills/japanese-reading-notes/SKILL.md)。已核对的文章 JSON 存于 `texts/`，便于重新生成页面与朗读；重复执行保留已有 Markdown。

文件前缀统一为三位起始页码：《人類のルーツ》为 `022`，原 001–035 篇依次为 `198、200、…、266`。目录中的“已有来源页码”保留此前转录记录；编号校正不改写尚未重新核对的旧图来源。

## 文章目录

| 编号（起始页码） | 原文与批注 | 注音阅读 | 已有来源页码 |
| --- | --- | --- | --- |
| 022 | [人類のルーツ](articles/022-%E4%BA%BA%E9%A1%9E%E3%81%AE%E3%83%AB%E3%83%BC%E3%83%84.md) | [阅读](readings/022-%E4%BA%BA%E9%A1%9E%E3%81%AE%E3%83%AB%E3%83%BC%E3%83%84.html) | 22–23 |
| 024 | [旧石器時代人の生活](articles/024-%E6%97%A7%E7%9F%B3%E5%99%A8%E6%99%82%E4%BB%A3%E4%BA%BA%E3%81%AE%E7%94%9F%E6%B4%BB.md) | [阅读](readings/024-%E6%97%A7%E7%9F%B3%E5%99%A8%E6%99%82%E4%BB%A3%E4%BA%BA%E3%81%AE%E7%94%9F%E6%B4%BB.html) | 24–25 |
| 198 | [陸海交通の発達](articles/198-%E9%99%B8%E6%B5%B7%E4%BA%A4%E9%80%9A%E3%81%AE%E7%99%BA%E9%81%94.md) | [阅读](readings/198-%E9%99%B8%E6%B5%B7%E4%BA%A4%E9%80%9A%E3%81%AE%E7%99%BA%E9%81%94.html) | 190 |
| 200 | [元禄文化](articles/200-%E5%85%83%E7%A6%84%E6%96%87%E5%8C%96.md) | [阅读](readings/200-%E5%85%83%E7%A6%84%E6%96%87%E5%8C%96.html) | 192–193 |
| 202 | [享保の改革](articles/202-%E4%BA%AB%E4%BF%9D%E3%81%AE%E6%94%B9%E9%9D%A9.md) | [阅读](readings/202-%E4%BA%AB%E4%BF%9D%E3%81%AE%E6%94%B9%E9%9D%A9.html) | 194–195 |
| 204 | [一揆と打ちこわし](articles/204-%E4%B8%80%E6%8F%86%E3%81%A8%E6%89%93%E3%81%A1%E3%81%93%E3%82%8F%E3%81%97.md) | [阅读](readings/204-%E4%B8%80%E6%8F%86%E3%81%A8%E6%89%93%E3%81%A1%E3%81%93%E3%82%8F%E3%81%97.html) | — |
| 206 | [田沼政治](articles/206-%E7%94%B0%E6%B2%BC%E6%94%BF%E6%B2%BB.md) | [阅读](readings/206-%E7%94%B0%E6%B2%BC%E6%94%BF%E6%B2%BB.html) | 198–199 |
| 208 | [寛政の改革](articles/208-%E5%AF%9B%E6%94%BF%E3%81%AE%E6%94%B9%E9%9D%A9.md) | [阅读](readings/208-%E5%AF%9B%E6%94%BF%E3%81%AE%E6%94%B9%E9%9D%A9.html) | 200–201 |
| 210 | [列強諸国の接近](articles/210-%E5%88%97%E5%BC%B7%E8%AB%B8%E5%9B%BD%E3%81%AE%E6%8E%A5%E8%BF%91.md) | [阅读](readings/210-%E5%88%97%E5%BC%B7%E8%AB%B8%E5%9B%BD%E3%81%AE%E6%8E%A5%E8%BF%91.html) | 202 |
| 212 | [文化・文政時代](articles/212-%E6%96%87%E5%8C%96%E3%83%BB%E6%96%87%E6%94%BF%E6%99%82%E4%BB%A3.md) | [阅读](readings/212-%E6%96%87%E5%8C%96%E3%83%BB%E6%96%87%E6%94%BF%E6%99%82%E4%BB%A3.html) | 204–205 |
| 214 | [化政文化](articles/214-%E5%8C%96%E6%94%BF%E6%96%87%E5%8C%96.md) | [阅读](readings/214-%E5%8C%96%E6%94%BF%E6%96%87%E5%8C%96.html) | 206–207 |
| 216 | [天保の改革](articles/216-%E5%A4%A9%E4%BF%9D%E3%81%AE%E6%94%B9%E9%9D%A9.md) | [阅读](readings/216-%E5%A4%A9%E4%BF%9D%E3%81%AE%E6%94%B9%E9%9D%A9.html) | 208–209 |
| 218 | [開国と貿易の開始](articles/218-%E9%96%8B%E5%9B%BD%E3%81%A8%E8%B2%BF%E6%98%93%E3%81%AE%E9%96%8B%E5%A7%8B.md) | [阅读](readings/218-%E9%96%8B%E5%9B%BD%E3%81%A8%E8%B2%BF%E6%98%93%E3%81%AE%E9%96%8B%E5%A7%8B.html) | 212–213 |
| 220 | [尊王攘夷と公武合体](articles/220-%E5%B0%8A%E7%8E%8B%E6%94%98%E5%A4%B7%E3%81%A8%E5%85%AC%E6%AD%A6%E5%90%88%E4%BD%93.md) | [阅读](readings/220-%E5%B0%8A%E7%8E%8B%E6%94%98%E5%A4%B7%E3%81%A8%E5%85%AC%E6%AD%A6%E5%90%88%E4%BD%93.html) | 214–215 |
| 222 | [幕府の滅亡](articles/222-%E5%B9%95%E5%BA%9C%E3%81%AE%E6%BB%85%E4%BA%A1.md) | [阅读](readings/222-%E5%B9%95%E5%BA%9C%E3%81%AE%E6%BB%85%E4%BA%A1.html) | 216–217 |
| 224 | [戊辰戦争](articles/224-%E6%88%8A%E8%BE%B0%E6%88%A6%E4%BA%89.md) | [阅读](readings/224-%E6%88%8A%E8%BE%B0%E6%88%A6%E4%BA%89.html) | 218 |
| 226 | [新政府の中央集権政策](articles/226-%E6%96%B0%E6%94%BF%E5%BA%9C%E3%81%AE%E4%B8%AD%E5%A4%AE%E9%9B%86%E6%A8%A9%E6%94%BF%E7%AD%96.md) | [阅读](readings/226-%E6%96%B0%E6%94%BF%E5%BA%9C%E3%81%AE%E4%B8%AD%E5%A4%AE%E9%9B%86%E6%A8%A9%E6%94%BF%E7%AD%96.html) | 220 |
| 228 | [地租改正と殖産興業政策](articles/228-%E5%9C%B0%E7%A7%9F%E6%94%B9%E6%AD%A3%E3%81%A8%E6%AE%96%E7%94%A3%E8%88%88%E6%A5%AD%E6%94%BF%E7%AD%96.md) | [阅读](readings/228-%E5%9C%B0%E7%A7%9F%E6%94%B9%E6%AD%A3%E3%81%A8%E6%AE%96%E7%94%A3%E8%88%88%E6%A5%AD%E6%94%BF%E7%AD%96.html) | 222–223 |
| 230 | [自由民権運動の展開](articles/230-%E8%87%AA%E7%94%B1%E6%B0%91%E6%A8%A9%E9%81%8B%E5%8B%95%E3%81%AE%E5%B1%95%E9%96%8B.md) | [阅读](readings/230-%E8%87%AA%E7%94%B1%E6%B0%91%E6%A8%A9%E9%81%8B%E5%8B%95%E3%81%AE%E5%B1%95%E9%96%8B.html) | 224–225 |
| 232 | [民権運動の崩壊と再生](articles/232-%E6%B0%91%E6%A8%A9%E9%81%8B%E5%8B%95%E3%81%AE%E5%B4%A9%E5%A3%8A%E3%81%A8%E5%86%8D%E7%94%9F.md) | [阅读](readings/232-%E6%B0%91%E6%A8%A9%E9%81%8B%E5%8B%95%E3%81%AE%E5%B4%A9%E5%A3%8A%E3%81%A8%E5%86%8D%E7%94%9F.html) | 226 |
| 234 | [憲法制定と議会開設](articles/234-%E6%86%B2%E6%B3%95%E5%88%B6%E5%AE%9A%E3%81%A8%E8%AD%B0%E4%BC%9A%E9%96%8B%E8%A8%AD.md) | [阅读](readings/234-%E6%86%B2%E6%B3%95%E5%88%B6%E5%AE%9A%E3%81%A8%E8%AD%B0%E4%BC%9A%E9%96%8B%E8%A8%AD.html) | 228–229 |
| 236 | [条約改正交渉](articles/236-%E6%9D%A1%E7%B4%84%E6%94%B9%E6%AD%A3%E4%BA%A4%E6%B8%89.md) | [阅读](readings/236-%E6%9D%A1%E7%B4%84%E6%94%B9%E6%AD%A3%E4%BA%A4%E6%B8%89.html) | 230 |
| 238 | [日清戦争](articles/238-%E6%97%A5%E6%B8%85%E6%88%A6%E4%BA%89.md) | [阅读](readings/238-%E6%97%A5%E6%B8%85%E6%88%A6%E4%BA%89.html) | 232 |
| 240 | [日露戦争](articles/240-%E6%97%A5%E9%9C%B2%E6%88%A6%E4%BA%89.md) | [阅读](readings/240-%E6%97%A5%E9%9C%B2%E6%88%A6%E4%BA%89.html) | 234 |
| 242 | [日韓併合](articles/242-%E6%97%A5%E9%9F%93%E4%BD%B5%E5%90%88.md) | [阅读](readings/242-%E6%97%A5%E9%9F%93%E4%BD%B5%E5%90%88.html) | 236–237 |
| 244 | [産業革命](articles/244-%E7%94%A3%E6%A5%AD%E9%9D%A9%E5%91%BD.md) | [阅读](readings/244-%E7%94%A3%E6%A5%AD%E9%9D%A9%E5%91%BD.html) | 238–239 |
| 246 | [大正政変](articles/246-%E5%A4%A7%E6%AD%A3%E6%94%BF%E5%A4%89.md) | [阅读](readings/246-%E5%A4%A7%E6%AD%A3%E6%94%BF%E5%A4%89.html) | 240–241 |
| 248 | [第一次世界大戦](articles/248-%E7%AC%AC%E4%B8%80%E6%AC%A1%E4%B8%96%E7%95%8C%E5%A4%A7%E6%88%A6.md) | [阅读](readings/248-%E7%AC%AC%E4%B8%80%E6%AC%A1%E4%B8%96%E7%95%8C%E5%A4%A7%E6%88%A6.html) | 242–243 |
| 250 | [護憲三派内閣と普通選挙](articles/250-%E8%AD%B7%E6%86%B2%E4%B8%89%E6%B4%BE%E5%86%85%E9%96%A3%E3%81%A8%E6%99%AE%E9%80%9A%E9%81%B8%E6%8C%99.md) | [阅读](readings/250-%E8%AD%B7%E6%86%B2%E4%B8%89%E6%B4%BE%E5%86%85%E9%96%A3%E3%81%A8%E6%99%AE%E9%80%9A%E9%81%B8%E6%8C%99.html) | 244–245 |
| 252 | [恐慌の時代](articles/252-%E6%81%90%E6%85%8C%E3%81%AE%E6%99%82%E4%BB%A3.md) | [阅读](readings/252-%E6%81%90%E6%85%8C%E3%81%AE%E6%99%82%E4%BB%A3.html) | 246–247 |
| 254 | [軍部の台頭](articles/254-%E8%BB%8D%E9%83%A8%E3%81%AE%E5%8F%B0%E9%A0%AD.md) | [阅读](readings/254-%E8%BB%8D%E9%83%A8%E3%81%AE%E5%8F%B0%E9%A0%AD.html) | 248–249 |
| 256 | [日中戦争](articles/256-%E6%97%A5%E4%B8%AD%E6%88%A6%E4%BA%89.md) | [阅读](readings/256-%E6%97%A5%E4%B8%AD%E6%88%A6%E4%BA%89.html) | 250–251 |
| 258 | [太平洋戦争](articles/258-%E5%A4%AA%E5%B9%B3%E6%B4%8B%E6%88%A6%E4%BA%89.md) | [阅读](readings/258-%E5%A4%AA%E5%B9%B3%E6%B4%8B%E6%88%A6%E4%BA%89.html) | 252 |
| 260 | [日本の敗戦](articles/260-%E6%97%A5%E6%9C%AC%E3%81%AE%E6%95%97%E6%88%A6.md) | [阅读](readings/260-%E6%97%A5%E6%9C%AC%E3%81%AE%E6%95%97%E6%88%A6.html) | 254–255 |
| 262 | [日本の民主化](articles/262-%E6%97%A5%E6%9C%AC%E3%81%AE%E6%B0%91%E4%B8%BB%E5%8C%96.md) | [阅读](readings/262-%E6%97%A5%E6%9C%AC%E3%81%AE%E6%B0%91%E4%B8%BB%E5%8C%96.html) | 256–257 |
| 264 | [日本の独立](articles/264-%E6%97%A5%E6%9C%AC%E3%81%AE%E7%8B%AC%E7%AB%8B.md) | [阅读](readings/264-%E6%97%A5%E6%9C%AC%E3%81%AE%E7%8B%AC%E7%AB%8B.html) | 258–259 |
| 266 | [日本の経済復興](articles/266-%E6%97%A5%E6%9C%AC%E3%81%AE%E7%B5%8C%E6%B8%88%E5%BE%A9%E8%88%88.md) | [阅读](readings/266-%E6%97%A5%E6%9C%AC%E3%81%AE%E7%B5%8C%E6%B8%88%E5%BE%A9%E8%88%88.html) | 260–261 |
