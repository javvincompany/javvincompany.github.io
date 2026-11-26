#!/usr/bin/env python3
# Rebuild javvin.ai into /en/ and /zh/ trees (one page per menu
# category per language), each page with its own title/description/lang tags,
# plus schema.org Book JSON-LD (with ISBN) on home + book detail pages.
# Content blocks are taken from the deployed split pages (build #1 outputs),
# which carry the canonical titles:
#   EN: The Power of Desire: A Brief History of Scientific & Technological Innovation
#   ZH: 《欲望的力量：人类科技创新简史》
import re, pathlib, json

ROOT = pathlib.Path('/home/hatch/workspace/website')
# Sources: the current /en/ and /zh/ trees (root files are redirect stubs now).
# Book detail bodies live in books-src/ fragments (one per language per book);
# books.html itself is now a listing page built from the BOOKS registry.
en_home = (ROOT / 'en' / 'index.html').read_text()
zh_home = (ROOT / 'zh' / 'index.html').read_text()

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
if '.article-cover' not in EXTRA_CSS:
    EXTRA_CSS = EXTRA_CSS.replace('</style>',
        '  .article-cover { margin: 0 0 1.2rem; text-align: center; }\n'
        '  .article-cover img { width: 180px; height: auto; border-radius: 4px; box-shadow: 0 8px 22px rgba(16,23,34,0.18); }\n'
        '  .article-cover figcaption { color: var(--muted); font-size: 0.95rem; margin-top: 0.5rem; }\n</style>')
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
if '.author-wrap' not in EXTRA_CSS:
    EXTRA_CSS = EXTRA_CSS.replace('</style>',
        '  .author-wrap { display: flex; gap: 1.6rem; align-items: flex-start; } .author-photo { margin: 0; flex: 0 0 180px; } .author-photo img { width: 100%; border-radius: 6px; display: block; box-shadow: 0 10px 26px rgba(16,23,34,0.18); } @media (max-width: 640px) { .author-wrap { flex-direction: column; } .author-photo { flex-basis: auto; width: 170px; margin: 0 auto; } } </style>')
if '.books-intro' not in EXTRA_CSS:
    EXTRA_CSS = EXTRA_CSS.replace('</style>',
        '  .books-intro { text-align: center; font-size: 1.08rem; line-height: 1.7; letter-spacing: 0.03em; margin: 0 0 1.6rem; } </style>')
if '.editions' not in EXTRA_CSS:
    EXTRA_CSS = EXTRA_CSS.replace('</style>',
        '  .editions { width: 100%; border-collapse: collapse; margin: 0.5rem 0 1rem; } .editions th, .editions td { text-align: left; padding: 0.6rem 0.75rem; border-bottom: 1px solid #e2dacc; line-height: 1.6; } .editions th { letter-spacing: 0.06em; font-size: 0.95rem; } .editions td.price { white-space: nowrap; font-weight: bold; } </style>')
if '.products-box' not in EXTRA_CSS:
    EXTRA_CSS = EXTRA_CSS.replace('</style>',
        '  .article-deck { font-size: 1.12rem; font-style: italic; line-height: 1.7; margin: 0 0 0.4rem; } .article-page .byline { margin: 0 0 1.6rem; } .fig-caption { font-weight: bold; text-align: center; margin: 1.8rem 0 0.6rem; line-height: 1.6; } .fig-note { font-size: 0.92rem; color: #5c5c5c; line-height: 1.7; margin: 0.4rem 0 1.2rem; } .pub-note { font-size: 0.92rem; color: #5c5c5c; margin-top: 2rem; } .article-fig { margin: 1.2rem 0; } .article-fig img { width: 100%; display: block; border-radius: 6px; } .products-box { position: fixed; left: 14px; top: 50%; transform: translateY(-50%); width: 192px; background: #fdfbf7; border: 1px solid #e2dacc; border-radius: 10px; box-shadow: 0 10px 30px rgba(16,23,34,0.16); padding: 0.9rem; z-index: 20; display: none; } .products-box h3 { font-size: 0.95rem; letter-spacing: 0.06em; margin: 0 0 0.5rem; text-align: center; } .products-box a { display: flex; gap: 0.6rem; align-items: flex-start; text-decoration: none; color: var(--ink); padding: 0.55rem 0; border-top: 1px solid #eee6d8; } .products-box a:first-of-type { border-top: none; } .products-box img { width: 52px; flex: 0 0 52px; border-radius: 4px; display: block; } .pb-title { font-size: 0.88rem; line-height: 1.45; display: block; font-weight: bold; } .pb-meta { font-size: 0.78rem; color: #6b6b6b; display: block; line-height: 1.45; } @media (min-width: 1280px) { .products-box { display: block; } } </style>')
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
        href = toc_href(lang, t)
        title_html = '<a href="%s">%s</a>' % (href, t) if href else t
        is_part = bool(re.match(r'^(VIII|VII|VI|IV|V|III|II|I)\s', t)) and not t.startswith(('Chapter', '第'))
        cls = 'toc-row toc-part' if is_part else 'toc-row'
        rows.append('<div class="%s"><span>%s</span><span>%s</span></div>' % (cls, title_html, e['page']))
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

BASE = 'https://javvin.ai/'
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
        'url': BASE + 'en/books-power-of-desire.html',
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
        'url': BASE + 'zh/books-power-of-desire.html',
        'offers': {'@type': 'Offer', 'url': 'https://payhip.com/b/ioAfP',
                   'price': '12.99', 'priceCurrency': 'USD',
                   'availability': 'https://schema.org/InStock', 'category': '电子书（PDF）'},
    },
}



def license_block(lang):
    if lang == 'en':
        return ('<section class="block" id="license">\n<h2>License Terms</h2>\n<div class="about-text">\n'
                '<p><strong>Digital posters.</strong> Each purchase is a license for one buyer. Personal use: print up to 2 copies (at home, at a print shop, or through an online print service), displayed in one place — your home, one classroom, or one workplace. Institutions using a poster at multiple locations: please buy one license per location. Commercial use: please contact us at help@javvin.ai. Please don’t share or pass on the file, upload it to a public website, or sell the file or printed copies.</p>\n'
                '<p><strong>Ebooks.</strong> Each purchase is a license for one reader. You may read the ebook on your own devices. Please don’t share or pass on the file, upload it to a public website, or resell it.</p>\n'
                '</div>\n</section>')
    return ('<section class="block" id="license">\n<h2>授权条款</h2>\n<div class="about-text">\n'
            '<p><strong>电子图谱。</strong>每次购买为一份授权，限购买者本人。个人使用：可打印不超过 2 份（在家、打印店或在线打印服务均可），展示于一处：家中、一个教室或一个工作场所。机构多点使用：请每个点购买一份授权。商用：请联系 help@javvin.ai。请勿分享或转传文件、勿上传至任何公开网站、勿出售文件或印品。</p>\n'
            '<p><strong>电子书。</strong>每次购买为一份授权，限购买者本人阅读，可在本人设备上使用。请勿分享或转传文件、勿上传至任何公开网站、勿转售。</p>\n'
            '</div>\n</section>')

def bottom_buy(lang):
    if lang == 'en':
        return ('<section class="block buy-bottom" id="buy-bottom">\n<div class="book-info">\n'
                '<p class="book-price">$12.99</p>\n'
                '<a class="buy-btn" href="https://payhip.com/b/LdW15" rel="noopener" target="_blank"><span>Buy the English eBook · $12.99</span></a>\n'
                '<p class="sample-link"><a href="https://payhip.com/b/RXgzv" rel="noopener" target="_blank">Read a free sample (PDF, 19 pages)</a></p>\n'
                '</div>\n</section>')
    return ('<section class="block buy-bottom" id="buy-bottom">\n<div class="book-info">\n'
            '<p class="book-price">$12.99</p>\n'
            '<a class="buy-btn" href="https://payhip.com/b/ioAfP" rel="noopener" target="_blank"><span>购买中文电子书 · $12.99</span></a>\n'
            '<p class="sample-link"><a href="https://payhip.com/b/P4XcA" rel="noopener" target="_blank">免费试读（18 页，填写邮箱领取）</a></p>\n'
            '</div>\n</section>')

def header(lang, page, fname):
    if lang == 'en':
        nav = [('books.html', 'Books'), ('posters.html', 'Posters'),
               ('articles.html', 'Articles'), ('for-authors.html', 'For Authors'),
               ('about.html', 'About')]
        self_link = './' if page == 'home' else fname
        other = '/zh/' if page == 'home' else '/zh/' + fname
        lang_html = ('<div class="lang-switch"><a class="active" href="%s">EN</a>'
                     '<a href="%s">中文</a></div>' % (self_link, other))
    else:
        nav = [('books.html', '书籍'), ('posters.html', '图谱'),
               ('articles.html', '文章'), ('for-authors.html', '作者投稿'),
               ('about.html', '关于')]
        self_link = './' if page == 'home' else fname
        other = '/en/' if page == 'home' else '/en/' + fname
        lang_html = ('<div class="lang-switch"><a href="%s">EN</a>'
                     '<a class="active" href="%s">中文</a></div>' % (other, self_link))
    links = '\n'.join('<a href="%s"><span>%s</span></a>' % (h, t) for h, t in nav)
    if lang == 'en':
        box = ('<aside class="products-box">\n<h3>Our Products</h3>\n'
               '<a href="books-power-of-desire.html"><img loading="lazy" alt="The Power of Desire" src="../assets/covers/cover-en-front.jpg"/><span><span class="pb-title">The Power of Desire</span><span class="pb-meta">Book · eBook $12.99</span></span></a>\n'
               '<a href="books-network-protocols-handbook.html"><img loading="lazy" alt="Network Protocols Handbook" src="../assets/covers/handbook-front.jpg"/><span><span class="pb-title">Network Protocols Handbook</span><span class="pb-meta">Book · eBook $24.95</span></span></a>\n'
               '<a href="posters.html"><img loading="lazy" alt="Network Protocols Map" src="../assets/posters/network-protocols-map-share.jpg"/><span><span class="pb-title">Network Protocols Map</span><span class="pb-meta">Poster · $19.99</span></span></a>\n</aside>')
    else:
        box = ('<aside class="products-box">\n<h3>我们的产品</h3>\n'
               '<a href="books-power-of-desire.html"><img loading="lazy" alt="欲望的力量" src="../assets/covers/cover-front.jpg"/><span><span class="pb-title">欲望的力量</span><span class="pb-meta">图书 · 电子书 $12.99</span></span></a>\n'
               '<a href="../en/books-network-protocols-handbook.html"><img loading="lazy" alt="Network Protocols Handbook" src="../assets/covers/handbook-front.jpg"/><span><span class="pb-title">Network Protocols Handbook</span><span class="pb-meta">图书 · 电子书 $24.95</span></span></a>\n'
               '<a href="posters.html"><img loading="lazy" alt="网络协议全景图" src="../assets/posters/network-protocols-map-share.jpg"/><span><span class="pb-title">网络协议全景图</span><span class="pb-meta">图谱 · $19.99</span></span></a>\n</aside>')
    if page == 'home':
        box = ''
    return ('<header>\n<a aria-label="Javvin Company" class="logo" href="./">'
            '<img alt="Javvin Company" src="../assets/javvin-wordmark.svg"/></a>\n<nav>\n%s\n%s\n</nav>\n</header>\n%s'
            % (links, lang_html, box))

