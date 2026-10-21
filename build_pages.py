#!/usr/bin/env python3
# Rebuild javvincompany.github.io into /en/ and /zh/ trees (one page per menu
# category per language), each page with its own title/description/lang tags,
# plus schema.org Book JSON-LD (with ISBN) on home + books pages.
# Content blocks are taken from the deployed split pages (build #1 outputs),
# which carry the canonical titles:
#   EN: The Power of Desire: A Brief History of Scientific & Technological Innovation
#   ZH: 《欲望的力量：人类科技创新简史》
import re, pathlib, json

ROOT = pathlib.Path('/home/hatch/workspace/website')
# Sources: the current /en/ and /zh/ trees (root files are redirect stubs now)
en_home = (ROOT / 'en' / 'index.html').read_text()
en_books = (ROOT / 'en' / 'books.html').read_text()
zh_home = (ROOT / 'zh' / 'index.html').read_text()
zh_books = (ROOT / 'zh' / 'books.html').read_text()

STYLE = re.search(r'<style>.*?</style>', en_home, re.S).group(0)
EXTRA_CSS = re.search(r'<style>\s*\.cards.*?</style>', en_home, re.S).group(0)

def section(html, sid):
    return re.search(r'<section class="block" id="%s">.*?</section>' % sid, html, re.S).group(0)

def hero(html):
    return re.search(r'<div class="hero">.*?(?=<div class="cards">)', html, re.S).group(0).rstrip() + '\n'

def footer(html):
    return re.search(r'<footer>.*?</footer>', html, re.S).group(0)

def get_page(fname, zh=False):
    return (ROOT / 'zh' / fname if zh else ROOT / 'en' / fname).read_text()

BASE = 'https://javvincompany.github.io/'
BOOK_JSONLD = {
    'en': {
        '@context': 'https://schema.org', '@type': 'Book',
        'name': 'The Power of Desire: A Brief History of Scientific & Technological Innovation',
        'author': {'@type': 'Person', 'name': 'Jielin Dong'},
        'publisher': {'@type': 'Organization', 'name': 'Javvin Company'},
        'inLanguage': 'en', 'isbn': '9781602670310',
        'bookFormat': 'https://schema.org/Paperback', 'bookEdition': 'Second edition',
        'numberOfPages': 482, 'datePublished': '2027-01-01',
        'image': BASE + 'assets/covers/cover-en-front.jpg',
        'url': BASE + 'en/books.html',
        'offers': {'@type': 'Offer', 'url': 'https://payhip.com/b/LdW15',
                   'price': '12.99', 'priceCurrency': 'USD',
                   'availability': 'https://schema.org/InStock', 'category': 'Ebook (PDF)'},
    },
    'zh': {
        '@context': 'https://schema.org', '@type': 'Book',
        'name': '欲望的力量：人类科技创新简史',
        'author': {'@type': 'Person', 'name': '董洁林'},
        'publisher': {'@type': 'Organization', 'name': 'Javvin Company'},
        'inLanguage': 'zh', 'isbn': '9781602670303',
        'bookFormat': 'https://schema.org/Paperback', 'bookEdition': '第二版',
        'numberOfPages': 424, 'datePublished': '2027-01-01',
        'image': BASE + 'assets/covers/cover-front.jpg',
        'url': BASE + 'zh/books.html',
        'offers': {'@type': 'Offer', 'url': 'https://payhip.com/b/ioAfP',
                   'price': '12.99', 'priceCurrency': 'USD',
                   'availability': 'https://schema.org/InStock', 'category': '电子书（PDF）'},
    },
}

def header(lang, page, fname):
    if lang == 'en':
        nav = [('books.html', 'Books'), ('posters.html', 'Posters'),
               ('articles.html', 'Articles'), ('about.html', 'About')]
        self_link = './' if page == 'home' else fname
        other = '/zh/' if page == 'home' else '/zh/' + fname
        lang_html = ('<div class="lang-switch"><a class="active" href="%s">EN</a>'
                     '<a href="%s">中文</a></div>' % (self_link, other))
    else:
        nav = [('books.html', '书籍'), ('posters.html', '图谱'),
               ('articles.html', '文章'), ('about.html', '关于')]
        self_link = './' if page == 'home' else fname
        other = '/en/' if page == 'home' else '/en/' + fname
        lang_html = ('<div class="lang-switch"><a href="%s">EN</a>'
                     '<a class="active" href="%s">中文</a></div>' % (other, self_link))
    links = '\n'.join('<a href="%s"><span>%s</span></a>' % (h, t) for h, t in nav)
    return ('<header>\n<a aria-label="Javvin Company" class="logo" href="./">'
            '<img alt="Javvin Company" src="../assets/javvin-wordmark.svg"/></a>\n<nav>\n%s\n%s\n</nav>\n</header>'
            % (links, lang_html))

