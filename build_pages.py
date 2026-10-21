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
STYLE = re.sub(r'(\.book-card img \{\s*width: min\()\d+px', r'\g<1>180px', STYLE)
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
        ('Elegant prose, compelling stories, and rigorous analysis—an achievement that invites comparison with Sapiens.', 'Lan Xue', 'Dean of Schwarzman College, Tsinghua University'),
        ('The history of technological invention from the perspective of those who use technology, making it feel tangible and refreshingly new.', 'Xiaochun Sun', 'Professor, University of Chinese Academy of Sciences'),
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
                   '<p>电子产品（电子书与电子图谱）一经交付完成，概不退货退款。本店保证文件成功交付：如下载失败或文件损坏，将免费重新交付。印刷版由第三方零售商出售，其退货与退款依出售该印刷版之零售商的政策办理。</p>\n'
                   '</div>\n</section>')
    else:
        returns = ('<section class="block" id="returns">\n<h2>Return Policy</h2>\n<div class="about-text">\n'
                   '<p>All sales of digital products (ebooks and digital posters) are final upon completion of delivery; delivered digital products are non-refundable. We guarantee successful delivery of your files — if a download fails or a file is corrupted, we will re-deliver it at no additional charge. Print editions are sold through third-party retailers, and returns and refunds for print editions are governed by the policies of the retailer from which the print edition was purchased.</p>\n'
                   '</div>\n</section>')
    # visible ISBN line in the book info (strip earlier injected lines first)
    books_sec = re.sub(r'\n?<p class="en">(Print edition ISBN:|纸质版 ISBN：|ISBN[:：])[^<]*</p>', '', books_sec)
    books_sec = re.sub(r'\n?<p class="tagline">[^<]*</p>', '', books_sec)
    if zh:
        books_sec = books_sec.replace(
            '<p class="en">（第二版）董洁林 著 · Javvin Company</p>',
            '<p class="en">（第二版）董洁林 著 · Javvin Company</p>\n<p class="en">ISBN：978-1-60267-030-3</p>\n<p class="tagline">从吃饱穿暖到人工智能，沿着人类欲望的线索，重新理解科技如何改变社会和历史。</p>', 1)
    else:
        books_sec = books_sec.replace(
            '<p class="en">by Jielin Dong · Javvin Company</p>',
            '<p class="en">by Jielin Dong · Javvin Company</p>\n<p class="en">ISBN: 978-1-60267-031-0</p>\n<p class="tagline">From food and clothing to artificial intelligence — following the thread of human desire to rethink how technology changes society and history.</p>', 1)
    bodies = {
        'home': hero_html + '\n' + cards(lang) + '\n' + praise_block(lang) + '\n' + footer(books_pg),
        'books': books_sec + '\n' + footer(books_pg),
        'posters': section(get_page('posters.html', zh), 'posters') + '\n' + footer(books_pg),
        'articles': section(get_page('articles.html', zh), 'articles') + '\n' + footer(books_pg),
        'about': section(get_page('about.html', zh), 'about') + '\n' + returns + '\n' + footer(books_pg),
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