def head(lang, page, fname, title, desc, og_title, keywords='', jsonld_override=None):
    seg = '' if page == 'home' else fname
    canon = BASE + lang + '/' + seg
    alt_en = BASE + 'en/' + seg
    alt_zh = BASE + 'zh/' + seg
    jsonld = ''
    if jsonld_override is not None:
        jsonld = ('\n<script type="application/ld+json">\n%s\n</script>'
                  % json.dumps(jsonld_override, ensure_ascii=False, indent=2))
    elif page == 'home':
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
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-KYM6J31ZQ2"></script>
<script>
window.dataLayer = window.dataLayer || [];
function gtag(){{dataLayer.push(arguments);}}
gtag('js', new Date());
gtag('config', 'G-KYM6J31ZQ2');
</script>
<!-- Cloudflare Web Analytics --><script defer src='https://static.cloudflareinsights.com/beacon.min.js' data-cf-beacon='{{"token": "38e3f6f15dc1452d9aab53cc4c968a65"}}'></script><!-- End Cloudflare Web Analytics -->
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

EN_BOOK_DESC = 'The Power of Desire, Second Edition, by Jielin Dong: a brief history of scientific and technological innovation, from food and clothing to AI. $12.99.'
ZH_BOOK_DESC = '《欲望的力量：人类科技创新简史》（第二版），董洁林著——从吃饱穿暖到人工智能，沿着人类欲望的线索重读科技史。电子书（PDF）$12.99。'
EN_HOME_DESC = 'Javvin Company, an AI-native publisher in San Francisco, publishes books and digital posters on technological innovation and network protocols.'
ZH_HOME_DESC = 'Javvin 公司是旧金山的一家 AI 原生出版社，出版科技创新史与网络协议领域的图书和电子图谱。'
META = {
    'en': {
        'home': ('index.html', 'Javvin Company — The Power of Desire: A Brief History of Scientific &amp; Technological Innovation',
                 EN_HOME_DESC, 'Javvin Company — The Power of Desire: A Brief History of Scientific &amp; Technological Innovation'),
        'books': ('books.html', 'Books | Javvin Company',
                  'Books by Jielin Dong, published by Javvin Company — including The Power of Desire: A Brief History of Scientific &amp; Technological Innovation.',
                  'Books | Javvin Company'),
        'posters': ('posters.html', 'Network Protocols Map — Digital Poster | Javvin Company',
                    'Network Protocols Map (2009 classic, revised 2026) — a high-resolution digital poster (PDF) from Javvin Company: download, print, and frame it yourself.', 'Network Protocols Map — Digital Poster | Javvin Company'),
        'articles': ('articles.html', 'Articles & Forewords — Xue Lan, Yan Yan, Sun Xiaochun | Javvin Company',
                     'Forewords, the preface, and essays on The Power of Desire: A Brief History of Scientific & Technological Innovation — by Xue Lan (Tsinghua), Yan Yan (SAIF Partners), and Sun Xiaochun (UCAS).', 'Articles & Forewords | Javvin Company'),
        'serial': ('serial-power-of-desire.html', 'The Power of Desire — Read the Book Online | Javvin Company',
                   'Read The Power of Desire online, section by section: the complete serialization index — preface, opening, all 24 chapters, conclusion, and appendix.', 'The Power of Desire — Serialization Index | Javvin Company'),
        'about': ('about.html', 'About Javvin Company — AI-Native Publisher in San Francisco',
                  'Javvin Company is an AI-native publisher based in San Francisco, specializing in books and posters on technological innovation. AI supports every stage of its work.', 'Javvin Company — About'),
        'for-authors': ('for-authors.html', 'Publish with Javvin — For Authors | Javvin Company',
                        'Publish with Javvin. Your knowledge. Your experience. Your story. A book worth sharing. Javvin welcomes proposals from scientists, engineers, researchers, educators, and other professionals.', 'Publish with Javvin | Javvin Company'),
        'affiliates': ('affiliates.html', 'Become a Javvin Affiliate | Javvin Company',
                        'Earn 30% recommending Javvin books and digital posters: the Network Protocols Map poster, The Power of Desire ebook, and the Network Protocols Handbook ebook.', 'Become a Javvin Affiliate | Javvin Company'),
    },
    'zh': {
        'home': ('index.html', 'Javvin 公司 — 《欲望的力量：人类科技创新简史》', ZH_HOME_DESC,
                 'Javvin 公司 — 《欲望的力量：人类科技创新简史》（第二版）'),
        'books': ('books.html', '书籍 | Javvin 公司',
                  'Javvin 公司出版的图书 — 董洁林作品，包括《欲望的力量：人类科技创新简史》。',
                  '书籍 | Javvin 公司'),
        'posters': ('posters.html', '网络协议全景图 — 电子图谱 | Javvin 公司',
                    '《网络协议全景图》（2009 经典版·2026 修订）— Javvin 公司电子图谱：高清 PDF，购买后下载，自行打印装裱。', '网络协议全景图 — 电子图谱 | Javvin 公司'),
        'articles': ('articles.html', '文章与推荐序 — 薛澜、阎焱、孙小淳 | Javvin 公司',
                     '《欲望的力量：人类科技创新简史》第二版前言，以及薛澜、阎焱、孙小淳为本书撰写的三篇推荐序全文。', 'Javvin 公司 — 文章与推荐序'),
        'serial': ('serial-power-of-desire.html', '《欲望的力量》连载总索引 | Javvin 公司',
                   '《欲望的力量：人类科技创新简史》全书连载总索引：前言、开篇、二十四章、结语、附录。', '《欲望的力量》连载总索引 | Javvin 公司'),
        'about': ('about.html', '关于 Javvin 公司 — AI 原生出版社（旧金山）',
                  'Javvin 公司是一家位于美国旧金山的 AI 原生出版社，专注于出版科技创新主题的图书与图谱；从编辑、设计到制作、营销与运营，人工智能支持公司工作的每一个环节。', 'Javvin 公司 — 关于'),
        'for-authors': ('for-authors.html', '在 Javvin 出版 — 作者投稿 | Javvin 公司',
                        '在 Javvin 出版。你的知识。你的经验。你的故事。一本值得分享的书。Javvin 欢迎科学家、工程师、研究人员、教育工作者以及其他专业人士投稿。', '在 Javvin 出版 | Javvin 公司'),
        'affiliates': ('affiliates.html', '成为 Javvin 分销伙伴 | Javvin 公司',
                        '推荐 Javvin 图书与电子图谱可获得 30% 佣金：网络协议全景图、欲望的力量电子书、Network Protocols Handbook 电子书。', '成为 Javvin 分销伙伴 | Javvin 公司'),
    },
}


KEYWORDS = {
    'en': {
        'home': 'Javvin Company, The Power of Desire, history of technological innovation, history of innovation, Jielin Dong, science and technology history, ebook',
        'books': 'Javvin Company books, Jielin Dong books, history of innovation books, ebooks',
        'posters': 'Network Protocols Map, network protocols poster, TCP/IP poster, OSI model, digital poster PDF, printable wall chart, Javvin',
        'articles': 'Xue Lan, Yan Yan, Sun Xiaochun, foreword, book review, The Power of Desire, history of innovation, Javvin Company',
        'serial': 'The Power of Desire serialization, read The Power of Desire online, Jielin Dong, history of innovation, book serialization',
        'about': 'Javvin Company, AI-native publisher, independent publisher, San Francisco publisher, Jielin Dong, books on technological innovation',
        'for-authors': 'For Authors, publish with Javvin, book proposal, submit a book proposal, Javvin Company, nonfiction publisher, technology books, professional handbooks, science books, innovation books, biographies, memoirs, author submissions, manuscript proposal, independent publisher, San Francisco publisher',
        'affiliates': 'Javvin affiliate, affiliate program, earn commission, recommend books, Network Protocols Map, digital poster, ebook affiliate, Javvin Company',
    },
    'zh': {
        'home': 'Javvin公司, 欲望的力量, 人类科技创新简史, 董洁林, 科技创新史, 科技史, 电子书',
        'books': 'Javvin公司图书, 董洁林图书, 科技创新史, 电子书',
        'posters': '网络协议全景图, 网络协议图, TCP/IP, OSI模型, 电子图谱, 知识图谱, PDF下载打印, Javvin',
        'articles': '薛澜, 阎焱, 孙小淳, 推荐序, 书评, 欲望的力量, 人类科技创新简史, 科技创新史',
        'serial': '欲望的力量连载, 欲望的力量在线阅读, 董洁林, 科技创新史, 连载总索引',
        'about': 'Javvin公司, AI原生出版社, 独立出版社, 旧金山出版社, 董洁林, 科技创新图书',
        'for-authors': '作者投稿, 在 Javvin 出版, 图书提案, 提交图书提案, Javvin公司, 非虚构出版, 科技图书, 专业手册, 科学图书, 创新图书, 传记, 回忆录, 手稿提案, 独立出版社, 旧金山出版社',
        'affiliates': 'Javvin分销, 分销伙伴, 推广佣金, 推荐图书, 网络协议全景图, 电子图谱, 电子书分销, Javvin公司',
    },
}

