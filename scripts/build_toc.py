#!/usr/bin/env python3
"""Render the photographed book contents, linking only completed readings."""
import argparse
import html
import json
import re
from pathlib import Path
from urllib.parse import quote

START = '<!-- book-toc:start -->'
END = '<!-- book-toc:end -->'


def sync_toc(root):
    root = Path(root)
    book = json.loads((root / 'book-toc.json').read_text(encoding='utf-8'))
    catalog = json.loads((root / 'catalog.json').read_text(encoding='utf-8'))
    published = {}
    for article in catalog:
        title = article['title']
        if title in published:
            raise ValueError(f'Ambiguous reading title: {title}')
        if not (root / 'readings' / (article['stem'] + '.html')).is_file():
            raise ValueError(f'Missing reading: {article["stem"]}')
        published[title] = article
    articles = [e for c in book['chapters'] for e in c['entries'] if e['kind'] == 'article']
    titles = [e['title'] for e in articles]
    if len(titles) != len(set(titles)):
        raise ValueError('Duplicate book article titles')
    missing = set(published) - set(titles)
    if missing:
        raise ValueError(f'Readings absent from book contents: {sorted(missing)}')
    available = len(published)
    count = len(articles)
    esc = html.escape
    markdown = ['# 全书目录', '',
                f'按原书目录整理，共 5 章、{count} 篇正文、5 篇专栏；已上线 {available} 篇正文。', '',
                '页码来自目录照片，与既有文件编号、原有来源页码分别记录。已有文章按标题关联；未提供正文的条目仅列目录。', '',
                '「はじめに」和「索引」的页码未见于照片，以「—」表示。', '']

    def row(entry, kind=None):
        kind = kind or entry.get('kind', 'appendix')
        title = entry['title']
        page = entry['page']
        subtitle = entry.get('subtitle', '')
        article = published.get(title) if kind == 'article' else None
        reading = quote('readings/' + article['stem'] + '.html', safe='/.-') if article else None
        search = f'{title} {subtitle} {page or ""} {page:03d}' if page is not None else f'{title} {subtitle}'
        number = f'{page:03d}' if page is not None else '—'
        number_attr = '' if page is not None else ' title="照片未标页码"'
        content = f'<span class="toc-title" lang="ja">{esc(title)}</span>'
        if subtitle:
            content += f'<span class="toc-subtitle" lang="ja">{esc(subtitle)}</span>'
        content = (f'<a class="toc-copy" href="{reading}">{content}</a>' if reading
                   else f'<div class="toc-copy">{content}</div>')
        label = '阅读 →' if article else '专栏 · 待更新' if kind == 'column' else '待更新'
        markdown.append(f'| {number} | ' + (f'[{title}]({reading})' if reading else title)
                        + f' | {subtitle or "—"} | ' + ('已上线' if article else '专栏 · 待更新' if kind == 'column' else '待更新') + ' |')
        return (f'<li class="toc-row{ " is-ready" if article else ""}" data-kind="{kind}" '
                f'data-ready="{str(bool(article)).lower()}" data-search="{esc(search, quote=True)}">'
                f'<span class="toc-page"{number_attr}>{number}</span>{content}'
                f'<span class="toc-state">{label}</span></li>')

    table_header = ['| 原书起始页 | 标题 | 副标题 | 阅读 |', '| --- | --- | --- | --- |']
    blocks = [START, '<section class="book-toc" aria-labelledby="toc-heading">',
              '<div class="toc-heading"><h2 id="toc-heading">全书目录</h2>'
              '<a href="book-toc.md" download>下载目录</a></div>',
              '<p class="notice">按原书章节排列，左侧为原书起始页码。绿色标题可进入阅读，其余篇目陆续更新。</p>',
              '<div class="toc-tools" hidden><label class="toc-search-label" for="toc-search">搜索目录'
              '<input id="toc-search" type="search" placeholder="标题、关键词或页码" autocomplete="off"></label>'
              '<label for="toc-filter">显示<select id="toc-filter"><option value="all">全部目录</option>'
              '<option value="ready">已上线正文</option><option value="pending">待更新正文</option></select></label>'
              '<button id="toc-expand" type="button">展开全部</button></div>',
              f'<p id="toc-result" class="notice" role="status" aria-live="polite">全书 {count} 篇正文 · 已上线 {available} 篇</p>']
    for chapter in book['chapters']:
        ready = sum(e['title'] in published for e in chapter['entries'] if e['kind'] == 'article')
        size = sum(e['kind'] == 'article' for e in chapter['entries'])
        markdown += ['', f'## 第 {chapter["number"]} 章　{chapter["title"]}（p. {chapter["page"]}）',
                     '', chapter['subtitle'], '', *table_header]
        blocks += [f'<details class="toc-chapter" id="{chapter["id"]}"' + (' open' if chapter['number'] == 1 else '') + '>',
                   '<summary><span class="chapter-copy">'
                   f'<span class="chapter-title"><span class="chapter-number">第 {chapter["number"]} 章</span> '
                   f'<span lang="ja">{esc(chapter["title"])}</span></span>'
                   f'<span class="chapter-subtitle" lang="ja">{esc(chapter["subtitle"])}</span></span>'
                   f'<span class="chapter-count">{size} 篇 · 已上线 {ready}</span></summary>', '<ol class="toc-list">']
        blocks.extend(row(e) for e in chapter['entries'])
        blocks += ['</ol></details>']
    markdown += ['', '## 序言与附录', '', *table_header]
    blocks += ['<details class="toc-chapter" id="book-appendix"><summary><span class="chapter-copy">'
               '<span class="chapter-title">序言与附录</span><span class="chapter-subtitle">序言、历史资料、年表与索引</span>'
               '</span><span class="chapter-count">10 项</span></summary><ol class="toc-list">']
    blocks.extend(row(e, 'appendix') for e in book['frontmatter'] + book['appendix'])
    blocks += ['</ol></details>', '<p id="toc-empty" class="notice" hidden>没有找到匹配的目录项，请尝试其他关键词。</p>', '</section>', END]
    index_path = root / 'index.html'
    index = index_path.read_text(encoding='utf-8')
    rendered = '\n'.join(blocks)
    if START in index:
        index = re.sub(re.escape(START) + '.*?' + re.escape(END), lambda _: rendered, index, flags=re.S)
    else:
        index = index.replace('<div class="controls">', rendered + '\n<h2 id="listening" class="listening-heading">已上线阅读与朗读</h2>\n<div class="controls">', 1)
    intro = f'全书 5 章 · {count} 篇正文 · 已上线 {available} 篇 · 假名注音与日语朗读'
    index = re.sub(r'<p class="intro">.*?</p>', lambda _: f'<p class="intro">{intro}</p>', index)
    index = re.sub(r'<meta name="description"[^>]*>',
                   lambda _: f'<meta name="description" content="读历史学日语：按原书 5 章整理 {count} 篇正文目录，已上线 {available} 篇假名注音阅读与日语朗读。">', index)
    nav = ''.join(f'<a href="#{c["id"]}">{esc(c["title"])}</a>' for c in book['chapters'])
    nav += '<a href="#listening">阅读与朗读</a><a href="https://everjapan.com/">EverJapan 主页 ↗</a>'
    index = re.sub(r'(<nav class="site-nav"[^>]*>).*?(</nav>)', lambda m: m[1] + nav + m[2], index, flags=re.S)
    if 'assets/toc.css' not in index:
        index = index.replace('</head>', '<link rel="stylesheet" href="assets/toc.css"></head>', 1)
        index = index.replace('</body>', '<script src="assets/toc.js"></script></body>', 1)
    index_path.write_text(index, encoding='utf-8')
    (root / 'book-toc.md').write_text('\n'.join(markdown) + '\n', encoding='utf-8')
    return {'chapters': len(book['chapters']), 'articles': count, 'published': available}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    print(json.dumps(sync_toc(parser.parse_args().root), ensure_ascii=False))
