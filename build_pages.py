#!/usr/bin/env python3
# Rebuild javvincompany.github.io as separate pages per menu category,
# English and Chinese fully separated. Canonical book titles:
#   EN: The Power of Desire: A Brief History of Scientific & Technological Innovation
#   ZH: 《欲望的力量：人类科技创新简史》
import re, pathlib

ROOT = pathlib.Path('/home/hatch/workspace/website')
en_src = (ROOT / 'index.html').read_text()
zh_src = (ROOT / 'zh' / 'index.html').read_text()

STYLE = re.search(r'<style>.*?</style>', en_src, re.S).group(0)

def section(src, sid):
    m = re.search(r'<section class="block" id="%s">.*?</section>' % sid, src, re.S)
    return m.group(0)

def hero(src):
    return re.search(r'<div class="hero">.*?(?=<section class="block")', src, re.S).group(0).rstrip() + '\n'

def footer(src):
    return re.search(r'<footer>.*?</footer>', src, re.S).group(0)

# ---------- canonical title fixes: EN ----------
CANON = 'The Power of Desire: A Brief History of Scientific &amp; Technological Innovation'
SHORT = 'A Brief History of Scientific &amp; Technological Innovation'

def fix_en(html):
    # variants -> canonical full title
    html = html.replace('The Power of Desire: A Brief History of Human Technological Innovation', CANON)
    html = html.replace('The Power of Desire: A Brief History of Scientific and Technological Innovation', CANON)
    # H1 sub-line variant
    html = html.replace('A Brief History of Human Technological Innovation', SHORT)
    # description italic: give it the full title
    html = html.replace('<em>A Brief History of Scientific and Technological Innovation</em>',
                        '<em>%s</em>' % CANON)
    # Sun foreword heading -> full title (names the second edition)
    html = html.replace('<em>A Brief History of Human Scientific and Technological Innovation</em>',
                        '<em>%s</em>' % CANON)
    # Sun: first-edition reference -> short canonical
    html = html.replace('first edition of A Brief History of Human Scientific and Technological Innovation,',
                        'first edition of %s,' % SHORT)
    # Sun: crystallization sentence -> full title (names this work)
    html = html.replace('A Brief History of Human Scientific and Technological Innovation is the crystallization',
                        '%s is the crystallization' % CANON)
    return html

def fix_zh(html):
    # description book reference -> full title
    html = html.replace('《人类科技创新简史》以重大科技首创数据库为基础',
                        '《欲望的力量：人类科技创新简史》以重大科技首创数据库为基础')
    # Sun foreword heading -> full title
    html = html.replace('人类为什么要创新——《人类科技创新简史》第二版推荐序',
                        '人类为什么要创新——《欲望的力量：人类科技创新简史》第二版推荐序')
    # Sun crystallization sentence -> full title
    html = html.replace('《人类科技创新简史》正是这些长期积累',
                        '《欲望的力量：人类科技创新简史》正是这些长期积累')
    # remove the English title line from the Chinese hero (language purity)
    html = re.sub(r'\n<p class="en-title">.*?</p>', '', html)
    return html

EN = fix_en(en_src)
ZH = fix_zh(zh_src)

# ---------- shared chrome ----------
def header(lang, page, fname):
    if lang == 'en':
        nav = [('books.html', 'Books'), ('posters.html', 'Posters'),
               ('articles.html', 'Articles'), ('about.html', 'About')]
        logo, asset = './', 'assets/javvin-wordmark.svg'
        self_link = './' if page == 'home' else fname
        other = '/zh/' if page == 'home' else '/zh/' + fname
        lang_html = ('<div class="lang-switch"><a class="active" href="%s">EN</a>'
                     '<a href="%s">中文</a></div>' % (self_link, other))
    else:
        nav = [('books.html', '书籍'), ('posters.html', '图谱'),
               ('articles.html', '文章'), ('about.html', '关于')]
        logo, asset = './', '../assets/javvin-wordmark.svg'
        self_link = './' if page == 'home' else fname
        other = '/' if page == 'home' else '/' + fname
        lang_html = ('<div class="lang-switch"><a href="%s">EN</a>'
                     '<a class="active" href="%s">中文</a></div>' % (other, self_link))
    links = '\n'.join('<a href="%s"><span>%s</span></a>' % (h, t) for h, t in nav)
    return ('<header>\n<a aria-label="Javvin Company" class="logo" href="%s">'
            '<img alt="Javvin Company" src="%s"/></a>\n<nav>\n%s\n%s\n</nav>\n</header>'
            % (logo, asset, links, lang_html))