# slug, page title (h1), byline, one-sentence guide, author short name, keywords
ARTICLES = {
    'en': [
        ('tsung-dao-lee-at-100', 'Tsung-Dao Lee at 100: In Pursuit of Science, Dancing Across Boundaries',
         'Jielin Dong',
         'On the centennial of Tsung-Dao Lee\'s birth, his CUSPEA student remembers a physicist who danced across boundaries — from parity nonconservation to the Beijing Electron-Positron Collider and the Internet in China.',
         'Jielin Dong', 'Tsung-Dao Lee, T. D. Lee, Li Zhengdao, Lee centennial, CUSPEA, parity nonconservation, Lee-Yang theorem, Lee model, Beijing Electron-Positron Collider, RHIC, Jielin Dong, history of physics'),
        ('preface', 'Preface to the English Edition',
         'Jielin Dong',
         'Preface to the first English edition of The Power of Desire: why humans innovate, how innovation changes life, and what the second edition adds.',
         'Jielin Dong', 'The Power of Desire preface, preface to the English edition, Jielin Dong, history of innovation, history of scientific innovation, Maslow needs innovation, three revolutions, Subsistence Revolution, Communication Revolution, Efficiency Revolution, artificial intelligence, superintelligence, second edition'),
        ('handbook-preface', 'Preface to the Fifth Edition',
         'Jielin Dong',
         'Preface to the fifth edition of Network Protocols Handbook: why the book is reorganized around how communication works, who it is for, and how to use it as a reference.',
         'Jielin Dong', 'Network Protocols Handbook preface, preface to the fifth edition, Jielin Dong, network protocols, how communication works, AI applications, TCP, QUIC, HTTP, fifth edition, Javvin'),
        ('xue-lan', 'A Small Boat on the Great River of Human Innovation',
         'Xue Lan (Professor at Tsinghua University and Dean of Schwarzman College, Tsinghua University)',
         'Tsinghua scholar Xue Lan on how the book retells the history of innovation — human needs as its thread, vivid stories and rigorous data as its method.',
         'Xue Lan', 'Xue Lan, Tsinghua University, Schwarzman College, foreword, history of innovation, The Power of Desire, Jielin Dong, human needs, history of science and technology, innovation history, Maslow, Needham Question, second edition, book foreword, innovation studies, China innovation, artificial intelligence and innovation, incremental innovation, major breakthroughs'),
        ('yan-yan', 'A Minority Voice Worth Cherishing in the Landscape of Ideas',
         'Yan Yan (Founding Managing Partner of SAIF Partners)',
         'Investor Yan Yan on incremental innovation versus major breakthroughs and the coming AI revolution — and why this book is a minority voice worth cherishing.',
         'Yan Yan', 'Yan Yan, SAIF Partners, incremental innovation, major breakthroughs, artificial intelligence, foreword, The Power of Desire, venture capital, investment, innovation ecosystem, AI revolution, technology investment, entrepreneurship, disruptive innovation, China technology, book foreword, second edition'),
        ('sun-xiaochun', 'Why Do Humans Innovate',
         'Sun Xiaochun (Professor, School of Humanities, University of Chinese Academy of Sciences; Former President of the Chinese Society for the History of Science and Technology)',
         'Historian of science Sun Xiaochun on the book\'s grand thought experiment — needs as warp, innovation as weft — and on an author who keeps revising her own views.',
         'Sun Xiaochun', 'Sun Xiaochun, history of science and technology, human needs, technological innovation, foreword, The Power of Desire, history of science, Chinese Academy of Sciences, needs-based innovation, innovation classification, science and technology achievements, book foreword, second edition'),
        ('us-china-ai-battle', 'The US-China AI Battle: Whose Dividend? Whose Price?',
         'Jielin Dong',
         'Companies, countries, and individuals have different scoreboards, and they are not commensurable.',
         'Jielin Dong', 'The US-China AI Battle, Whose Dividend Whose Price, Jielin Dong, US-China AI competition, AI competition, open weights, open-weight models, AI ecosystem, six-layer AI ecosystem, Harness, AI applications, token prices, token price decline, AI computing power, FP16, EFLOPS, AI chips, NVIDIA, DeepSeek, Qwen, Moonshot AI, Zhipu, Meta, Muse Spark, Anthropic, Hugging Face, OpenRouter, Vercel, AI governance, AI safety, model distillation, AI infrastructure, data centers, AI borders, AI regulation, Economic Observer, AI dividends, AI and jobs, AI productivity, AGI, model consolidation, AI capital, enterprise AI, AI monetization'),
        ('power-of-desire-human-needs-and-the-dynamics-of-innovation', 'Maslow Hierarchy of Needs Innovation',
         'Jielin Dong',
         'Maslow hierarchy of needs innovation: how desires, social needs, and external conditions shape what people create — from the opening of The Power of Desire.',
         'Jielin Dong', 'Maslow hierarchy of needs innovation, The Power of Desire, Jielin Dong, history of innovation, Maslow needs, why humans innovate'),
        ('power-of-desire-six-categories-of-scientific-and-technological-value', 'Six Categories of Technological Value',
         'Jielin Dong',
         'Six categories of technological value, classified by needs — subsistence, security, communication, mobility, efficiency, exploration — from The Power of Desire.',
         'Jielin Dong', 'six categories of technological value, The Power of Desire, Jielin Dong, history of innovation, classification of technology, needs framework'),
        ('power-of-desire-ten-thousand-years-at-the-scientific-and-technological-frontier', 'Ten Thousand Years of Innovation',
         'Jielin Dong',
         'Ten thousand years of innovation: the technological frontier across subsistence, communication, turning-point, and efficiency eras — from The Power of Desire.',
         'Jielin Dong', 'ten thousand years of innovation, The Power of Desire, Jielin Dong, history of innovation, major achievements, technological frontier'),
        ('power-of-desire-three-great-scientific-and-technological-revolutions', 'Three Great Technological Revolutions',
         'Jielin Dong',
         'Three great technological revolutions — subsistence, communication, efficiency — transformed food, knowledge, wealth over ten millennia — The Power of Desire.',
         'Jielin Dong', 'three great technological revolutions, The Power of Desire, Jielin Dong, history of innovation, Subsistence Revolution, Communication Revolution, Efficiency Revolution'),
        ('power-of-desire-population-size-and-scientific-and-technological-innovation', 'Population Size and Technological Innovation',
         'Jielin Dong',
         'Population size and technological innovation: why more people and researchers did not raise per-capita breakthroughs since the 1920s — from The Power of Desire.',
         'Jielin Dong', 'population size and technological innovation, The Power of Desire, Jielin Dong, history of innovation, major firsts, population and innovation'),
        ('power-of-desire-population-size-and-scientific-and-technological-innovation-part-2', 'Structure of Major Innovation',
         'Jielin Dong',
         'Structure of major innovation: major firsts atop a pyramid of incremental improvements; breakthroughs open space for later creation — from The Power of Desire.',
         'Jielin Dong', 'structure of major innovation, The Power of Desire, Jielin Dong, history of innovation, major firsts, incremental innovation, pyramid of innovation'),
        ('power-of-desire-part-2-introduction', 'History of Subsistence Innovation: Introduction',
         'Jielin Dong',
         'History of subsistence innovation: how humans changed how they obtain food and stay warm — leaving Africa, farming, cooking, and textiles — The Power of Desire.',
         'Jielin Dong', 'history of subsistence innovation, The Power of Desire, Jielin Dong, history of innovation, subsistence, agriculture, food and textiles'),
        ('power-of-desire-homo-sapiens-in-a-changing-african-environment', 'Homo sapiens out of Africa: Homo sapiens in a Changing African Environment',
         'Jielin Dong',
         'Homo sapiens out of Africa: glacial cycles reshaped Africa, and Homo sapiens left Africa for the world — from The Power of Desire, Chapter 1.',
         'Jielin Dong', 'Homo sapiens out of Africa, The Power of Desire, Jielin Dong, history of innovation, Homo sapiens origins, Africa, ice ages, EPICA ice core'),
        ('power-of-desire-homo-sapiens-in-a-changing-african-environment-part-2', 'Neanderthals and Homo sapiens: Homo sapiens in a Changing African Environment (continued)',
         'Jielin Dong',
         'Neanderthals and Homo sapiens: after leaving Africa, Homo sapiens met Neanderthals and Denisovans, and tools, language, and storytelling changed how humans lived — from The Power of Desire, Chapter 1.',
         'Jielin Dong', 'Neanderthals and Homo sapiens, The Power of Desire, Jielin Dong, history of innovation, Neanderthals, Denisovans, early human technology, composite tools'),
    ],
    'zh': [
        ('tsung-dao-lee-at-100', '李政道百年：求索科学，跨域起舞',
         '董洁林',
         '李政道诞辰百年之际，追忆这位跨域起舞的物理学家：从宇称不守恒到北京正负电子对撞机，再到互联网进入中国。',
         '董洁林', '李政道, 李政道百年, CUSPEA, 宇称不守恒, 李杨定理, 李模型, 北京正负电子对撞机, 董洁林, 物理学史'),
        ('preface', '第二版前言',
         '董洁林',
         '《欲望的力量：人类科技创新简史》第二版前言：人类为什么创新，创新怎样改变生活，第二版修订了什么。',
         '董洁林', '欲望的力量第二版前言, 第二版前言, 董洁林, 科技创新史, 人类为什么创新, 马斯洛需求理论, 三场大革命, 生存革命, 交流革命, 效率革命, 人工智能, 超级智能, 科技创新史'),
        ('xue-lan', '人类创新历史长河中的一叶轻舟',
         '薛澜（清华大学教授，清华大学苏世民书院院长）',
         '薛澜以创新研究学者的视角，解读本书如何以人类需求为线索、用故事与数据重构万年科技创新史。',
         '薛澜', '薛澜, 清华大学, 苏世民书院, 推荐序, 科技创新史, 欲望的力量, 董洁林, 人类需求, 科技史, 创新史, 马斯洛, 李约瑟问题, 第二版, 创新研究, 中国创新, 人工智能与创新, 渐进式创新, 重大突破'),
        ('yan-yan', '思想谱系里珍贵的少数派声音',
         '阎焱（赛富基金创始管理合伙人）',
         '阎焱从投资人的视角谈渐进式创新与重大突破、人工智能带来的新变革，称本书是思想谱系里珍贵的少数派声音。',
         '阎焱', '阎焱, 赛富基金, 渐进式创新, 重大突破, 人工智能, 推荐序, 欲望的力量, 风险投资, 投资, 创新生态, AI变革, 科技投资, 创业, 颠覆式创新, 中国科技, 第二版'),
        ('sun-xiaochun', '人类为什么要创新——《欲望的力量：人类科技创新简史》第二版推荐序',
         '孙小淳（中国科学院大学人文学院教授，中国科学技术史学会原理事长）',
         '孙小淳以科技史家的眼光，评述本书以需求为经、创新为纬的思想实验与作者不断修正自我的治学态度。',
         '孙小淳', '孙小淳, 科技史, 人类需求, 科技创新, 推荐序, 欲望的力量, 第二版, 中国科学院大学, 需求创新, 创新分类, 科技成就'),
        ('us-china-ai-battle', '中美AI战局：谁的红利？谁的代价？',
         '董洁林',
         '公司、国家与个人各有记分牌，且并不通约。',
         '董洁林', '中美AI战局, 谁的红利谁的代价, 董洁林, 中美AI竞争, AI竞争, 开放权重, 开放权重模型, AI生态, 六层生态, Harness, AI应用, Token价格, Token降价, AI算力, FP16, EFLOPS, AI芯片, 英伟达, NVIDIA, 深度求索, DeepSeek, 千问, Qwen, 月之暗面, 智谱, Meta, Muse Spark, Anthropic, Hugging Face, OpenRouter, Vercel, AI治理, AI安全, 模型蒸馏, AI基础设施, 数据中心, AI疆域, AI监管, 经济观察报, AI红利, AI与就业, 生产率, AGI, 模型整合, AI资本, 企业AI, AI变现'),
        ('power-of-desire-human-needs-and-the-dynamics-of-innovation', '需求创新动力学：人类需求与科技创新的动力',
         '董洁林',
         '需求创新动力学：马斯洛需求理论如何解释科技创新的动力？马斯洛1943年提出生理、安全、归属、尊重、自我实现等需求，后期又延伸到自我超越；人的欲望、社会需求与外部条件怎样共同塑造创造的方向与节奏？本书提出“需求与科技创新动力学”模型，把三者联系起来；科技成果又反过来改变这组关系，形成反馈——《欲望的力量》开篇。',
         '董洁林', '需求创新动力学, 欲望的力量, 董洁林, 科技创新史, 马斯洛需求理论, 人类为什么创新'),
        ('power-of-desire-six-categories-of-scientific-and-technological-value', '科技六类价值：从需求看科技的六类价值',
         '董洁林',
         '科技六类价值：按人类需求为科技分类——生存与温饱、安全与健康、交流与娱乐、机动与灵活、效率与利用、探索与超越六类；同一项成果可能服务于多种需求，按当时最突出的用途确定主要类别；图I-2为分类线索的对应示意，图I-3为各区域人口比例；3170项重大成就的统计框架，如何比较不同时期与地区的创新重点——《欲望的力量》开篇。',
         '董洁林', '科技六类价值, 欲望的力量, 董洁林, 科技创新史, 科技分类, 需求理论'),
        ('power-of-desire-ten-thousand-years-at-the-scientific-and-technological-frontier', '万年科技前沿：科技前沿演进的万年趋势',
         '董洁林',
         '万年科技前沿：过去一万多年，重大科技成就如何累计？图I-4显示累计趋势，增长较快的时段与农业革命、轴心时代、科学革命和工业革命大致相连；生存、交流、转折、效率四个时代怎样交替，数据库含科学条目1138项、技术条目2032项，在六类需求中的分布各不相同；图I-5比较各时期六类成就占比——《欲望的力量》开篇。',
         '董洁林', '万年科技前沿, 欲望的力量, 董洁林, 科技创新史, 重大科技成就, 科技前沿'),
        ('power-of-desire-three-great-scientific-and-technological-revolutions', '三次科技革命：人类的三次科技大革命',
         '董洁林',
         '三次科技革命：生存大革命、交流大革命、效率大革命，分别改变了人类获取食物、积累知识、创造财富的方式；约一万二千年前农业兴起，五千多年前文字出现，十七世纪以来煤炭与蒸汽机打开新阶段；三条主线如何贯穿万年科技史；效率大革命仍在延续：能源转换、新材料和智能机器继续改变生产与工作方式——《欲望的力量》开篇。',
         '董洁林', '三次科技革命, 欲望的力量, 董洁林, 科技创新史, 生存革命, 交流革命, 效率革命'),
        ('power-of-desire-population-size-and-scientific-and-technological-innovation', '人口与科技创新：人口规模与科技创新',
         '董洁林',
         '人口与科技创新：人口越多，重大首创就越多吗？马尔萨斯、熊彼特、索罗、罗默从不同角度讨论人口、知识与增长；图I-8显示人均年均重大首创自二十世纪二十年代后达到高点，此后明显下降；图I-9显示人口超过约20亿后，两者转为负相关；科研投入增加而突破相对减少，促使我们重新思考创新的投入方式——《欲望的力量》开篇。',
         '董洁林', '人口与科技创新, 欲望的力量, 董洁林, 科技创新史, 重大首创, 人口规模'),
        ('power-of-desire-population-size-and-scientific-and-technological-innovation-part-2', '重大创新结构：人口规模与科技创新（续）',
         '董洁林',
         '重大创新结构：重大创新与微创新共同构成科技发展的结构，顶端是数量较少的重大首创，下面是大量改进与应用；重大成就往往具有很长的生命力，并在周围催生密集的后续创新；从创造过程看，有理论、想象出发与从用户、实际问题出发两种方式；重大突破先于人口变化，打开新的生存与发展空间，人口和经济随后扩展——《欲望的力量》开篇。',
         '董洁林', '重大创新结构, 欲望的力量, 董洁林, 科技创新史, 重大首创, 微创新, 创新金字塔'),
        ('power-of-desire-part-2-introduction', '生存温饱创新：必需篇导言',
         '董洁林',
         '生存温饱创新：人类怎样改变获取食物、抵御寒冷的方式？从走出非洲、开垦土地，到烹调食物、纺织衣物，生存与温饱技术扩大了可利用的资源，提高了土地承载人口的能力；约四成生存温饱类重大成就出现于公元前5000年及更早时期，耕作、灌溉与食物加工技术随后数千年继续积累，至公元之初已占约74%——《欲望的力量》第二编导言。',
         '董洁林', '生存温饱创新, 欲望的力量, 董洁林, 科技创新史, 生存与温饱, 农业, 食物与纺织'),
        ('power-of-desire-homo-sapiens-in-a-changing-african-environment', '智人走出非洲：非洲的智人与变化的环境',
         '董洁林',
         '智人走出非洲：冰期与间冰期的交替塑造非洲的环境，智人从东非裂谷走向世界——《欲望的力量》第 1 章。',
         '董洁林', '智人走出非洲, 欲望的力量, 董洁林, 科技创新史, 智人起源, 非洲, 冰期, EPICA冰核'),
        ('power-of-desire-homo-sapiens-in-a-changing-african-environment-part-2', '尼安德特人与智人：非洲的智人与变化的环境（续）',
         '董洁林',
         '尼安德特人与智人：走出非洲后，智人与尼安德特人、丹尼索瓦人相遇并交流基因，石器、复合工具、语言与讲故事的能力逐步发展；表1-1列出早期技术的部分证据——《欲望的力量》第 1 章。',
         '董洁林', '尼安德特人与智人, 欲望的力量, 董洁林, 科技创新史, 尼安德特人, 丹尼索瓦人, 早期人类技术, 复合工具'),
    ],
}

