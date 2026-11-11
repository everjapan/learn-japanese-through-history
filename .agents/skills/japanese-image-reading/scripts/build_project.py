#!/usr/bin/env python3
"""Build a reviewed article, Nanami audio and the existing static collection."""
import argparse
import asyncio
import hashlib
import html
import json
import re
import tempfile
from pathlib import Path
from urllib.parse import quote

from build_reading import RUBY, build, required_text

VOICE = 'ja-JP-NanamiNeural'
RATE = '-5%'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def url(path):
    return quote(path, safe='/.-')


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def sync_collection(root):
    """Refresh only the generated list, counts and README article table."""
    entries = json.loads((root / 'catalog.json').read_text(encoding='utf-8'))
    stems = [e['stem'] for e in entries]
    if len(set(stems)) != len(stems):
        raise ValueError('duplicate catalog stems')
    entries.sort(key=lambda e: int(e['stem'].split('-', 1)[0]))
    groups = {}
    blocks, rows = [], []
    ids = {'原始时代': 'primitive', '江户时代': 'edo', '幕末与近现代': 'modern'}
    for entry in entries:
        stem, title = entry['stem'], html.escape(entry['title'])
        group = entry['group']
        group_id = ids.get(group, 'group-' + digest(group.encode())[:8])
        if group not in groups:
            blocks.append(f'<h2 class="group-heading" id="{group_id}">{html.escape(group)}</h2>')
        groups[group] = groups.get(group, 0) + 1
        page = (root / 'readings' / (stem + '.html')).read_text(encoding='utf-8')
        title_match = re.search(r'<h1[^>]*>(.*?)</h1>', page, re.S)
        ruby_title = title_match[1] if title_match else title
        number = stem.split('-', 1)[0]
        seconds = round(entry['seconds'])
        duration = f'{seconds // 60}:{seconds % 60:02d}'
        pages = html.escape(entry.get('pages', ''))
        meta = duration + (f' · 第 {pages} 页' if pages else '')
        if entry.get('numbering_note'):
            meta += ' · ' + html.escape(entry['numbering_note'])
        if entry.get('translation'):
            meta += ' · 日中逐段对照'
        reading, audio, article = [url(f'{folder}/{stem}{suffix}') for folder, suffix in
                                   [('readings', '.html'), ('audio', '.mp3'), ('articles', '.md')]]
        label = '阅读日中对照' if entry.get('translation') else '阅读注音全文'
        links = f'<a href="{reading}">{label} →</a><a href="{article}">原文与批注</a>'
        if entry.get('translation'):
            links += f'<a href="{url("translations/" + stem + ".md")}" download>下载日中对照</a>'
        links += f'<a href="{article}" download>下载原文 Markdown</a><a href="{audio}" download>下载 MP3</a>'
        blocks.append(f'<section class="entry" data-stem="{html.escape(stem, quote=True)}">\n'
                      f'<div class="number">{number}</div><div class="entry-body">\n'
                      f'<h2 lang="ja"><a href="{reading}">{ruby_title}</a></h2><div class="meta">{meta}</div>\n'
                      f'<audio controls preload="none" src="{audio}" aria-label="{title}朗读"></audio>\n'
                      f'<div class="links">{links}</div>\n</div></section>')
        rows.append(f'| {number} | [{entry["title"]}]({article}) | [阅读]({reading}) | {entry.get("pages") or "—"} |')
    index = (root / 'index.html').read_text(encoding='utf-8')
    start = index.index('<h2 class="group-heading"')
    end = index.index('<footer', start)
    index = index[:start] + '\n'.join(blocks) + '\n' + index[end:]
    total = round(sum(e['seconds'] for e in entries))
    index = re.sub(r'<p class="intro">.*?</p>',
                   f'<p class="intro">{len(entries)} 篇日本史短文 · 假名注音 · Nanami 日语朗读 · 共 {total // 60} 分 {total % 60} 秒</p>', index)
    index = re.sub(r'读历史学日语：\d+ 篇', f'读历史学日语：{len(entries)} 篇', index)
    nav = ''.join(f'<a href="#{ids.get(g, "group-" + digest(g.encode())[:8])}">{html.escape(g)} · {count} 篇</a>'
                  for g, count in groups.items())
    nav += '<a href="https://github.com/everjapan/learn-japanese-through-history/tree/main/articles">Markdown 原文目录 ↗</a><a href="https://everjapan.com/">EverJapan 主页 ↗</a>'
    index = re.sub(r'(<nav class="site-nav"[^>]*>).*?(</nav>)', lambda m: m[1] + nav + m[2], index, flags=re.S)
    index = index.replace('“原文与批注”打开仓库中的 Markdown，可在登录后编辑并添加笔记。', '“原文与批注”打开无注音 Markdown，可下载后编辑并添加笔记。')
    (root / 'index.html').write_text(index, encoding='utf-8')
    readme_path = root / 'README.md'
    readme = readme_path.read_text(encoding='utf-8')
    heading = '## 文章目录'
    table = '| 编号（起始页码） | 原文与批注 | 注音阅读 | 已有来源页码 |\n| --- | --- | --- | --- |\n'
    before, after = readme.split(heading, 1)
    following = re.search(r'\n## ', after)
    remainder = after[following.start():] if following else ''
    readme = before + heading + '\n\n' + table + '\n'.join(rows) + '\n' + remainder
    for folder, desc in [('articles', '篇无注音 Markdown'), ('readings', '个注音阅读页'), ('audio', '个 MP3 朗读音频')]:
        readme = re.sub(rf'(\| `{folder}/` \| )\d+( {desc})', lambda m: m[1] + str(len(entries)) + m[2], readme)
    readme = re.sub(r'\d+ 篇日本史短文：[^。]+。',
                    f'{len(entries)} 篇日本史短文：' + '、'.join(f'{g} {n} 篇' for g, n in groups.items()) + '。', readme, count=1)
    readme_path.write_text(readme, encoding='utf-8')
    dump(root / 'catalog.json', entries)


