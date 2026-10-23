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
# smaller covers (idempotent: match whatever current values are)
STYLE = re.sub(r'(\.hero img \{\s*width: min\()\d+px', r'\g<1>280px', STYLE)
STYLE = re.sub(r'(\.book-card img \{\s*width: min\()\d+px', r'\g<1>150px', STYLE)
EXTRA_CSS = re.search(r'<style>\s*\.cards.*?</style>', en_home, re.S).group(0)
if '.tagline' not in EXTRA_CSS:
    EXTRA_CSS = EXTRA_CSS.replace('</style>',
        '  .tagline { font-size: 1.08rem; color: var(--ink); letter-spacing: 0.03em; line-height: 1.7; margin: 0.25rem 0 1rem; }\n</style>')
if '.toc-row' not in EXTRA_CSS:
    EXTRA_CSS = EXTRA_CSS.replace('</style>',
        '  .toc-row { display: flex; justify-content: space-between; gap: 1rem; padding: 0.12rem 0; }\n'
        '  .toc-part { font-weight: bold; margin-top: 0.9rem; }\n'
        '  .praise { margin-bottom: 1.6rem; }\n'
        '  .praise p { font-size: 1.02rem; line-height: 1.75; }\n'
        '  .praise .who { color: var(--muted); margin-top: 0.3rem; font-size: 0.95rem; }\n</style>')
if '.hero-tagline' not in EXTRA_CSS:
    EXTRA_CSS = EXTRA_CSS.replace('</style>',
        '  .hero-tagline { color: #e8e2d4; font-size: 1.05rem; line-height: 1.75; letter-spacing: 0.03em; margin: 1.25rem 0 0.25rem; }\n</style>')
if 'body.en .hero-text h1' not in EXTRA_CSS:
    EXTRA_CSS = EXTRA_CSS.replace('</style>',
        '  body.en .hero-text h1 { font-size: clamp(1.7rem, 4.2vw, 2.6rem); }\n</style>')
if 'hero-btn.alt' not in EXTRA_CSS:
    EXTRA_CSS = EXTRA_CSS.replace('</style>',
        '  .hero-btn.alt { background: transparent; border: 1px solid var(--gold); color: var(--gold); margin-left: 0.5rem; }\n'
        '  @media (max-width: 640px) {\n'
        '    header { padding: 0.75rem 1rem; }\n'
        '    .logo img { height: 44px; }\n'
        '    nav { flex-wrap: wrap; gap: 0.5rem 0.9rem; justify-content: flex-end; }\n'
        '    nav a, .lang-switch a { white-space: nowrap; }\n'
        '    .hero { flex-direction: column; padding: 2rem 1.25rem 3rem; gap: 1.5rem; }\n'
        '    .hero-text { order: -1; }\n'
        '    .hero img { width: min(190px, 55vw); }\n'
        '    .hero-btn.alt { margin-left: 0; margin-top: 0.75rem; }\n'
        '  }\n</style>')
if '.poster-card' not in EXTRA_CSS:
    EXTRA_CSS = EXTRA_CSS.replace('</style>',
        '  .poster-card { max-width: 780px; margin: 0 auto; }\n'
        '  .poster-card img { width: 100%; border-radius: 6px; box-shadow: 0 16px 40px rgba(16,23,34,0.22); display: block; }\n'
        '  .poster-info { margin-top: 1.4rem; }\n'
        '  .poster-info h3 { font-size: 1.5rem; letter-spacing: 0.06em; margin-bottom: 0.25rem; }\n'
        '  .poster-info .en { color: var(--muted); font-style: italic; margin-bottom: 1rem; }\n'
        '  .poster-info p { line-height: 1.75; margin-bottom: 0.9rem; }\n</style>')
if '.poster-viewer' not in EXTRA_CSS:
    EXTRA_CSS = EXTRA_CSS.replace('</style>',
        '  .poster-viewer { position: relative; border-radius: 6px; overflow: hidden; box-shadow: 0 16px 40px rgba(16,23,34,0.22); line-height: 0; touch-action: none; cursor: grab; }\n'
        '  .poster-viewer img { width: 100%; display: block; user-select: none; -webkit-user-drag: none; }\n'
        '  .poster-lens { position: absolute; width: min(46%, 430px); aspect-ratio: 3/2; border: 4px solid #fff; border-radius: 4px; box-shadow: 0 14px 34px rgba(16,23,34,0.35); background-repeat: no-repeat; display: none; pointer-events: none; }\n'
        '  .poster-viewer.ready .poster-lens { display: block; }\n'
        '  .poster-hint { color: var(--muted); font-size: 0.95rem; text-align: center; margin-top: 0.6rem; }\n</style>')