# --- The Power of Desire serialization (2026-11-22) ---
# One data source for the serial index: serial-units.json lists every
# installment in book order (142 rows: 2 forewords + preface + 5 opening
# sections + 6 part intros + 120 chapter sections + 5 conclusion sections +
# 3 appendix sections; long sections split into two installments when
# published, so the finished serial is about 160 pairs). Published rows
# carry 'href'; the rest are plain titles until their article goes live.
# The same data renders both the standalone hub page
# (serial-power-of-desire.html, the SEO landing page) and the serial
# section on the book detail page.
SERIAL_UNITS = _json.loads((ROOT / 'serial-units.json').read_text())

SERIAL_JSONLD = {
    'en': {'@context': 'https://schema.org', '@type': 'CollectionPage',
           'name': 'The Power of Desire — Serialization Index',
           'inLanguage': 'en',
           'about': {'@type': 'Book',
                     'name': 'The Power of Desire: A Brief History of Scientific & Technological Innovation',
                     'author': {'@type': 'Person', 'name': 'Jielin Dong'}}},
    'zh': {'@context': 'https://schema.org', '@type': 'CollectionPage',
           'name': '《欲望的力量》连载总索引',
           'inLanguage': 'zh',
           'about': {'@type': 'Book',
                     'name': '欲望的力量：人类科技创新简史',
                     'author': {'@type': 'Person', 'name': '董洁林'}}},
}

def serial_unit_list(lang, units):
    zh = (lang == 'zh')
    rows = []
    for u in units:
        title = u['zh'] if zh else u['en']
        if u['published']:
            status = '已发布' if zh else 'Published'
            rows.append('<div class="toc-row"><span><a href="%s">%s</a></span><span>%s</span></div>'
                        % (u['href'], title, status))
        else:
            status = '待发布' if zh else 'Coming soon'
            rows.append('<div class="toc-row"><span>%s</span><span>%s</span></div>' % (title, status))
    return '\n'.join(rows)

def serial_index_html(lang):
    zh = (lang == 'zh')
    parts = []
    for u in SERIAL_UNITS:
        if not parts or parts[-1]['id'] != u['part']:
            parts.append({'id': u['part'], 'en': u['part_en'], 'zh': u['part_zh'],
                          'chapters': [], 'units': []})
        p = parts[-1]
        if u['chapter'] is None:
            p['units'].append(u)
        else:
            if not p['chapters'] or p['chapters'][-1]['id'] != u['chapter']:
                p['chapters'].append({'id': u['chapter'], 'en': u['chapter_en'],
                                      'zh': u['chapter_zh'], 'units': []})
            p['chapters'][-1]['units'].append(u)
    out = []
    for p in parts:
        out.append('<div class="serial-part" id="serial-%s">\n<h3>%s</h3>'
                   % (p['id'], p['zh'] if zh else p['en']))
        out.append(serial_unit_list(lang, p['units']))
        for c in p['chapters']:
            out.append('<h4 id="serial-%s">%s</h4>' % (c['id'], c['zh'] if zh else c['en']))
            out.append(serial_unit_list(lang, c['units']))
        out.append('</div>')
    return '\n'.join(out)