BASE = 'https://javvincompany.github.io/'
def head(lang, page, fname, title, desc, og_title):
    if lang == 'en':
        canon = BASE + ('' if page == 'home' else fname)
        alt_zh = BASE + 'zh/' + ('' if page == 'home' else fname)
        alt_en = canon
    else:
        canon = BASE + 'zh/' + ('' if page == 'home' else fname)
        alt_en = BASE + ('' if page == 'home' else fname)
        alt_zh = canon
    return f'''<head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<title>{title}</title>
<meta content="{desc}" name="description"/>
<meta content="UjqM5b327ctUoN0HMQ91Dvwp_7B0VCA48ALKU27OKyU" name="google-site-verification"/>
<link href="{canon}" rel="canonical"/><link href="{alt_en}" hreflang="x-default" rel="alternate"/><link href="{alt_zh}" hreflang="zh" rel="alternate"/><link href="{alt_en}" hreflang="en" rel="alternate"/>
<meta content="website" property="og:type"/>
<meta content="Javvin Company" property="og:site_name"/>
<meta content="{og_title}" property="og:title"/>
<meta content="{desc}" property="og:description"/>
<meta content="{canon}" property="og:url"/>
<meta content="https://javvincompany.github.io/assets/covers/cover-en-front.jpg" property="og:image"/>
{STYLE}
</head>'''

EXTRA_CSS = '''
<style>
  .cards { max-width: 860px; margin: 0 auto; padding: 3.5rem 2rem 4rem;
    display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 1.25rem; }
  .card { border: 1px solid #e2dacc; border-radius: 8px; background: #fffdf8;
    padding: 1.75rem 1.25rem; text-align: center; text-decoration: none; color: var(--ink); }
  .card:hover { border-color: var(--gold); }
  .card h3 { font-size: 1.15rem; letter-spacing: 0.2em; margin-bottom: 0.5rem; }
  .card p { color: var(--muted); font-size: 0.9rem; line-height: 1.6; }
  .hero-btn { display: inline-block; margin-top: 1.5rem; background: var(--gold); color: var(--navy);
    padding: 0.6rem 1.6rem; border-radius: 999px; text-decoration: none; font-size: 0.95rem;
    font-family: -apple-system, "PingFang SC", "Microsoft YaHei", sans-serif; }
  .hero-btn:hover { opacity: 0.88; }
</style>'''

def page(lang, page_name, fname, title, desc, og_title, body_html):
    h = head(lang, page_name, fname, title, desc, og_title).replace(
        '</style>', '</style>' + EXTRA_CSS, 1)
    body_attr = ' class="en"' if lang == 'en' else ''
    return ('<!DOCTYPE html>\n<html lang="%s">\n%s\n<body%s>\n%s\n%s\n</body>\n</html>\n'
            % ('en' if lang == 'en' else 'zh-CN', h, body_attr,
               header(lang, page_name, fname), body_html))

EN_BOOK_DESC = ('Javvin Company — The Power of Desire: A Brief History of Scientific &amp; '
                'Technological Innovation, by Jielin Dong. Ebook (PDF) sold here.')
ZH_BOOK_DESC = 'Javvin Company — 董洁林作品：《欲望的力量：人类科技创新简史》（第二版）。电子版 PDF 本站出售。'

