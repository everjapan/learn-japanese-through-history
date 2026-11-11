#!/usr/bin/env python3
"""Render a reviewed bilingual article; never overwrite existing annotations."""
import argparse
import html
import json
import re
from pathlib import Path
from urllib.parse import quote

RUBY = re.compile(r'\[([^\[\]|]+)\|([^\[\]|]+)\]')


def required_text(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'{label} must be nonempty text')
    return value


def render_ruby(plain, annotated, label):
    if annotated is None:
        return html.escape(plain)
    required_text(annotated, label)
    if RUBY.sub(lambda m: m[1], annotated) != plain:
        raise ValueError(f'{label}: removing furigana changes the Japanese text')
    parts, cursor = [], 0
    for match in RUBY.finditer(annotated):
        parts.append(html.escape(annotated[cursor:match.start()]))
        parts.append(f'<ruby>{html.escape(match[1])}<rp>（</rp><rt>{html.escape(match[2])}</rt><rp>）</rp></ruby>')
        cursor = match.end()
    parts.append(html.escape(annotated[cursor:]))
    return ''.join(parts)


STYLE = '''
:root{color-scheme:light;--ink:#243733;--green:#326f61;--paper:#fcfaf4}
*{box-sizing:border-box}body{margin:0;background:#eeeee5;color:var(--ink);font-family:"Hiragino Mincho ProN","Yu Mincho",serif}
main{max-width:960px;margin:40px auto;padding:40px 56px;background:var(--paper);border-top:5px solid var(--green)}
nav,.controls,footer{font-family:system-ui,"PingFang SC",sans-serif}nav{display:flex;flex-wrap:wrap;gap:20px;font-size:14px}
a{color:var(--green);text-underline-offset:4px}h1{font-size:34px;line-height:2.1;margin:24px 0 0}rt{font-size:.5em;color:#4e7267;font-weight:400}
.subtitle{font-size:18px;line-height:2.6;margin:12px 0}.zh{font:17px/1.95 system-ui,"PingFang SC","Microsoft YaHei",sans-serif;color:#52665e}
.title-zh{font-size:20px;margin:0 0 14px}.subtitle-zh{font-size:15px;margin:0 0 22px}
.controls{display:flex;flex-wrap:wrap;align-items:center;gap:14px;background:#f1f4ed;border:1px solid #d5e0d5;padding:16px;border-radius:10px;margin:24px 0 30px;font-size:14px}
button,select{font:inherit;background:white;border:1px solid #bacdbd;border-radius:6px;padding:7px 10px;color:var(--ink);cursor:pointer}
audio{width:100%;height:42px}article{font-size:21px;line-height:2.8;line-break:strict;overflow-wrap:break-word}
.paragraph-pair{padding-bottom:26px;margin-bottom:28px;border-bottom:1px solid #e1e4d9}.ja{margin:0;text-indent:1em}
.paragraph-pair>.zh{background:#f1f4ed;border-left:3px solid #b5c8b9;padding:14px 18px;margin:12px 0 0}
.hide-ruby rt{visibility:hidden}[hidden]{display:none!important}footer{font-size:12px;line-height:1.8;color:#69756a;margin-top:24px}
button:focus-visible,a:focus-visible,select:focus-visible{outline:2px solid var(--green);outline-offset:4px}
@media(max-width:650px){main{margin:0;padding:26px 20px}h1{font-size:29px}article{font-size:19px}.subtitle{font-size:16px}.paragraph-pair>.zh{font-size:16px;padding:12px 15px}}
@media print{body{background:white}main{margin:0;border:0;padding:0;max-width:none}.controls,nav{display:none}article{font-size:13pt}.paragraph-pair>.zh{background:transparent;font-size:11pt}}
'''

SCRIPT = '''
const translationToggle=document.getElementById('translation-toggle');
translationToggle.addEventListener('click',()=>{
  const visible=translationToggle.getAttribute('aria-pressed')==='true';
  document.querySelectorAll('.zh').forEach(p=>p.hidden=visible);
  translationToggle.setAttribute('aria-pressed',String(!visible));
  translationToggle.textContent=visible?'显示中文翻译':'隐藏中文翻译';
});
const rubyToggle=document.getElementById('ruby-toggle');
if(rubyToggle)rubyToggle.addEventListener('click',()=>{
  const hidden=document.body.classList.toggle('hide-ruby');
  rubyToggle.setAttribute('aria-pressed',String(!hidden));
  rubyToggle.textContent=hidden?'显示假名':'隐藏假名';
});
const player=document.getElementById('audio');
if(player)document.getElementById('speed').addEventListener('change',e=>player.playbackRate=Number(e.target.value));
'''