def serial_hub_page(lang):
    zh = (lang == 'zh')
    title = '《欲望的力量》连载总索引' if zh else 'The Power of Desire — Serialization Index'
    intro = ('《欲望的力量：人类科技创新简史》（第二版）全文连载。已发布的点开即读，其余陆续发布，每天中、英文各一篇。' if zh
             else 'The Power of Desire: A Brief History of Scientific & Technological Innovation, serialized section by section. Published installments are linked; the rest follow daily, one in English and one in Chinese.')
    return ('<section class="block" id="serial-hub">\n<h1>%s</h1>\n<p>%s</p>\n%s\n</section>\n%s'
            % (title, intro, serial_index_html(lang), bottom_buy(lang)))

def serial_section(lang):
    zh = (lang == 'zh')
    title = '连载' if zh else 'Read the Book Online'
    intro = ('全书一篇一篇连载。已发布的点开即读，其余每天中、英文各一篇陆续发布。' if zh
             else 'The whole book, serialized section by section. Published installments are linked; new ones appear daily, one in English and one in Chinese.')
    return ('<section class="block" id="serial">\n<details class="foreword" open>\n<summary><span>%s</span></summary>\n<div>\n<p>%s</p>\n%s\n</div>\n</details>\n</section>'
            % (title, intro, serial_index_html(lang)))