def cards(lang):
    if lang == 'en':
        items = [('books.html', 'Books', 'The Power of Desire — ebook (PDF) sold here.'),
                 ('posters.html', 'Posters', 'Digital posters — download the PDF and print it yourself.'),
                 ('articles.html', 'Articles', 'Forewords by Xue Lan, Yan Yan, and Sun Xiaochun.'),
                 ('about.html', 'About', 'About Javvin Company and how to reach us.')]
    else:
        items = [('books.html', '书籍', '《欲望的力量：人类科技创新简史》（第二版）电子版。'),
                 ('posters.html', '图谱', '电子图谱 — 下载高清 PDF，自行打印装裱。'),
                 ('articles.html', '文章', '薛澜、阎焱、孙小淳三篇推荐序。'),
                 ('about.html', '关于', 'Javvin 公司简介与联系方式。')]
    inner = '\n'.join('<a class="card" href="%s"><h3>%s</h3><p>%s</p></a>' % i for i in items)
    return '<div class="cards">\n%s\n</div>' % inner

def build(src_fixed, lang, out_dir):
    h = hero(src_fixed)
    # add an explore button into the hero, before the meta list
    btn_text = 'Explore the Book' if lang == 'en' else '了解本书'
    h = h.replace('<ul class="meta">',
                  '<a class="hero-btn" href="books.html">%s</a>\n<ul class="meta">' % btn_text, 1)
    bodies = {
        'home': h + '\n' + cards(lang) + '\n' + footer(src_fixed),
        'books': section(src_fixed, 'books') + '\n' + footer(src_fixed),
        'posters': section(src_fixed, 'posters') + '\n' + footer(src_fixed),
        'articles': section(src_fixed, 'articles') + '\n' + footer(src_fixed),
        'about': section(src_fixed, 'about') + '\n' + footer(src_fixed),
    }
    if lang == 'en':
        meta = {
            'home': ('index.html', 'Javvin Company — The Power of Desire: A Brief History of Scientific &amp; Technological Innovation',
                     EN_BOOK_DESC, 'Javvin Company — The Power of Desire: A Brief History of Scientific &amp; Technological Innovation'),
            'books': ('books.html', 'Books — Javvin Company', EN_BOOK_DESC,
                      'Javvin Company — The Power of Desire: A Brief History of Scientific &amp; Technological Innovation'),
            'posters': ('posters.html', 'Posters — Javvin Company',
                        'Digital posters (PDF) from Javvin Company — download and print yourself.',
                        'Javvin Company — Posters'),
            'articles': ('articles.html', 'Articles — Javvin Company',
                         'Forewords to The Power of Desire by Xue Lan, Yan Yan, and Sun Xiaochun — Javvin Company.',
                         'Javvin Company — Articles'),
            'about': ('about.html', 'About — Javvin Company',
                      'Javvin Company is an independent publisher in San Francisco, specializing in books and posters on technological innovation.',
                      'Javvin Company — About'),
        }
    else:
        meta = {
            'home': ('index.html', 'Javvin 公司 — 《欲望的力量：人类科技创新简史》', ZH_BOOK_DESC,
                     'Javvin 公司 — 《欲望的力量：人类科技创新简史》（第二版）'),
            'books': ('books.html', '书籍 — Javvin 公司', ZH_BOOK_DESC,
                      'Javvin 公司 — 《欲望的力量：人类科技创新简史》（第二版）'),
            'posters': ('posters.html', '图谱 — Javvin 公司',
                        'Javvin 公司电子图谱 — 购买后下载高清 PDF，自行打印装裱。', 'Javvin 公司 — 图谱'),
            'articles': ('articles.html', '文章 — Javvin 公司',
                         '薛澜、阎焱、孙小淳为《欲望的力量：人类科技创新简史》撰写的推荐序。', 'Javvin 公司 — 文章'),
            'about': ('about.html', '关于 — Javvin 公司',
                      'Javvin 公司是一家位于旧金山的独立出版社，专注于出版科技创新主题的图书与图谱。', 'Javvin 公司 — 关于'),
        }
    for name, (fname, title, desc, ogt) in meta.items():
        html = page(lang, name, fname, title, desc, ogt, bodies[name])
        (out_dir / fname).write_text(html)
        print('wrote', out_dir / fname, len(html))

build(EN, 'en', ROOT)
build(ZH, 'zh', ROOT / 'zh')
print('done')