if '.poster-chips' not in EXTRA_CSS:
    EXTRA_CSS = EXTRA_CSS.replace('</style>',
        '  .poster-price { font-size: 1.15rem; margin: 0.4rem 0 0.9rem; }\n'
        '  .poster-chips { display: flex; gap: 0.5rem; flex-wrap: wrap; margin: 0.9rem 0 0.6rem; }\n'
        '  .poster-chips button { font: inherit; font-size: 0.92rem; padding: 0.35rem 0.95rem; border-radius: 999px; border: 1px solid var(--gold); background: transparent; color: var(--ink); cursor: pointer; }\n'
        '  .poster-chips button.active { background: var(--gold); color: #101722; }\n'
        '  .poster-detail img { width: 100%; border-radius: 6px; box-shadow: 0 10px 26px rgba(16,23,34,0.18); display: block; }\n</style>')
if '.cover-fig' not in EXTRA_CSS:
    EXTRA_CSS = EXTRA_CSS.replace('</style>',
        '  .cover-fig { margin: 0; text-align: center; }\n'
        '  .hero .cover-fig figcaption { color: #e8e2d4; font-size: 1.05rem; line-height: 1.75; letter-spacing: 0.03em; max-width: 320px; margin: 1rem auto 0; }\n'
        '  .book-card .cover-fig figcaption { color: var(--ink); font-size: 1.08rem; line-height: 1.7; letter-spacing: 0.03em; max-width: 280px; margin: 0.9rem auto 0; }\n</style>')
if '.nr-badge' not in EXTRA_CSS:
    EXTRA_CSS = EXTRA_CSS.replace('</style>',
        '  .nr-badge { display: inline-block; background: var(--gold); color: #101722; font-weight: 700; font-size: 0.8rem; letter-spacing: 0.16em; text-transform: uppercase; padding: 0.32rem 0.85rem; border-radius: 999px; margin-bottom: 0.9rem; }\n</style>')
if '.prod-grid' not in EXTRA_CSS:
    EXTRA_CSS = EXTRA_CSS.replace('</style>',
        '  html { scroll-behavior: smooth; }\n'
        '  .prod-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1.4rem; }\n'
        '  @media (max-width: 720px) { .prod-grid { grid-template-columns: 1fr; } }\n'
        '  .prod-card { border: 1px solid rgba(16,23,34,0.14); border-radius: 10px; padding: 1.2rem 1.3rem 1.35rem; background: rgba(255,255,255,0.35); }\n'
        '  .prod-card .prod-img { width: 100%; height: 230px; border-radius: 6px; display: block; margin-bottom: 1rem; background: #fff; }\n'
        '  .prod-card .prod-img.book { object-fit: contain; }\n'
        '  .prod-card .prod-img.poster { object-fit: cover; }\n'
        '  .prod-card h3 { margin: 0 0 0.35rem; font-size: 1.35rem; line-height: 1.4; }\n'
        '  .prod-card .prod-sub { color: var(--muted); line-height: 1.65; margin: 0 0 0.6rem; }\n'
        '  .prod-card .prod-price { font-size: 1.2rem; margin: 0.3rem 0 0.9rem; }\n'
        '  .prod-actions { display: flex; align-items: center; gap: 1.1rem; flex-wrap: wrap; }\n'
        '  .prod-actions .detail-link { color: var(--gold); text-decoration: none; font-size: 1rem; }\n</style>')
if '.art-list' not in EXTRA_CSS:
    EXTRA_CSS = EXTRA_CSS.replace('</style>',
        '  .art-list { display: grid; gap: 1.1rem; }\n'
        '  .art-card { display: block; border: 1px solid rgba(16,23,34,0.14); border-radius: 8px; padding: 1.2rem 1.4rem; text-decoration: none; color: var(--ink); background: rgba(255,255,255,0.35); }\n'
        '  .art-card:hover { border-color: var(--gold); }\n'
        '  .art-card h3 { margin: 0 0 0.3rem; font-size: 1.3rem; }\n'
        '  .art-card .byline { margin: 0 0 0.6rem; }\n'
        '  .art-card .art-guide { line-height: 1.7; margin: 0 0 0.7rem; }\n'
        '  .art-more { color: var(--gold); font-size: 0.98rem; }\n'
        '  .article-page h1 { font-size: 1.9rem; line-height: 1.35; margin-bottom: 0.4rem; }\n'
        '  .back-link { margin-top: 2rem; }\n</style>')
if '.book-price' not in EXTRA_CSS:
    EXTRA_CSS = EXTRA_CSS.replace('</style>',
        '  .book-price { font-size: 1.2rem; margin: 0.6rem 0 0.4rem; }\n'
        '  .buy-bottom { text-align: left; }\n</style>')

import json as _json
def toc_block(lang):
    data = _json.loads((ROOT / ('toc-zh.json' if lang == 'zh' else 'toc-en.json')).read_text())
    rows = []
    for e in data:
        t = e['title']
        is_part = bool(re.match(r'^(VIII|VII|VI|IV|V|III|II|I)\s', t)) and not t.startswith(('Chapter', '第'))
        cls = 'toc-row toc-part' if is_part else 'toc-row'
        rows.append('<div class="%s"><span>%s</span><span>%s</span></div>' % (cls, t, e['page']))
    label = '目录' if lang == 'zh' else 'Table of Contents'
    return ('<section class="block" id="toc">\n<details class="foreword">\n<summary><span>%s</span></summary>\n<div>\n%s\n</div>\n</details>\n</section>'
            % (label, '\n'.join(rows)))