def toc_href(lang, t):
    if lang == 'en':
        if t.startswith('Preface'): return 'articles-preface.html'
        if t.startswith('Foreword One'): return 'articles-xue-lan.html'
        if t.startswith('Foreword Two'): return 'articles-sun-xiaochun.html'
        m = re.match(r'Chapter (\d+)', t)
        if m: return '#serial-ch%02d' % int(m.group(1))
        if t.startswith('VIII Conclusion'): return '#serial-conclusion'
        if t.startswith('Appendix'): return '#serial-appendix'
        m = re.match(r'^([IV]+) ', t)
        if m:
            return '#serial-part%d' % {'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5, 'VI': 6, 'VII': 7}[m.group(1)]
        return None
    if t.startswith('第二版前言'): return 'articles-preface.html'
    if t.startswith('推荐序一'): return 'articles-xue-lan.html'
    if t.startswith('推荐序二'): return 'articles-sun-xiaochun.html'
    m = re.match(r'第(\d+) 章', t)
    if m: return '#serial-ch%02d' % int(m.group(1))
    if t.startswith('VIII 结语'): return '#serial-conclusion'
    if t.startswith('附录'): return '#serial-appendix'
    m = re.match(r'^([IV]+) ', t)
    if m:
        return '#serial-part%d' % {'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5, 'VI': 6, 'VII': 7}[m.group(1)]
    return None

# Serialization articles carry their book's cover right under the title, so a
# reader arriving from search knows at a glance which book the installment
# belongs to (2026-11-22, her rule). Standalone articles (e.g.
# us-china-ai-battle) get no cover. Future serial units use slugs starting
# with 'power-of-desire-' or 'handbook-', so they pick up the cover
# automatically. The cover links to the book detail page.
def article_cover(lang, slug):
    zh = (lang == 'zh')
    if slug.startswith('handbook-'):
        return ('<figure class="cover-fig article-cover">\n'
                '<a href="books-network-protocols-handbook.html"><img loading="lazy" src="../assets/covers/handbook-front.jpg" alt="Cover of Network Protocols Handbook, Fifth Edition"/></a>\n'
                '<figcaption><a href="books-network-protocols-handbook.html">Network Protocols Handbook</a></figcaption>\n</figure>')
    if slug in ('preface', 'xue-lan', 'yan-yan', 'sun-xiaochun') or slug.startswith('power-of-desire-'):
        if zh:
            return ('<figure class="cover-fig article-cover">\n'
                    '<a href="books-power-of-desire.html"><img loading="lazy" src="../assets/covers/cover-front.jpg" alt="《欲望的力量：人类科技创新简史》第二版封面"/></a>\n'
                    '<figcaption><a href="books-power-of-desire.html">《欲望的力量》</a></figcaption>\n</figure>')
        return ('<figure class="cover-fig article-cover">\n'
                '<a href="books-power-of-desire.html"><img loading="lazy" src="../assets/covers/cover-en-front.jpg" alt="Cover of The Power of Desire, second edition"/></a>\n'
                '<figcaption><a href="books-power-of-desire.html">The Power of Desire</a></figcaption>\n</figure>')
    return ''

def articles_index(lang):
    zh = (lang == 'zh')
    h2 = '文章' if zh else 'Articles'
    hub = ('<p>全书连载总索引：<a href="serial-power-of-desire.html">《欲望的力量》连载总索引 →</a></p>' if zh
           else '<p>Read the whole book online: <a href="serial-power-of-desire.html">The Power of Desire — Serialization Index →</a></p>')
    return ('<section class="block" id="articles">\n<h2>%s</h2>\n%s\n<div class="art-list">\n%s\n</div>\n</section>'
            % (h2, hub, art_cards(lang)))

def article_jsonld(lang, art, fname):
    slug, title, _b, guide, author, _k = art
    return {'@context': 'https://schema.org', '@type': 'Article',
            'headline': title,
            'author': {'@type': 'Person', 'name': author},
            'publisher': {'@type': 'Organization', 'name': 'Javvin Company'},
            'inLanguage': lang, 'description': guide,
            'mainEntityOfPage': BASE + lang + '/' + fname,
            'about': ({'@type': 'Thing', 'name': ('中美AI竞争' if lang == 'zh' else 'US-China AI competition')}
                      if slug == 'us-china-ai-battle' else
                      ({'@type': 'Person', 'name': ('李政道' if lang == 'zh' else 'Tsung-Dao Lee')}
                       if slug == 'tsung-dao-lee-at-100' else
                       {'@type': 'Book',
                        'name': ('Network Protocols Handbook' if slug == 'handbook-preface' else
                                 ('欲望的力量：人类科技创新简史' if lang == 'zh'
                                  else 'The Power of Desire: A Brief History of Scientific & Technological Innovation'))}))}


def art_cards(lang):
    zh = (lang == 'zh')
    items = []
    for slug, title, byline, guide, _a, _k in ARTICLES[lang]:
        more = '阅读全文 →' if zh else 'Read the full article →'
        items.append('<a class="art-card" href="articles-%s.html"><h3>%s</h3>'
                     '<p class="byline">%s</p><p class="art-guide">%s</p>'
                     '<span class="art-more">%s</span></a>' % (slug, title, byline, guide, more))
    return '\n'.join(items)

# slug, card title, card subline, cover, cover alt, price, buy url, buy label,
# detail-link label, detail page title, detail description, detail og title, keywords
# (the slug is shared across languages so the language switch links match)
BOOKS = {
    'en': [
        ('power-of-desire',
         'The Power of Desire',
         'A Brief History of Scientific &amp; Technological Innovation, by Jielin Dong · Ebook (PDF), second edition; print edition by print-on-demand.',
         '../assets/covers/cover-en-front.jpg', 'Cover of The Power of Desire, second edition',
         '$12.99', 'https://payhip.com/b/LdW15', 'Buy the eBook · $12.99', 'https://www.amazon.com/dp/1602670315', 'Buy the Paperback · $29.99', 'Details →',
         'The Power of Desire — The Book | Javvin Company', EN_BOOK_DESC,
         'Javvin Company — The Power of Desire: A Brief History of Scientific &amp; Technological Innovation',
         'The Power of Desire, Jielin Dong, history of innovation, history of technological innovation, human needs, ebook PDF, ISBN 9781602670310'),
        ('network-protocols-handbook',
         'Network Protocols Handbook',
         'Understanding Connectivity Across the Internet, Cloud, and AI Systems, by Jielin Dong · Fifth Edition · January 2027',
         '../assets/covers/handbook-front.jpg', 'Cover of Network Protocols Handbook, Fifth Edition',
         '$24.95', 'https://payhip.com/b/rG6sm', 'Buy the eBook · $24.95', 'https://www.amazon.com/dp/1602670323', 'Buy the Paperback · $49.99', 'Details →',
         'Network Protocols Handbook, Fifth Edition — Jielin Dong | Javvin Company',
         'Network Protocols Handbook, Fifth Edition follows a request from a device to a cloud service or an AI data center and back, and explains the protocols at each step: Ethernet, Wi-Fi, IP, routing, and DNS; TCP, QUIC, and HTTP; encryption and identity; container and cloud networks.',
         'Javvin Company — Network Protocols Handbook, Fifth Edition',
         'Network Protocols Handbook, fifth edition, Ethernet, Wi-Fi, IP, routing, DNS, TCP, QUIC, HTTP, MCP, A2A, RDMA, Ultra Ethernet, Jielin Dong, ISBN 9781602670327'),
    ],
    'zh': [
        ('power-of-desire',
         '《欲望的力量：人类科技创新简史》（第二版）',
         '董洁林著 · 电子书（PDF），本站购买后下载；纸质版按需印刷。',
         '../assets/covers/cover-front.jpg', '《欲望的力量：人类科技创新简史》第二版封面',
         '$12.99', 'https://payhip.com/b/ioAfP', '购买电子书 · $12.99', '', '', '详细介绍 →',
         '《欲望的力量：人类科技创新简史》（第二版）— 董洁林 | Javvin 公司', ZH_BOOK_DESC,
         'Javvin 公司 — 《欲望的力量：人类科技创新简史》（第二版）',
         '欲望的力量, 人类科技创新简史, 董洁林, 第二版, 科技创新史, 人类需求, 电子书PDF, ISBN 9781602670303'),
    ],
}

def book_cards(lang):
    items = []
    for (slug, title, sub, cover, alt, price, buy, buy_label, pb, pb_label, more,
         _dt, _dd, _og, _kw) in BOOKS[lang]:
        buy_html = ('<a class="buy-btn" href="%s" rel="noopener" target="_blank"><span>%s</span></a>'
                    % (buy, buy_label)) if buy else ''
        if pb:
            buy_html += ('<a class="buy-btn" href="%s" rel="noopener" target="_blank"><span>%s</span></a>'
                         % (pb, pb_label))
        items.append(
            '<div class="prod-card"><a href="books-%s.html"><img loading="lazy" class="prod-img book" src="%s" alt="%s"/></a>'
            '<h3>%s</h3>'
            '<p class="prod-sub">%s</p>'
            '<div class="prod-actions">%s'
            '<a class="detail-link" href="books-%s.html">%s</a></div></div>'
            % (slug, cover, alt, title, sub, buy_html, slug, more))
    return ''.join(items)

def books_index(lang):
    h2 = '书籍' if lang == 'zh' else 'Books'
    return ('<section class="block" id="books"><h2>%s</h2><div class="prod-grid">%s</div></section>'
            % (h2, book_cards(lang)))

def products_block(lang):
    if lang == 'zh':
        return ('<section class="block" id="products">\n<h2>作品</h2>\n<div class="prod-grid">\n'
                '<div class="prod-card"><img loading="lazy" class="prod-img book" src="../assets/covers/cover-front.jpg" alt="《欲望的力量：人类科技创新简史》第二版封面"/>'
                '<h3>《欲望的力量：人类科技创新简史》（第二版）</h3>'
                '<p class="prod-sub">董洁林著 · 电子书（PDF），本站购买后下载；纸质版按需印刷。</p>'
                '<div class="prod-actions"><a class="buy-btn" href="https://payhip.com/b/ioAfP" rel="noopener" target="_blank"><span>购买电子书 · $12.99</span></a>'
                '<a class="detail-link" href="books-power-of-desire.html">详细介绍 →</a></div></div>\n'
                '<div class="prod-card"><img loading="lazy" class="prod-img poster" src="../assets/posters/network-protocols-map-promo.jpg" alt="网络协议全景图"/>'
                '<h3>网络协议全景图</h3>'
                '<p class="prod-sub">Network Protocols Map · 电子图谱（PDF），2009 经典版 · 2026 修订，横版 36×24 英寸，自行打印装裱。</p>'
                '<div class="prod-actions"><a class="buy-btn" href="https://payhip.com/b/xO3uf" rel="noopener" target="_blank"><span>购买图谱 · $19.99</span></a>'
                '<a class="detail-link" href="posters.html">详细介绍 →</a></div></div>\n'
                '</div>\n</section>')
    return ('<section class="block" id="products">\n<h2>Publications</h2>\n<div class="prod-grid">\n'
            '<div class="prod-card"><img loading="lazy" class="prod-img book" src="../assets/covers/cover-en-front.jpg" alt="Cover of The Power of Desire, second edition"/>'
            '<h3>The Power of Desire</h3>'
            '<p class="prod-sub">A Brief History of Scientific &amp; Technological Innovation, by Jielin Dong · Ebook (PDF), second edition; print edition by print-on-demand.</p>'
            '<div class="prod-actions"><a class="buy-btn" href="https://payhip.com/b/LdW15" rel="noopener" target="_blank"><span>Buy the eBook · $12.99</span></a><a class="buy-btn" href="https://www.amazon.com/dp/1602670315" rel="noopener" target="_blank"><span>Buy the Paperback · $29.99</span></a>'
            '<a class="detail-link" href="books-power-of-desire.html">Details →</a></div></div>\n'
            '<div class="prod-card"><img loading="lazy" class="prod-img book" src="../assets/covers/handbook-front.jpg" alt="Cover of Network Protocols Handbook, Fifth Edition"/>'
            '<h3>Network Protocols Handbook</h3>'
            '<p class="prod-sub">Understanding Connectivity Across the Internet, Cloud, and AI Systems, by Jielin Dong · Fifth Edition · January 2027</p>'
            '<div class="prod-actions"><a class="buy-btn" href="https://payhip.com/b/rG6sm" rel="noopener" target="_blank"><span>Buy the eBook · $24.95</span></a><a class="buy-btn" href="https://www.amazon.com/dp/1602670323" rel="noopener" target="_blank"><span>Buy the Paperback · $49.99</span></a>'
            '<a class="detail-link" href="books-network-protocols-handbook.html">Details →</a></div></div>\n'
            '<div class="prod-card"><img loading="lazy" class="prod-img poster" src="../assets/posters/network-protocols-map-promo.jpg" alt="Network Protocols Map"/>'
            '<h3>Network Protocols Map</h3>'
            '<p class="prod-sub">Digital poster (PDF) — 2009 classic, revised 2026 · 36×24 in, download and print it yourself.</p>'
            '<div class="prod-actions"><a class="buy-btn" href="https://payhip.com/b/xO3uf" rel="noopener" target="_blank"><span>Buy the Poster · $19.99</span></a>'
            '<a class="detail-link" href="posters.html">Details →</a></div></div>\n'
            '</div>\n</section>')

def home_articles(lang):
    zh = (lang == 'zh')
    h2 = '文章与推荐序' if zh else 'Articles'
    return ('<section class="block" id="home-articles">\n<h2>%s</h2>\n<div class="art-list">\n%s\n</div>\n</section>'
            % (h2, art_cards(lang)))

def for_authors_body(lang):
    mailto = 'mailto:help@javvin.ai?subject=Book%20Proposal%20%E2%80%94%20'
    if lang == 'en':
        return '''<section class="block" id="for-authors">
<h1>Publish with Javvin</h1>
<p class="article-deck">Your knowledge. Your experience. Your story. A book worth sharing.</p>
<p>You may have spent years solving difficult problems, developing new ideas, or building a career others could learn from. Perhaps you have a life story that deserves to be recorded.</p>
<p>Javvin welcomes proposals from scientists, engineers, researchers, educators, and other professionals. We seek nonfiction that makes specialized knowledge accessible, offers a useful perspective, or preserves the experiences behind meaningful work.</p>
<p><a class="buy-btn" href="MAILTO"><span>Submit a Book Proposal</span></a></p>
<h2>Books We Welcome</h2>
<h3>Technology and professional knowledge</h3>
<p>Practical guides, handbooks, and educational books covering computing, networking, cybersecurity, artificial intelligence, engineering, and other professional fields.</p>
<h3>Science, technology, and innovation</h3>
<p>Books exploring discoveries, inventions, technological change, and their effects on business and society.</p>
<h3>Biographies and memoirs</h3>
<p>The lives and careers of scientists, engineers, entrepreneurs, educators, and other professionals—including people whose contributions deserve wider recognition. We welcome personal memoirs and biographies written by others, with appropriate attention to sources, permissions, and privacy.</p>
<p class="welcome-close">Your proposal may be a specialist reference, an accessible introduction, a career memoir, or a deeply researched life story. We value a clear purpose, a defined readership, and an author with something substantive to share.</p>
<h2>An Author's Perspective on Publishing</h2>
<p>A strong book requires careful choices: what to include, how to organize it, which details to verify, and how to keep readers engaged without losing the author's voice.</p>
<p>Javvin understands these challenges through its own publishing work. Our Network Protocols Handbook, first published in 2004 and now in its fifth edition, reflects a sustained commitment to making complex knowledge useful to readers.</p>
<p>We bring that same attention to clarity, accuracy, and thoughtful presentation when considering new projects.</p>
<h2>A Publishing Plan for Your Project</h2>
<p>Every book has different needs. For selected proposals, we discuss the manuscript's readiness, intended audience, editorial requirements, design, publication formats, and distribution goals.</p>
<p>Publishing services, fees, and commercial terms are negotiated individually for each project. Any author contribution, allocation of responsibilities, rights, and revenue arrangements will be set out in a written agreement before work begins.</p>
<h2>Share Your Proposal</h2>
<p>You do not need a completed manuscript to contact us. Please send:</p>
<ul>
<li>A brief description of your book and its intended readers.</li>
<li>A proposed table of contents or chapter outline.</li>
<li>A sample chapter or representative writing sample.</li>
<li>A short biography explaining your connection to the subject.</li>
<li>The manuscript's current status, approximate length, and expected completion date.</li>
</ul>
<p>For a biography or memoir, please also describe the principal subject, the materials available, and your relationship to the people whose stories you plan to tell.</p>
<h2>Let's Discuss Your Book</h2>
<p>Send your proposal to <a href="mailto:help@javvin.ai">help@javvin.ai</a>.</p>
<p>Email subject: Book Proposal — [Your Book Title]</p>
<p><a class="buy-btn" href="MAILTO"><span>Submit a Book Proposal</span></a></p>
</section>'''.replace('MAILTO', mailto)
    return '''<section class="block" id="for-authors">
<h1>在 Javvin 出版</h1>
<p class="article-deck">你的知识。你的经验。你的故事。一本值得分享的书。</p>
<p>你可能花了多年时间解决难题、提出新想法，或者积累了一番值得他人借鉴的职业生涯。也许，你有一段值得记录的人生故事。</p>
<p>Javvin 欢迎科学家、工程师、研究人员、教育工作者以及其他专业人士投稿。我们寻找这样的非虚构作品：让专业知识变得易于理解，提供有用的视角，或者保存有意义的工作背后的经验。</p>
<p><a class="buy-btn" href="MAILTO"><span>提交图书提案</span></a></p>
<h2>我们欢迎的图书</h2>
<h3>技术与专业知识</h3>
<p>涵盖计算机、网络、网络安全、人工智能、工程及其他专业领域的实用指南、手册和教材。</p>
<h3>科学与技术创新</h3>
<p>探讨发现、发明、技术变革及其对商业和社会影响的图书。</p>
<h3>传记与回忆录</h3>
<p>科学家、工程师、企业家、教育工作者及其他专业人士的人生与职业生涯——包括那些贡献值得更广泛认可的人物。我们欢迎个人回忆录，也欢迎由他人撰写的传记，同时会恰当注意资料来源、授权与隐私。</p>
<p class="welcome-close">你的提案可以是一部专业参考书、一本通俗易懂的入门书、一部职业回忆录，或者一部经过深入研究的人生故事。我们看重明确的写作目的、清晰的读者定位，以及言之有物的作者。</p>
<h2>从作者的角度看出版</h2>
<p>一本好书需要谨慎的取舍：收录什么、如何组织、核实哪些细节，以及如何在不丢失作者声音的前提下吸引读者。</p>
<p>Javvin 通过自身的出版工作理解这些挑战。我们的《Network Protocols Handbook》首版于 2004 年，现已出至第五版，体现了我们长期以来致力于让复杂知识对读者真正有用的承诺。</p>
<p>在考虑新项目时，我们同样注重清晰、准确和用心的呈现。</p>
<h2>为你的项目制订出版计划</h2>
<p>每本书的需求各不相同。对于入选的提案，我们会讨论稿件的完成程度、目标读者、编辑要求、设计、出版形式和发行目标。</p>
<p>出版服务、费用和商业条款按每个项目单独协商。任何作者出资、责任分工、权利和收益安排，都会在工作开始前以书面协议明确。</p>
<h2>分享你的提案</h2>
<p>联系我们不需要已经完成的手稿。请发送：</p>
<ul>
<li>图书简介及其目标读者。</li>
<li>拟定的目录或章节大纲。</li>
<li>样章或有代表性的写作样本。</li>
<li>简短的个人简介，说明你与主题的关联。</li>
<li>稿件目前的进度、大致篇幅和预计完成日期。</li>
</ul>
<p>如果是传记或回忆录，还请介绍主要人物、现有的资料，以及你与打算讲述其故事的人物之间的关系。</p>
<h2>来谈谈你的书</h2>
<p>请把提案发送至 <a href="mailto:help@javvin.ai">help@javvin.ai</a>。</p>
<p>邮件主题：Book Proposal — [你的书名]</p>
<p><a class="buy-btn" href="MAILTO"><span>提交图书提案</span></a></p>
</section>'''.replace('MAILTO', mailto)
def affiliates_body(lang):
    signup = 'https://payhip.com/auth/register/af6abecfbbf0cd5'
    if lang == 'en':
        return '''<section class="block" id="affiliates">
<h1>Become a Javvin Affiliate</h1>
<p class="article-deck">Recommend books and posters your audience will actually use — and earn 30% on every sale you refer.</p>
<p>Javvin Company publishes books and digital posters on networking, technology, and the history of innovation. If you teach, write, or talk to people who learn this material, you can earn by recommending work you trust.</p>
<p><a class="buy-btn" href="SIGNUP" rel="noopener" target="_blank"><span>Apply as an Affiliate</span></a></p>
<h2>What You Can Promote</h2>
<h3>Network Protocols Map — digital poster (PDF, 36 × 24 in), $19.99</h3>
<p>A wall chart of the protocols behind connected systems, from the 2009 classic, revised 2026. Buyers download the file and print it themselves.</p>
<h3>The Power of Desire — ebook (PDF), $12.99</h3>
<p>A brief history of scientific and technological innovation, available in English and Chinese editions.</p>
<h3>Network Protocols Handbook, fifth edition — ebook (PDF), $24.95</h3>
<p>Understanding connectivity across the Internet, cloud, and AI systems. English edition.</p>
<h2>How It Works</h2>
<p>1. Apply with the link on this page. We will approve your application and assign the products.</p>
<p>2. Share your tracked links with your audience — on your site, in your course, in your newsletter, or on social media.</p>
<p>3. Earn 30% of every sale made through your links. Tracking lasts 30 days, with credit to the last link clicked.</p>
<h2>Payments</h2>
<p>Commissions are paid monthly via PayPal, based on Payhip's monthly affiliate report.</p>
<h2>Please Note</h2>
<p>Buyers purchase from Javvin's store, and our standard license terms apply to them: a poster purchase may be printed in up to 2 copies and displayed in one location; ebooks are for the buyer's own reading on their own devices; files may not be shared, forwarded, uploaded, or resold. Affiliates refer buyers — they do not receive files to sell onward.</p>
<p><a class="buy-btn" href="SIGNUP" rel="noopener" target="_blank"><span>Apply as an Affiliate</span></a></p>
<h2>Questions?</h2>
<p>Contact us at <a href="mailto:help@javvin.ai">help@javvin.ai</a>.</p>
</section>'''.replace('SIGNUP', signup)
    return '''<section class="block" id="affiliates">
<h1>成为 Javvin 分销伙伴</h1>
<p class="article-deck">推荐你真正信任的图书与图谱，每一笔你带来的销售，你可获得 30% 佣金。</p>
<p>Javvin 公司出版网络、技术与创新史主题的图书与电子图谱。如果你面向学习这些内容的人群授课、写作或分享，推荐值得信任的作品即可获得收益。</p>
<p><a class="buy-btn" href="SIGNUP" rel="noopener" target="_blank"><span>申请成为分销伙伴</span></a></p>
<h2>可推广的产品</h2>
<h3>网络协议全景图 — 电子图谱（PDF，36 × 24 英寸），$19.99</h3>
<p>呈现联网系统背后协议的全景图，源自 2009 经典版、2026 修订。买家下载文件后自行打印。</p>
<h3>《欲望的力量》— 电子书（PDF），$12.99</h3>
<p>人类科技创新简史，有英文版与中文版。</p>
<h3>Network Protocols Handbook（第五版）— 电子书（PDF），$24.95</h3>
<p>理解互联网、云与 AI 系统的连通性。英文版。</p>
<h2>如何运作</h2>
<p>1. 通过本页链接申请。我们批准申请后，会为你开通可推广的产品。</p>
<p>2. 把你的专属推广链接分享给受众——你的网站、课程、 newsletter 或社交媒体均可。</p>
<p>3. 通过你的链接产生的每一笔销售，你可获得 30% 佣金。追踪有效期 30 天，以最后一次点击为准。</p>
<h2>佣金结算</h2>
<p>佣金按月通过 PayPal 支付，以 Payhip 的月度分销报告为准。</p>
<h2>请注意</h2>
<p>买家在 Javvin 店铺购买，适用我们的标准授权条款：图谱每购可打印最多 2 份、展示于一处；电子书限购买者本人在本人设备上阅读；文件不得分享、转传、上传或转售。分销伙伴负责引荐买家，不会直接拿到文件去销售。</p>
<p><a class="buy-btn" href="SIGNUP" rel="noopener" target="_blank"><span>申请成为分销伙伴</span></a></p>
<h2>有问题？</h2>
<p>请联系 <a href="mailto:help@javvin.ai">help@javvin.ai</a>。</p>
</section>'''.replace('SIGNUP', signup)


def build(lang, out_dir):
    zh = (lang == 'zh')
    home = zh_home if zh else en_home
    hero_html = hero(home)
    hero_html = re.sub(r'\n?<span class="nr-badge">[^<]*</span>', '', hero_html)
    badge_txt = '最新发布' if zh else 'New Release'
    hero_html = hero_html.replace('<div class="hero-text">',
                                  '<div class="hero-text">\n<span class="nr-badge">%s</span>' % badge_txt, 1)
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
    hero_html = hero_html.replace(explore, explore.replace('books.html', 'books-power-of-desire.html') + sample_btn, 1)
    # visible ISBN line in the hero meta list (strip earlier injected lines first)
    hero_html = re.sub(r'\n?<li><span class="k">ISBN</span>[^<]*</li>', '', hero_html)
    isbn_li = ('<li><span class="k">ISBN</span>978-1-60267-030-3</li>' if zh
               else '<li><span class="k">ISBN</span>978-1-60267-031-0</li>')
    hero_html = hero_html.replace('</ul>', isbn_li + '\n</ul>', 1)
    # author bio section after the book introduction
    if zh:
        bio = ('<section class="block" id="author">\n<h2>作者简介</h2>\n<div class="about-text">\n'
               '<p>董洁林博士是一位学者和作家，研究与写作领域涵盖科学技术史、创新政策和全球科技竞争。她长期为《华尔街日报》和《金融时报》中文版撰稿，已出版五部著作及多篇文章。她也是 Javvin Company（<a href="https://javvin.ai/">Javvin.ai</a>）的创始人。</p>\n'
               '<p>董洁林博士曾在清华大学和苏州大学担任教学与研究职务。在清华大学，她曾任中国科技政策研究中心兼职研究员，以及技术创新研究中心兼职教授、学术委员会委员。在苏州大学，她曾任特聘教授、企业创新与发展研究中心主任。她还曾在朗讯、思科和 Network Associates 等科技公司担任管理职务，并在金融服务机构和科研院所工作。此外，她曾担任多家科技创业公司的董事。</p>\n'
               '<p>董洁林博士于1988年获得美国卡内基梅隆大学物理学博士学位，1982年获得中山大学理学学士学位。她通过竞争激烈的中美联合招考物理研究生项目（CUSPEA）赴美深造。</p>\n'
               '<p><strong>社交媒体</strong><br/>X：<a href="https://x.com/D931931" rel="noopener" target="_blank">@D931931</a> ｜ LinkedIn：<a href="https://www.linkedin.com/in/jielin-dong-04b4b515/" rel="noopener" target="_blank">Jielin Dong</a></p>\n'
               '</div>\n</section>')
    else:
        bio = ('<section class="block" id="author">\n<h2>About the Author</h2>\n<div class="about-text">\n'
               '<p>Dr. Jielin Dong is a scholar and author whose work focuses on the history of science and technology, innovation policy, and global technology competition. A regular contributor to the Chinese editions of The Wall Street Journal and the Financial Times, she has published five books and numerous articles. She is the founder of Javvin Company (<a href="https://javvin.ai/">Javvin.ai</a>).</p>\n'
               '<p>Dr. Dong has held academic and research appointments at Tsinghua University and Soochow University. At Tsinghua, she has served as a part-time research fellow at the China Institute for Science and Technology Policy, and as a part-time professor and academic committee member at the Research Center for Technological Innovation. At Soochow, she has served as a distinguished professor and director of the Center for Enterprise Innovation and Development. Her career also includes management roles at Lucent, Cisco, and Network Associates, as well as positions in financial services and scientific research institutes. She has also served on the boards of several technology startups.</p>\n'
               '<p>Dr. Dong earned her Ph.D. in physics from Carnegie Mellon University in 1988 and her B.S. from Sun Yat-sen University in 1982. She pursued graduate study in the United States through the highly competitive CUSPEA program.</p>\n'
               '<p><strong>Social media</strong><br/>X: <a href="https://x.com/D931931" rel="noopener" target="_blank">@D931931</a> &nbsp;|&nbsp; LinkedIn: <a href="https://www.linkedin.com/in/jielin-dong-04b4b515/" rel="noopener" target="_blank">Jielin Dong</a></p>\n'
               '</div>\n</section>')
    # return policy lives on the About page (moved there 2026-10-21 at her request)
    if zh:
        returns = ('<section class="block" id="returns">\n<h2>退货政策</h2>\n<div class="about-text">\n'
                   '<p>电子产品（电子书与电子图谱）一经交付完成，概不退货退款。本店保证文件成功交付：如下载失败或文件损坏，将免费重新交付。</p>\n'
                   '<p>印刷版采用按需印刷（Print-on-Demand）方式：您下单后，专门为您印制并寄送。如果您从本网站购买的印刷版出现印刷或装订瑕疵、需要退换，请联系 help@javvin.ai。如果您从其他网站或书店购买印刷版，其退换依出售该印刷版之零售商的政策办理。</p>\n'
                   '</div>\n</section>')
    else:
        returns = ('<section class="block" id="returns">\n<h2>Return Policy</h2>\n<div class="about-text">\n'
                   '<p>All sales of digital products (ebooks and digital posters) are final upon completion of delivery; delivered digital products are non-refundable. We guarantee successful delivery of your files — if a download fails or a file is corrupted, we will re-deliver it at no additional charge.</p>\n'
                   '<p>Print editions are produced by print-on-demand: when you place an order, a copy is printed especially for you and shipped to you. If a print copy purchased from this website has printing or binding defects and you need a return or exchange, please contact help@javvin.ai. If you purchased the print edition from another website or bookstore, its return or exchange is governed by the policy of the retailer that sold it.</p>\n'
                   '</div>\n</section>')
    # book-info layout (byline / price+buy+sample / spec line / tagline) is canonical in the source pages
    bodies = {
        'home': hero_html + '\n' + products_block(lang) + '\n' + home_articles(lang) + '\n' + praise_block(lang) + '\n' + footer(home),
        'books': books_index(lang) + footer(home),
        'posters': section(get_page('posters.html', zh), 'posters') + '\n' + footer(home),
        'articles': articles_index(lang) + '\n' + footer(home),
        'serial': serial_hub_page(lang) + '\n' + footer(home),
        'about': section(get_page('about.html', zh), 'about') + '\n' + license_block(lang) + '\n' + returns + '\n' + footer(home),
        'for-authors': for_authors_body(lang) + '\n' + footer(home),
        'affiliates': affiliates_body(lang) + '\n' + footer(home),
    }
    if lang == 'en':
        bodies = {k: v.replace('"assets/', '"../assets/') for k, v in bodies.items()}
    for name, (fname, title, desc, ogt) in META[lang].items():
        jld = SERIAL_JSONLD[lang] if name == 'serial' else None
        hd = head(lang, name, fname, title, desc, ogt, keywords=KEYWORDS[lang][name], jsonld_override=jld)
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
        cover = article_cover(lang, slug)
        if cover:
            frag = frag.replace('</h1>', '</h1>\n' + cover, 1)
        back = ('<p class="back-link"><a href="articles.html">← 返回文章列表</a></p>' if zh
                else '<p class="back-link"><a href="articles.html">← Back to Articles</a></p>')
        body = ('<section class="block article-page" id="article">\n%s\n%s\n</section>\n%s'
                % (frag, back, footer(home)))
        if lang == 'en':
            body = body.replace('"assets/', '"../assets/')
        t = ('%s — %s | Javvin 公司' % (atitle, author)) if zh else ('%s — %s | Javvin Company' % (atitle, author))
        hd = head(lang, 'article', fname, t, guide, t, keywords=akw,
                  jsonld_override=article_jsonld(lang, art, fname))
        body_attr = ' class="en"' if lang == 'en' else ''
        html = ('<!DOCTYPE html>\n<html lang="%s">\n%s\n<body%s>\n%s\n%s\n</body>\n</html>\n'
                % ('en' if lang == 'en' else 'zh-CN', hd, body_attr,
                   header(lang, 'article', fname), body))
        if slug == 'handbook-preface':
            # English-only book (same as the handbook detail page): point the
            # language switch at the Chinese Articles list and drop the zh alternate.
            html = html.replace('<a href="/zh/articles-handbook-preface.html">中文</a>',
                                '<a href="/zh/articles.html">中文</a>')
            html = html.replace('<link href="https://javvin.ai/zh/articles-handbook-preface.html" hreflang="zh" rel="alternate"/>', '')
        (out_dir / fname).write_text(html)
        print('wrote', out_dir / fname, len(html))

    # standalone book pages (split out of the Books page 2026-10-29 at her request)
    for bk in BOOKS[lang]:
        (slug, _ct, _cs, _cv, _al, _pr, _buy, _bl, _pb, _pbl, _more,
         dtitle, desc, ogt, kw) = bk
        if slug == 'network-protocols-handbook':
            continue  # written by build_handbook_page below (own TOC/bio, no buy)
        fname = 'books-%s.html' % slug
        frag = (ROOT / 'books-src' / ('%s-%s.html' % (lang, slug))).read_text().strip()
        back = ('<p class="back-link"><a href="books.html">← 返回书籍列表</a></p>' if zh
                else '<p class="back-link"><a href="books.html">← Back to Books</a></p>')
        author_alt = '董洁林博士肖像' if zh else 'Portrait of Dr. Jielin Dong'
        bio_html = bio.replace('<div class="about-text">',
            '<div class="author-wrap"><figure class="author-photo"><img loading="lazy" src="../assets/author-jielin-dong.jpg" alt="%s"/></figure><div class="about-text">' % author_alt, 1)
        _head, _sep, _tail = bio_html.rpartition('</div>')
        bio_html = _head + '</div></div>' + _tail
        body = frag + toc_block(lang) + serial_section(lang) + praise_block(lang) + bio_html + bottom_buy(lang) + back + footer(home)
        if lang == 'en':
            body = body.replace('"assets/', '"../assets/')
        hd = head(lang, 'book', fname, dtitle, desc, ogt, keywords=kw,
                  jsonld_override=BOOK_JSONLD[lang])
        body_attr = ' class="en"' if lang == 'en' else ''
        html = '''<!DOCTYPE html>
<html lang="%s">
%s
<body%s>
%s
%s
</body>
</html>
''' % ('en' if lang == 'en' else 'zh-CN', hd, body_attr,
       header(lang, 'book', fname), body)
        if lang == 'en':
            html = html.replace('https://javvin.ai/assets/covers/cover-en-front.jpg',
                                'https://javvin.ai/assets/covers/cover-en-3d.jpg')
        else:
            html = html.replace('https://javvin.ai/assets/covers/cover-front.jpg',
                                'https://javvin.ai/assets/covers/cover-3d.jpg')
        (out_dir / fname).write_text(html)
        print('wrote', out_dir / fname, len(html))

def build_handbook_page():
    # English-only book page (2026-10-30): not built by the detail loop above,
    # which appends the Power of Desire TOC/praise/buy blocks. Its TOC lives
    # in the fragment; its author bio below is the back-cover text; price and
    # buy button live in the fragment (Payhip PDF $24.95, since 2026-10-30).
    fname = 'books-network-protocols-handbook.html'
    frag = (ROOT / 'books-src' / 'en-network-protocols-handbook.html').read_text().strip()
    author_html = ('<section class="block" id="author">\n<h2>About the Author</h2>\n'
        '<div class="author-wrap"><figure class="author-photo"><img loading="lazy" src="../assets/author-jielin-dong.jpg" alt="Portrait of Dr. Jielin Dong"/></figure><div class="about-text">\n'
        '<p>Dr. Jielin Dong’s networking experience includes work at Cisco Systems, Lucent Technologies, and Network Associates. She also served as a professor of the history of science and technology.</p>\n'
        '</div></div>\n</section>')
    back = '<p class="back-link"><a href="books.html">← Back to Books</a></p>'
    body = frag + author_html + back + footer(en_home)
    desc = 'Network Protocols Handbook, Fifth Edition follows a request from a device to a cloud service or an AI data center and back, and explains the protocols at each step: Ethernet, Wi-Fi, IP, routing, and DNS; TCP, QUIC, and HTTP; encryption and identity; container and cloud networks.'
    jsonld = {'@context': 'https://schema.org', '@type': 'Book',
        'name': 'Network Protocols Handbook',
        'bookEdition': 'Fifth Edition',
        'author': {'@type': 'Person', 'name': 'Jielin Dong'},
        'publisher': {'@type': 'Organization', 'name': 'Javvin Company'},
        'inLanguage': 'en', 'isbn': '9781602670327',
        'datePublished': '2027-01', 'numberOfPages': 324,
        'image': BASE + 'assets/covers/handbook-3d.jpg',
        'url': BASE + 'en/books-network-protocols-handbook.html',
        'description': desc,
        'offers': {'@type': 'Offer', 'url': 'https://payhip.com/b/rG6sm',
                   'price': '24.95', 'priceCurrency': 'USD',
                   'availability': 'https://schema.org/InStock', 'category': 'Ebook (PDF)'}}
    hd = head('en', 'book', fname,
              'Network Protocols Handbook, Fifth Edition — Jielin Dong | Javvin Company',
              desc,
              'Javvin Company — Network Protocols Handbook, Fifth Edition',
              keywords='Network Protocols Handbook, fifth edition, Ethernet, Wi-Fi, IP, routing, DNS, TCP, QUIC, HTTP, MCP, A2A, RDMA, Ultra Ethernet, Jielin Dong, ISBN 9781602670327',
              jsonld_override=jsonld)
    html = ('<!DOCTYPE html>\n<html lang="en">\n%s\n<body class="en">\n%s\n%s\n</body>\n</html>\n'
            % (hd, header('en', 'book', fname), body))
    # No Chinese edition yet: point the language switch at the Chinese
    # Books listing, drop the zh alternate, and use the handbook cover art.
    html = html.replace('<a href="/zh/books-network-protocols-handbook.html">中文</a>',
                        '<a href="/zh/books.html">中文</a>')
    html = html.replace('<link href="https://javvin.ai/zh/books-network-protocols-handbook.html" hreflang="zh" rel="alternate"/>', '')
    html = html.replace('https://javvin.ai/assets/covers/cover-en-front.jpg',
                        'https://javvin.ai/assets/covers/handbook-3d.jpg')
    (ROOT / 'en' / fname).write_text(html)
    print('wrote', ROOT / 'en' / fname, len(html))

build('en', ROOT / 'en')
build('zh', ROOT / 'zh')
build_handbook_page()

STUB = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<title>Javvin Company</title>
<link href="https://javvin.ai/en/{seg}" rel="canonical"/>
<meta content="0; url=/en/{seg}" http-equiv="refresh"/>
<meta content="noindex" name="robots"/>
</head>
<body>
<p>This page has moved to <a href="/en/{seg}">Javvin Company (English)</a>.</p>
</body>
</html>
'''
for fname in ['index.html', 'books.html', 'posters.html', 'articles.html', 'about.html', 'for-authors.html', 'affiliates.html']:
    seg = '' if fname == 'index.html' else fname
    (ROOT / fname).write_text(STUB.format(seg=seg))
    print('stub', fname, '-> /en/' + seg)
print('done')