def head(lang, page, fname, title, desc, og_title):
    seg = '' if page == 'home' else fname
    canon = BASE + lang + '/' + seg
    alt_en = BASE + 'en/' + seg
    alt_zh = BASE + 'zh/' + seg
    jsonld = ''
    if page in ('home', 'books'):
        jsonld = ('\n<script type="application/ld+json">\n%s\n</script>'
                  % json.dumps(BOOK_JSONLD[lang], ensure_ascii=False, indent=2))
    og_img = BASE + ('assets/covers/cover-en-front.jpg' if lang == 'en'
                     else 'assets/covers/cover-front.jpg')
    return f'''<head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<title>{title}</title>
<meta content="{desc}" name="description"/>
<meta content="UjqM5b327ctUoN0HMQ91Dvwp_7B0VCA48ALKU27OKyU" name="google-site-verification"/>
<link href="{canon}" rel="canonical"/><link href="{alt_en}" hreflang="x-default" rel="alternate"/><link href="{alt_zh}" hreflang="zh" rel="alternate"/><link href="{alt_en}" hreflang="en" rel="alternate"/>
<meta content="website" property="og:type"/>
<meta content="Javvin Company" property="og:site_name"/>
<meta content="{'en_US' if lang == 'en' else 'zh_CN'}" property="og:locale"/>
<meta content="{og_title}" property="og:title"/>
<meta content="{desc}" property="og:description"/>
<meta content="{canon}" property="og:url"/>
<meta content="{og_img}" property="og:image"/>{jsonld}
{STYLE}
{EXTRA_CSS}
</head>'''

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

EN_BOOK_DESC = ('Javvin Company — The Power of Desire: A Brief History of Scientific &amp; '
                'Technological Innovation, by Jielin Dong. Ebook (PDF) sold here.')
ZH_BOOK_DESC = 'Javvin Company — 董洁林作品：《欲望的力量：人类科技创新简史》（第二版）。电子版 PDF 本站出售。'
META = {
    'en': {
        'home': ('index.html', 'Javvin Company — The Power of Desire: A Brief History of Scientific &amp; Technological Innovation',
                 EN_BOOK_DESC, 'Javvin Company — The Power of Desire: A Brief History of Scientific &amp; Technological Innovation'),
        'books': ('books.html', 'Books — Javvin Company', EN_BOOK_DESC,
                  'Javvin Company — The Power of Desire: A Brief History of Scientific &amp; Technological Innovation'),
        'posters': ('posters.html', 'Posters — Javvin Company',
                    'Digital posters (PDF) from Javvin Company — download and print yourself.', 'Javvin Company — Posters'),
        'articles': ('articles.html', 'Articles — Javvin Company',
                     'Forewords to The Power of Desire by Xue Lan, Yan Yan, and Sun Xiaochun — Javvin Company.', 'Javvin Company — Articles'),
        'about': ('about.html', 'About — Javvin Company',
                  'Javvin Company is an independent publisher in San Francisco, specializing in books and posters on technological innovation.', 'Javvin Company — About'),
    },
    'zh': {
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
    },
}

def build(lang, out_dir):
    zh = (lang == 'zh')
    home = zh_home if zh else en_home
    books_pg = zh_books if zh else en_books
    hero_html = hero(home)
    # visible ISBN line in the hero meta list
    isbn_li = ('<li><span class="k">ISBN</span>978-1-60267-030-3</li>' if zh
               else '<li><span class="k">ISBN</span>978-1-60267-031-0</li>')
    hero_html = hero_html.replace('</ul>', isbn_li + '\n</ul>', 1)
    books_sec = section(books_pg, 'books')
    # visible ISBN line in the book info
    if zh:
        books_sec = books_sec.replace(
            '<p class="en">（第二版）董洁林 著 · Javvin Company</p>',
            '<p class="en">（第二版）董洁林 著 · Javvin Company</p>\n<p class="en">纸质版 ISBN：978-1-60267-030-3</p>', 1)
    else:
        books_sec = books_sec.replace(
            '<p class="en">by Jielin Dong · Javvin Company</p>',
            '<p class="en">by Jielin Dong · Javvin Company</p>\n<p class="en">Print edition ISBN: 978-1-60267-031-0</p>', 1)
    bodies = {
        'home': hero_html + '\n' + cards(lang) + '\n' + footer(books_pg),
        'books': books_sec + '\n' + footer(books_pg),
        'posters': section(get_page('posters.html', zh), 'posters') + '\n' + footer(books_pg),
        'articles': section(get_page('articles.html', zh), 'articles') + '\n' + footer(books_pg),
        'about': section(get_page('about.html', zh), 'about') + '\n' + footer(books_pg),
    }
    if lang == 'en':
        bodies = {k: v.replace('"assets/', '"../assets/') for k, v in bodies.items()}
    for name, (fname, title, desc, ogt) in META[lang].items():
        hd = head(lang, name, fname, title, desc, ogt)
        body_attr = ' class="en"' if lang == 'en' else ''
        html = ('<!DOCTYPE html>\n<html lang="%s">\n%s\n<body%s>\n%s\n%s\n</body>\n</html>\n'
                % ('en' if lang == 'en' else 'zh-CN', hd, body_attr,
                   header(lang, name, fname), bodies[name]))
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / fname).write_text(html)
        print('wrote', out_dir / fname, len(html))

build('en', ROOT / 'en')
build('zh', ROOT / 'zh')

STUB = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<title>Javvin Company</title>
<link href="https://javvincompany.github.io/en/{seg}" rel="canonical"/>
<meta content="0; url=/en/{seg}" http-equiv="refresh"/>
<meta content="noindex" name="robots"/>
</head>
<body>
<p>This page has moved to <a href="/en/{seg}">Javvin Company (English)</a>.</p>
</body>
</html>
'''
for fname in ['index.html', 'books.html', 'posters.html', 'articles.html', 'about.html']:
    seg = '' if fname == 'index.html' else fname
    (ROOT / fname).write_text(STUB.format(seg=seg))
    print('stub', fname, '-> /en/' + seg)
print('done')