PRAISE = {
    'en': [
        ('Elegant prose, compelling stories, and rigorous analysis—an achievement that invites comparison with Sapiens.', 'Xue Lan', 'Dean of Schwarzman College, Tsinghua University'),
        ('The history of technological invention from the perspective of those who use technology, making it feel tangible and refreshingly new.', 'Sun Xiaochun', 'Professor, University of Chinese Academy of Sciences'),
        ('Vivid, accessible language and stories rooted in everyday life ... showing how the world we live in came to be—and who brought it into being.', 'Zhiwu Chen', 'Chair Professor of Finance, The University of Hong Kong'),
        ('The quiet voices in the long tail of the spectrum of ideas become especially precious, because the future holds countless possibilities.', 'Yan Yan', 'Founding Managing Partner, SAIF Partners'),
        ('Dong weaves human needs into the historical warp and data analysis into the logical weft to examine how science and technology have shaped human history.', 'Guosheng Wu', 'Chair, Department of the History of Science, Tsinghua University'),
        ('Through quantitative analysis and exceptionally well-grounded arguments, the book offers illuminating answers.', 'Weigang Wan', 'Science Writer'),
    ],
    'zh': [
        ('把传统的科技创新编年史解构，再用优美的文笔、引人入胜的故事和严谨的学术分析按照新的体系重建。', '薛澜', '清华大学苏世民书院院长'),
        ('以技术使用者的角度，观察和体会人类技术的发明创造历史，使人感到真切且耳目一新。', '孙小淳', '中国科学院大学人文学院教授'),
        ('以通俗鲜活的语言和生活化故事讲解一次次科技创新，让你了解今天我们生活的世界是怎么来的、是谁带来的。', '陈志武', '香港大学金融学讲席教授'),
        ('思想谱系分布长尾里的微弱声音就格外弥足珍贵，因为未来有无数可能性。', '阎焱', '赛富基金创始管理合伙人'),
        ('以人的需求为历史经线，以科技史的数据分析为逻辑纬线，透视科学技术对人类历史的影响，别具一格，值得关注！', '吴国盛', '清华大学科学史系主任'),
        ('这本书使用量化分析的科学方法、极其扎实的论证，给了我很好的答案。', '万维钢', '科学作家'),
    ],
}

def praise_block(lang):
    items = PRAISE[lang]
    label = '各界推荐' if lang == 'zh' else 'Praise for the Book'
    parts = ['<section class="block" id="praise">\n<h2>%s</h2>' % label]
    for q, name, aff in items:
        if lang == 'zh':
            parts.append('<div class="praise"><p>“%s”</p><p class="who">——%s · %s</p></div>' % (q, name, aff))
        else:
            parts.append('<div class="praise"><p>“%s”</p><p class="who">— %s, %s</p></div>' % (q, name, aff))
    parts.append('</section>')
    return '\n'.join(parts)

def section(html, sid):
    return re.search(r'<section class="block" id="%s">.*?</section>' % sid, html, re.S).group(0)

def hero(html):
    return re.search(r'<div class="hero">.*?(?=<section class="block"|<div class="cards">)', html, re.S).group(0).rstrip() + '\n'

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
        'bookFormat': 'https://schema.org/EBook', 'bookEdition': 'Second edition',
        'numberOfPages': 484,
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
        'bookFormat': 'https://schema.org/EBook', 'bookEdition': '第二版',
        'numberOfPages': 426,
        'image': BASE + 'assets/covers/cover-front.jpg',
        'url': BASE + 'zh/books.html',
        'offers': {'@type': 'Offer', 'url': 'https://payhip.com/b/ioAfP',
                   'price': '12.99', 'priceCurrency': 'USD',
                   'availability': 'https://schema.org/InStock', 'category': '电子书（PDF）'},
    },
}



def license_block(lang):
    if lang == 'en':
        return ('<section class="block" id="license">\n<h2>License Terms</h2>\n<div class="about-text">\n'
                '<p><strong>Digital posters.</strong> Each purchase is a license for one buyer. Personal use: print up to 2 copies (at home, at a print shop, or through an online print service), displayed in one place — your home, one classroom, or one workplace. Institutions using a poster at multiple locations: please buy one license per location. Commercial use: please contact us at javvincompany@gmail.com. Please don’t share or pass on the file, upload it to a public website, or sell the file or printed copies.</p>\n'
                '<p><strong>Ebooks.</strong> Each purchase is a license for one reader. You may read the ebook on your own devices. Please don’t share or pass on the file, upload it to a public website, or resell it.</p>\n'
                '</div>\n</section>')
    return ('<section class="block" id="license">\n<h2>授权条款</h2>\n<div class="about-text">\n'
            '<p><strong>电子图谱。</strong>每次购买为一份授权，限购买者本人。个人使用：可打印不超过 2 份（在家、打印店或在线打印服务均可），展示于一处：家中、一个教室或一个工作场所。机构多点使用：请每个点购买一份授权。商用：请联系 javvincompany@gmail.com。请勿分享或转传文件、勿上传至任何公开网站、勿出售文件或印品。</p>\n'
            '<p><strong>电子书。</strong>每次购买为一份授权，限购买者本人阅读，可在本人设备上使用。请勿分享或转传文件、勿上传至任何公开网站、勿转售。</p>\n'
            '</div>\n</section>')