def build(article, root):
    if not isinstance(article, dict):
        raise ValueError('article must be a JSON object')
    stem = required_text(article.get('stem'), 'stem')
    if stem in ('.', '..') or '/' in stem or '\\' in stem or '\n' in stem:
        raise ValueError('stem must be a filename without directories')
    title = required_text(article.get('title'), 'title')
    title_zh = required_text(article.get('title_zh'), 'title_zh')
    title_html = render_ruby(title, article.get('furigana_title'), 'furigana_title')
    subtitle = article.get('subtitle', '')
    subtitle_zh = article.get('subtitle_zh', '')
    if not isinstance(subtitle, str) or not isinstance(subtitle_zh, str):
        raise ValueError('subtitle fields must be text')
    if bool(subtitle.strip()) != bool(subtitle_zh.strip()):
        raise ValueError('provide both subtitle and subtitle_zh, or omit both')
    subtitle_html = render_ruby(subtitle, article.get('furigana_subtitle'), 'furigana_subtitle')
    paragraphs = article.get('paragraphs')
    if not isinstance(paragraphs, list) or not paragraphs:
        raise ValueError('paragraphs must be a nonempty list')
    pairs = []
    for index, p in enumerate(paragraphs, 1):
        if not isinstance(p, dict):
            raise ValueError(f'paragraph {index} must be an object')
        ja = required_text(p.get('ja'), f'paragraph {index}.ja')
        zh = required_text(p.get('zh'), f'paragraph {index}.zh')
        ja_html = render_ruby(ja, p.get('furigana'), f'paragraph {index}.furigana')
        pairs.append(f'<section class="paragraph-pair" id="paragraph-{index}"><p class="ja" lang="ja">{ja_html}</p><p class="zh" lang="zh-CN">{html.escape(zh)}</p></section>')

    root = root.resolve()
    targets = {
        'original': root / 'articles' / (stem + '.md'),
        'translation': root / 'translations' / (stem + '.md'),
        'reading': root / 'readings' / (stem + '.html'),
    }
    for target in targets.values():
        if not target.resolve().is_relative_to(root):
            raise ValueError('output directory resolves outside the selected root')
        if target.exists():
            raise FileExistsError(f'Preserving existing file: {target}; edit it in place or choose a temporary output root')

    audio_html = ''
    if article.get('audio'):
        audio = Path(required_text(article['audio'], 'audio'))
        resolved = (root / audio).resolve()
        if audio.is_absolute() or not resolved.is_relative_to(root) or not resolved.is_file():
            raise ValueError('audio must name an existing file relative to the output root')
        audio_url = quote('../' + audio.as_posix(), safe='/.-')
        audio_html = f'<audio id="audio" controls preload="metadata" src="{audio_url}"></audio><label>播放速度 <select id="speed"><option value="0.8">0.8×</option><option value="1" selected>1×</option><option value="1.15">1.15×</option></select></label><a href="{audio_url}" download>下载 MP3</a>'

    md_title = f'# {title} / {title_zh}\n'
    def quote_translation(text):
        return '\n'.join('> ' + line if line else '>' for line in text.splitlines())

    subtitle_md = f'\n{subtitle}\n\n{quote_translation(subtitle_zh)}\n' if subtitle else ''
    translation = md_title + subtitle_md
    for p in paragraphs:
        translation += f'\n---\n\n{p["ja"]}\n\n{quote_translation(p["zh"])}\n'
    original = f'# {title}\n\n' + (subtitle + '\n\n' if subtitle else '') + '\n\n'.join(p['ja'] for p in paragraphs) + '\n'
    subtitle_block = f'<div class="subtitle">{subtitle_html}</div><p class="zh subtitle-zh" lang="zh-CN">{html.escape(subtitle_zh)}</p>' if subtitle else ''
    ruby_button = '<button id="ruby-toggle" type="button" aria-pressed="true">隐藏假名</button>' if any('<ruby>' in t for t in [title_html, subtitle_html, *pairs]) else ''
    source = Path(str(article.get('source', '')).replace('\\', '/')).name
    pages = str(article.get('pages', ''))
    source_note = ' · '.join(x for x in [source, f'第 {pages} 页' if pages else ''] if x)
    translation_url = quote('../translations/' + stem + '.md', safe='/.-')
    nav = '<a href="../index.html">← 返回合集</a>' if (root / 'index.html').is_file() else ''
    original_url = quote('../articles/' + stem + '.md', safe='/.-')
    nav += f'<a href="{original_url}">原文与批注</a>'
    nav += f'<a href="{translation_url}" download>下载日中对照 Markdown</a>'
    page = f'''<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}｜日中对照</title><style>{STYLE}</style></head><body><main>
<nav lang="zh-CN">{nav}</nav><h1>{title_html}</h1><p class="zh title-zh" lang="zh-CN">{html.escape(title_zh)}</p>
{subtitle_block}
<div class="controls" lang="zh-CN"><button id="translation-toggle" type="button" aria-pressed="true">隐藏中文翻译</button>{ruby_button}{audio_html}</div>
<article aria-label="日中对照正文">{''.join(pairs)}</article><footer lang="zh-CN">{html.escape(source_note)}</footer>
</main><script>{SCRIPT}</script></body></html>
'''
    content = {'original': original, 'translation': translation, 'reading': page}
    for key, target in targets.items():
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open('x', encoding='utf-8') as f:
            f.write(content[key])
    return {key: str(value) for key, value in targets.items()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('article', type=Path)
    parser.add_argument('--root', type=Path, required=True)
    args = parser.parse_args()
    try:
        data = json.loads(args.article.read_text(encoding='utf-8'))
        result = build(data, args.root)
    except (ValueError, OSError) as error:
        parser.exit(1, f'{error}\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