async def generate_audio(root, article, force=False):
    import edge_tts
    from mutagen.mp3 import MP3
    plain = '\n\n'.join(x for x in [article['title'], article.get('subtitle', ''),
                                    *(p['ja'] for p in article['paragraphs'])] if x)
    speech = required_text(article.get('speech', plain), 'speech')
    fingerprint = digest(json.dumps([plain, speech, VOICE, RATE], ensure_ascii=False).encode())
    folder = root / 'audio'
    folder.mkdir(exist_ok=True)
    target = folder / (article['stem'] + '.mp3')
    cache_path = target.with_suffix('.json')
    cache = json.loads(cache_path.read_text()) if cache_path.exists() else {}
    if not force and target.exists() and cache.get('fingerprint') == fingerprint and cache.get('audio_sha256') == digest(target.read_bytes()):
        return MP3(target).info.length, 'reused'
    with tempfile.TemporaryDirectory(prefix='nanami-') as temp:
        candidate = Path(temp) / 'speech.mp3'
        await edge_tts.Communicate(speech, VOICE, rate=RATE).save(str(candidate))
        seconds = MP3(candidate).info.length
        if seconds <= 1:
            raise ValueError('generated audio is unexpectedly short')
        data = candidate.read_bytes()
        target.write_bytes(data)
    dump(cache_path, {'fingerprint': fingerprint, 'audio_sha256': digest(data),
                      'voice': VOICE, 'rate': RATE, 'seconds': round(seconds, 3)})
    return seconds, 'generated'


def run(article, root, force_audio=False):
    root = root.resolve()
    stem = required_text(article.get('stem'), 'stem')
    if not re.fullmatch(r'\d{3}-[^/\\\n]+', stem):
        raise ValueError('stem must be NNN-title, using the starting page number')
    required_text(article.get('group'), 'group')
    for key in ['furigana_title', *(['furigana_subtitle'] if article.get('subtitle') else [])]:
        required_text(article.get(key), key)
    for p in article.get('paragraphs', []):
        required_text(p.get('furigana'), 'paragraph.furigana')
    # Validate and prepare documents before contacting the speech service.
    data = dict(article)
    data.pop('audio', None)
    with tempfile.TemporaryDirectory(prefix='article-build-') as temp:
        staging = Path(temp)
        (staging / 'index.html').touch()
        draft = build(data, staging)
        for key, folder in [('original', 'articles'), ('translation', 'translations')]:
            target = root / folder / (stem + '.md')
            target.parent.mkdir(exist_ok=True)
            if not target.exists():
                target.write_text(Path(draft[key]).read_text(), encoding='utf-8')
        try:
            seconds, audio_status = asyncio.run(generate_audio(root, article, force_audio))
        except Exception as error:
            raise RuntimeError(f'原文与翻译已保留；Nanami 音频未完成：{error}') from error
        # Render again with an existing audio file and a collection backlink.
        output = staging / 'final'
        output.mkdir()
        (output / 'index.html').touch()
        # Keep the audio inside the staging root for the renderer's path checks.
        (output / 'audio').mkdir()
        (output / 'audio' / (stem + '.mp3')).write_bytes((root / 'audio' / (stem + '.mp3')).read_bytes())
        data['audio'] = 'audio/' + stem + '.mp3'
        rendered = build(data, output)
        for folder in ['readings', 'texts']:
            (root / folder).mkdir(exist_ok=True)
        (root / 'readings' / (stem + '.html')).write_text(Path(rendered['reading']).read_text(), encoding='utf-8')
    plain = article['title'] + '\n' + (article.get('subtitle', '') + '\n' if article.get('subtitle') else '')
    plain += '\n' + '\n\n'.join(p['ja'] for p in article['paragraphs']) + '\n'
    annotated = article['furigana_title'] + '\n' + (article.get('furigana_subtitle', '') + '\n' if article.get('subtitle') else '')
    annotated += '\n' + '\n\n'.join(p['furigana'] for p in article['paragraphs']) + '\n'
    (root / 'texts' / (stem + '-原文.txt')).write_text(plain, encoding='utf-8')
    (root / 'texts' / (stem + '-ふりがな.txt')).write_text(RUBY.sub(lambda m: m[1] + '（' + m[2] + '）', annotated), encoding='utf-8')
    dump(root / 'texts' / (stem + '.json'), data)
    entries = json.loads((root / 'catalog.json').read_text(encoding='utf-8'))
    previous = next((e for e in entries if e['stem'] == stem), {})
    entry = {**previous, **{k: article[k] for k in ['stem', 'title', 'subtitle', 'pages', 'group', 'numbering_note'] if k in article},
             'seconds': round(seconds, 3), 'translation': True}
    entries = [e for e in entries if e['stem'] != stem] + [entry]
    dump(root / 'catalog.json', entries)
    sync_collection(root)
    return {'stem': stem, 'audio': audio_status, 'seconds': round(seconds, 3), 'markdown': 'existing annotations preserved'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('article', type=Path)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--force-audio', action='store_true')
    args = parser.parse_args()
    try:
        result = run(json.loads(args.article.read_text(encoding='utf-8')), args.root, args.force_audio)
    except (ValueError, OSError, RuntimeError, ImportError) as error:
        parser.exit(1, str(error) + '\n')
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()