def bottom_buy(lang):
    if lang == 'en':
        return ('<section class="block buy-bottom" id="buy-bottom">\n<div class="book-info">\n'
                '<p class="book-price">$12.99</p>\n'
                '<a class="buy-btn" href="https://payhip.com/b/LdW15" rel="noopener" target="_blank"><span>Buy the English Ebook · $12.99</span></a>\n'
                '<p class="sample-link"><a href="https://payhip.com/b/RXgzv" rel="noopener" target="_blank">Read a free sample (PDF, 19 pages)</a></p>\n'
                '</div>\n</section>')
    return ('<section class="block buy-bottom" id="buy-bottom">\n<div class="book-info">\n'
            '<p class="book-price">$12.99</p>\n'
            '<a class="buy-btn" href="https://payhip.com/b/ioAfP" rel="noopener" target="_blank"><span>购买中文电子版 · $12.99</span></a>\n'
            '<p class="sample-link"><a href="https://payhip.com/b/P4XcA" rel="noopener" target="_blank">免费试读（18 页，填写邮箱领取）</a></p>\n'
            '</div>\n</section>')

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

def head(lang, page, fname, title, desc, og_title, keywords='', jsonld_override=None):
    seg = '' if page == 'home' else fname
    canon = BASE + lang + '/' + seg
    alt_en = BASE + 'en/' + seg
    alt_zh = BASE + 'zh/' + seg
    jsonld = ''
    if jsonld_override is not None:
        jsonld = ('\n<script type="application/ld+json">\n%s\n</script>'
                  % json.dumps(jsonld_override, ensure_ascii=False, indent=2))
    elif page in ('home', 'books'):
        jsonld = ('\n<script type="application/ld+json">\n%s\n</script>'
                  % json.dumps(BOOK_JSONLD[lang], ensure_ascii=False, indent=2))
    og_img = BASE + ('assets/covers/cover-en-front.jpg' if lang == 'en'
                     else 'assets/covers/cover-front.jpg')
    if page == 'posters':
        og_img = BASE + 'assets/posters/network-protocols-map-share.jpg'
    return f'''<head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<title>{title}</title>
<meta content="{desc}" name="description"/>
<meta content="{keywords}" name="keywords"/>
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
                 ('posters.html', 'Posters', 'Network Protocols Map — digital poster (PDF), $19.99.'),
                 ('articles.html', 'Articles', 'Forewords by Xue Lan, Yan Yan, and Sun Xiaochun.'),
                 ('about.html', 'About', 'About Javvin Company and how to reach us.')]
    else:
        items = [('books.html', '书籍', '《欲望的力量：人类科技创新简史》（第二版）电子版。'),
                 ('posters.html', '图谱', '网络协议全景图 — 电子图谱（PDF），$19.99。'),
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
        'books': ('books.html', 'The Power of Desire — The Book | Javvin Company', EN_BOOK_DESC,
                  'Javvin Company — The Power of Desire: A Brief History of Scientific &amp; Technological Innovation'),
        'posters': ('posters.html', 'Network Protocols Map — Digital Poster | Javvin Company',
                    'Network Protocols Map (2009 classic, revised 2026) — a high-resolution digital poster (PDF) from Javvin Company: download, print, and frame it yourself.', 'Network Protocols Map — Digital Poster | Javvin Company'),
        'articles': ('articles.html', 'Articles & Forewords — Xue Lan, Yan Yan, Sun Xiaochun | Javvin Company',
                     'Forewords and essays on The Power of Desire: A Brief History of Scientific & Technological Innovation — by Xue Lan (Tsinghua), Yan Yan (SAIF Partners), and Sun Xiaochun (UCAS).', 'Articles & Forewords | Javvin Company'),
        'about': ('about.html', 'About Javvin Company — Independent Publisher in San Francisco',
                  'Javvin Company is an independent publisher in San Francisco, specializing in books and posters on technological innovation.', 'Javvin Company — About'),
    },
    'zh': {
        'home': ('index.html', 'Javvin 公司 — 《欲望的力量：人类科技创新简史》', ZH_BOOK_DESC,
                 'Javvin 公司 — 《欲望的力量：人类科技创新简史》（第二版）'),
        'books': ('books.html', '《欲望的力量：人类科技创新简史》（第二版）— 董洁林 | Javvin 公司', ZH_BOOK_DESC,
                  'Javvin 公司 — 《欲望的力量：人类科技创新简史》（第二版）'),
        'posters': ('posters.html', '网络协议全景图 — 电子图谱 | Javvin 公司',
                    '《网络协议全景图》（2009 经典版·2026 修订）— Javvin 公司电子图谱：高清 PDF，购买后下载，自行打印装裱。', '网络协议全景图 — 电子图谱 | Javvin 公司'),
        'articles': ('articles.html', '文章与推荐序 — 薛澜、阎焱、孙小淳 | Javvin 公司',
                     '薛澜、阎焱、孙小淳为《欲望的力量：人类科技创新简史》撰写的三篇推荐序全文。', 'Javvin 公司 — 文章与推荐序'),
        'about': ('about.html', '关于 Javvin 公司 — 旧金山独立出版社',
                  'Javvin 公司是一家位于旧金山的独立出版社，专注于出版科技创新主题的图书与图谱。', 'Javvin 公司 — 关于'),
    },
}


KEYWORDS = {
    'en': {
        'home': 'Javvin Company, The Power of Desire, history of technological innovation, history of innovation, Jielin Dong, science and technology history, ebook',
        'books': 'The Power of Desire, Jielin Dong, history of innovation, history of technological innovation, human needs, ebook PDF, ISBN 9781602670310',
        'posters': 'Network Protocols Map, network protocols poster, TCP/IP poster, OSI model, digital poster PDF, printable wall chart, Javvin',
        'articles': 'Xue Lan, Yan Yan, Sun Xiaochun, foreword, book review, The Power of Desire, history of innovation, Javvin Company',
        'about': 'Javvin Company, independent publisher, San Francisco publisher, Jielin Dong, books on technological innovation',
    },
    'zh': {
        'home': 'Javvin公司, 欲望的力量, 人类科技创新简史, 董洁林, 科技创新史, 科技史, 电子书',
        'books': '欲望的力量, 人类科技创新简史, 董洁林, 第二版, 科技创新史, 人类需求, 电子书PDF, ISBN 9781602670303',
        'posters': '网络协议全景图, 网络协议图, TCP/IP, OSI模型, 电子图谱, 知识图谱, PDF下载打印, Javvin',
        'articles': '薛澜, 阎焱, 孙小淳, 推荐序, 书评, 欲望的力量, 人类科技创新简史, 科技创新史',
        'about': 'Javvin公司, 独立出版社, 旧金山出版社, 董洁林, 科技创新图书',
    },
}

# slug, page title (h1), byline, one-sentence guide, author short name, keywords
ARTICLES = {
    'en': [
        ('xue-lan', 'A Small Boat on the Great River of Human Innovation',
         'Xue Lan (Professor at Tsinghua University and Dean of Schwarzman College, Tsinghua University)',
         'Tsinghua scholar Xue Lan on how the book retells the history of innovation — human needs as its thread, vivid stories and rigorous data as its method.',
         'Xue Lan', 'Xue Lan, Tsinghua University, Schwarzman College, foreword, history of innovation, The Power of Desire, Jielin Dong'),
        ('yan-yan', 'A Minority Voice Worth Cherishing in the Landscape of Ideas',
         'Yan Yan (Founding Managing Partner of SAIF Partners)',
         'Investor Yan Yan on incremental innovation versus major breakthroughs and the coming AI revolution — and why this book is a minority voice worth cherishing.',
         'Yan Yan', 'Yan Yan, SAIF Partners, incremental innovation, major breakthroughs, artificial intelligence, foreword, The Power of Desire'),
        ('sun-xiaochun', 'Why Do Humans Innovate',
         'Sun Xiaochun (Professor, School of Humanities, University of Chinese Academy of Sciences; Former President of the Chinese Society for the History of Science and Technology)',
         'Historian of science Sun Xiaochun on the book\'s grand thought experiment — needs as warp, innovation as weft — and on an author who keeps revising her own views.',
         'Sun Xiaochun', 'Sun Xiaochun, history of science and technology, human needs, technological innovation, foreword, The Power of Desire'),
    ],
    'zh': [
        ('xue-lan', '人类创新历史长河中的一叶轻舟',
         '薛澜（清华大学教授，清华大学苏世民书院院长）',
         '薛澜以创新研究学者的视角，解读本书如何以人类需求为线索、用故事与数据重构万年科技创新史。',
         '薛澜', '薛澜, 清华大学, 苏世民书院, 推荐序, 科技创新史, 欲望的力量, 董洁林'),
        ('yan-yan', '思想谱系里珍贵的少数派声音',
         '阎焱（赛富基金创始管理合伙人）',
         '阎焱从投资人的视角谈渐进式创新与重大突破、人工智能带来的新变革，称本书是思想谱系里珍贵的少数派声音。',
         '阎焱', '阎焱, 赛富基金, 渐进式创新, 重大突破, 人工智能, 推荐序, 欲望的力量'),
        ('sun-xiaochun', '人类为什么要创新——《欲望的力量：人类科技创新简史》第二版推荐序',
         '孙小淳（中国科学院大学人文学院教授，中国科学技术史学会原理事长）',
         '孙小淳以科技史家的眼光，评述本书以需求为经、创新为纬的思想实验与作者不断修正自我的治学态度。',
         '孙小淳', '孙小淳, 科技史, 人类需求, 科技创新, 推荐序, 欲望的力量, 第二版'),
    ],
}

def articles_index(lang):
    h2 = '文章' if lang == 'zh' else 'Articles'
    return ('<section class="block" id="articles">\n<h2>%s</h2>\n<div class="art-list">\n%s\n</div>\n</section>'
            % (h2, art_cards(lang)))

def article_jsonld(lang, art, fname):
    slug, title, _b, guide, author, _k = art
    return {'@context': 'https://schema.org', '@type': 'Article',
            'headline': title,
            'author': {'@type': 'Person', 'name': author},
            'publisher': {'@type': 'Organization', 'name': 'Javvin Company'},
            'inLanguage': lang, 'description': guide,
            'mainEntityOfPage': BASE + lang + '/' + fname,
            'about': {'@type': 'Book',
                      'name': ('欲望的力量：人类科技创新简史' if lang == 'zh'
                               else 'The Power of Desire: A Brief History of Scientific & Technological Innovation')}}


def art_cards(lang):
    zh = (lang == 'zh')
    items = []
    for slug, title, byline, guide, _a, _k in ARTICLES[lang]:
        more = '阅读全文 →' if zh else 'Read the full article →'
        items.append('<a class="art-card" href="articles-%s.html"><h3>%s</h3>'
                     '<p class="byline">%s</p><p class="art-guide">%s</p>'
                     '<span class="art-more">%s</span></a>' % (slug, title, byline, guide, more))
    return '\n'.join(items)

def products_block(lang):
    if lang == 'zh':
        return ('<section class="block" id="products">\n<h2>产品</h2>\n<div class="prod-grid">\n'
                '<div class="prod-card"><img class="prod-img book" src="../assets/covers/cover-front.jpg" alt="《欲望的力量：人类科技创新简史》第二版封面"/>'
                '<h3>《欲望的力量：人类科技创新简史》（第二版）</h3>'
                '<p class="prod-sub">董洁林著 · 电子书（PDF），本站购买后下载；纸质版按需印刷。</p>'
                '<p class="prod-price">$12.99</p>'
                '<div class="prod-actions"><a class="buy-btn" href="https://payhip.com/b/ioAfP" rel="noopener" target="_blank"><span>购买电子书</span></a>'
                '<a class="detail-link" href="books.html">详细介绍 →</a></div></div>\n'
                '<div class="prod-card"><img class="prod-img poster" src="../assets/posters/network-protocols-map-promo.jpg" alt="网络协议全景图"/>'
                '<h3>网络协议全景图</h3>'
                '<p class="prod-sub">Network Protocols Map · 电子图谱（PDF），2009 经典版 · 2026 修订，横版 36×24 英寸，自行打印装裱。</p>'
                '<p class="prod-price">$19.99</p>'
                '<div class="prod-actions"><a class="buy-btn" href="https://payhip.com/b/xO3uf" rel="noopener" target="_blank"><span>购买图谱</span></a>'
                '<a class="detail-link" href="posters.html">详细介绍 →</a></div></div>\n'
                '</div>\n</section>')
    return ('<section class="block" id="products">\n<h2>Our Products</h2>\n<div class="prod-grid">\n'
            '<div class="prod-card"><img class="prod-img book" src="../assets/covers/cover-en-front.jpg" alt="Cover of The Power of Desire, second edition"/>'
            '<h3>The Power of Desire</h3>'
            '<p class="prod-sub">A Brief History of Scientific &amp; Technological Innovation, by Jielin Dong · Ebook (PDF), second edition; print edition by print-on-demand.</p>'
            '<p class="prod-price">$12.99</p>'
            '<div class="prod-actions"><a class="buy-btn" href="https://payhip.com/b/LdW15" rel="noopener" target="_blank"><span>Buy the Ebook</span></a>'
            '<a class="detail-link" href="books.html">Details →</a></div></div>\n'
            '<div class="prod-card"><img class="prod-img poster" src="../assets/posters/network-protocols-map-promo.jpg" alt="Network Protocols Map"/>'
            '<h3>Network Protocols Map</h3>'
            '<p class="prod-sub">Digital poster (PDF) — 2009 classic, revised 2026 · 36×24 in, download and print it yourself.</p>'
            '<p class="prod-price">$19.99</p>'
            '<div class="prod-actions"><a class="buy-btn" href="https://payhip.com/b/xO3uf" rel="noopener" target="_blank"><span>Buy the Poster</span></a>'
            '<a class="detail-link" href="posters.html">Details →</a></div></div>\n'
            '</div>\n</section>')

def home_articles(lang):
    zh = (lang == 'zh')
    h2 = '文章与推荐序' if zh else 'Articles & Forewords'
    return ('<section class="block" id="home-articles">\n<h2>%s</h2>\n<div class="art-list">\n%s\n</div>\n</section>'
            % (h2, art_cards(lang)))

def build(lang, out_dir):
    zh = (lang == 'zh')
    home = zh_home if zh else en_home
    books_pg = zh_books if zh else en_books
    hero_html = hero(home)
    hero_html = re.sub(r'\n?<span class="nr-badge">[^<]*</span>', '', hero_html)
    hero_html = hero_html.replace('<div class="hero-text">',
                                  '<div class="hero-text">\n<span class="nr-badge">New Release</span>', 1)
    # tagline sits under the cover image as its caption (strip earlier placements first)
    hero_html = re.sub(r'\n?<p class="hero-tagline">[^<]*</p>', '', hero_html)
    hero_html = re.sub(r'<figcaption class="cover-caption">[^<]*</figcaption>', '', hero_html)
    hero_html = hero_html.replace('<figure class="cover-fig">', '').replace('</figure>', '')
    hero_cap = ('从吃饱穿暖到人工智能，沿着人类欲望的线索，重新理解科技如何改变社会和历史。' if zh
                else 'From food and clothing to artificial intelligence — following the thread of human desire to rethink how technology changes society and history.')
    hero_html = re.sub(r'(<img[^>]*covers/[^>]*>)',
                       r'<figure class="cover-fig">\1<figcaption class="cover-caption">%s</figcaption></figure>' % hero_cap,
                       hero_html, count=1)
    # free-sample button next to the explore button (strip earlier injected one first)
    hero_html = re.sub(r'\n?<a class="hero-btn alt"[^>]*>[^<]*</a>', '', hero_html)
    if zh:
        sample_btn = '\n<a class="hero-btn alt" href="https://payhip.com/b/P4XcA" rel="noopener" target="_blank">免费试读</a>'
        explore = '<a class="hero-btn" href="books.html">了解本书</a>'
    else:
        sample_btn = '\n<a class="hero-btn alt" href="https://payhip.com/b/RXgzv" rel="noopener" target="_blank">Read a Free Sample</a>'
        explore = '<a class="hero-btn" href="books.html">Explore the Book</a>'
    hero_html = hero_html.replace(explore, explore + sample_btn, 1)
    # visible ISBN line in the hero meta list (strip earlier injected lines first)
    hero_html = re.sub(r'\n?<li><span class="k">ISBN</span>[^<]*</li>', '', hero_html)
    isbn_li = ('<li><span class="k">ISBN</span>978-1-60267-030-3</li>' if zh
               else '<li><span class="k">ISBN</span>978-1-60267-031-0</li>')
    hero_html = hero_html.replace('</ul>', isbn_li + '\n</ul>', 1)
    books_sec = section(books_pg, 'books')
    # author bio section after the book introduction
    if zh:
        bio = ('<section class="block" id="author">\n<h2>作者简介</h2>\n<div class="about-text">\n'
               '<p>董洁林博士是一位学者和评论家，研究领域涵盖科技史、创新政策与全球科技竞争。她是《华尔街日报》和《金融时报》中文版的长期撰稿人，发表文章众多，并著有五部著作。</p>\n'
               '<p>董博士曾在清华大学和苏州大学担任学术与研究职务。在清华大学，她曾任中国科学学与科技政策研究院兼职研究员，并任技术创新研究中心兼职教授、学术委员会委员。在苏州大学，她曾任特聘教授、企业创新与发展研究中心主任。她的职业生涯还包括在朗讯、思科、Network Associates 等科技公司担任管理职务，以及在金融服务机构和科研院所任职。她曾出任多家科技初创企业的董事。</p>\n'
               '<p>董博士 1988 年获卡内基梅隆大学物理学博士学位，1982 年获中山大学学士学位。她通过竞争极为激烈的 CUSPEA（中美联合培养物理研究生）项目赴美攻读研究生。</p>\n'
               '</div>\n</section>')
    else:
        bio = ('<section class="block" id="author">\n<h2>About the Author</h2>\n<div class="about-text">\n'
               '<p>Dr. Jielin Dong is a scholar and commentator whose work spans the history of science and technology, innovation policy, and global technology competition. She is a regular contributor to the Chinese editions of The Wall Street Journal and the Financial Times. She has published numerous articles and five books.</p>\n'
               '<p>Dr. Dong has held academic and research appointments at Tsinghua University and Soochow University. At Tsinghua, she has served as a part-time research fellow at the China Institute for Science and Technology Policy and as a part-time professor and academic committee member at the Research Center for Technological Innovation. At Soochow, she has served as a distinguished professor and director of the Center for Enterprise Innovation and Development. Her career also includes management roles at technology companies, including Lucent, Cisco, and Network Associates, as well as positions in financial services and scientific research institutes. She has served on the boards of several technology startups.</p>\n'
               '<p>Dr. Dong earned her Ph.D. in physics from Carnegie Mellon University in 1988 and her B.S. from Sun Yat-sen University in 1982. She went to the United States for graduate study through the highly competitive CUSPEA program.</p>\n'
               '</div>\n</section>')
    books_sec = books_sec + '\n' + toc_block(lang) + '\n' + praise_block(lang) + '\n' + bio
    # return policy lives on the About page (moved there 2026-10-21 at her request)
    if zh:
        returns = ('<section class="block" id="returns">\n<h2>退货政策</h2>\n<div class="about-text">\n'
                   '<p>电子产品（电子书与电子图谱）一经交付完成，概不退货退款。本店保证文件成功交付：如下载失败或文件损坏，将免费重新交付。</p>\n'
                   '<p>印刷版采用按需印刷（Print-on-Demand）方式：您下单后，专门为您印制并寄送。如果您从本网站购买的印刷版出现印刷或装订瑕疵、需要退换，请联系 javvincompany@gmail.com。如果您从其他网站或书店购买印刷版，其退换依出售该印刷版之零售商的政策办理。</p>\n'
                   '</div>\n</section>')
    else:
        returns = ('<section class="block" id="returns">\n<h2>Return Policy</h2>\n<div class="about-text">\n'
                   '<p>All sales of digital products (ebooks and digital posters) are final upon completion of delivery; delivered digital products are non-refundable. We guarantee successful delivery of your files — if a download fails or a file is corrupted, we will re-deliver it at no additional charge.</p>\n'
                   '<p>Print editions are produced by print-on-demand: when you place an order, a copy is printed especially for you and shipped to you. If a print copy purchased from this website has printing or binding defects and you need a return or exchange, please contact javvincompany@gmail.com. If you purchased the print edition from another website or bookstore, its return or exchange is governed by the policy of the retailer that sold it.</p>\n'
                   '</div>\n</section>')
    # book-info layout (byline / price+buy+sample / spec line / tagline) is canonical in the source pages
    bodies = {
        'home': hero_html + '\n' + products_block(lang) + '\n' + home_articles(lang) + '\n' + praise_block(lang) + '\n' + footer(books_pg),
        'books': books_sec + '\n' + bottom_buy(lang) + '\n' + footer(books_pg),
        'posters': section(get_page('posters.html', zh), 'posters') + '\n' + footer(books_pg),
        'articles': articles_index(lang) + '\n' + footer(books_pg),
        'about': section(get_page('about.html', zh), 'about') + '\n' + license_block(lang) + '\n' + returns + '\n' + footer(books_pg),
    }
    if lang == 'en':
        bodies = {k: v.replace('"assets/', '"../assets/') for k, v in bodies.items()}
    for name, (fname, title, desc, ogt) in META[lang].items():
        hd = head(lang, name, fname, title, desc, ogt, keywords=KEYWORDS[lang][name])
        body_attr = ' class="en"' if lang == 'en' else ''
        html = ('<!DOCTYPE html>\n<html lang="%s">\n%s\n<body%s>\n%s\n%s\n</body>\n</html>\n'
                % ('en' if lang == 'en' else 'zh-CN', hd, body_attr,
                   header(lang, name, fname), bodies[name]))
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / fname).write_text(html)
        print('wrote', out_dir / fname, len(html))
    # standalone article pages (split out of the Articles page 2026-10-23 at her request)
    for art in ARTICLES[lang]:
        slug, atitle, _byline, guide, author, akw = art
        fname = 'articles-%s.html' % slug
        frag = (ROOT / 'articles-src' / ('%s-%s.html' % (lang, slug))).read_text().strip()
        frag = frag.replace('<h3>', '<h1>', 1).replace('</h3>', '</h1>', 1)
        back = ('<p class="back-link"><a href="articles.html">← 返回文章列表</a></p>' if zh
                else '<p class="back-link"><a href="articles.html">← Back to Articles</a></p>')
        body = ('<section class="block article-page" id="article">\n%s\n%s\n</section>\n%s'
                % (frag, back, footer(books_pg)))
        if lang == 'en':
            body = body.replace('"assets/', '"../assets/')
        t = ('%s — %s | Javvin 公司' % (atitle, author)) if zh else ('%s — %s | Javvin Company' % (atitle, author))
        hd = head(lang, 'article', fname, t, guide, t, keywords=akw,
                  jsonld_override=article_jsonld(lang, art, fname))
        body_attr = ' class="en"' if lang == 'en' else ''
        html = ('<!DOCTYPE html>\n<html lang="%s">\n%s\n<body%s>\n%s\n%s\n</body>\n</html>\n'
                % ('en' if lang == 'en' else 'zh-CN', hd, body_attr,
                   header(lang, 'article', fname), body))
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
