from configuration import conf
import os
from bs4 import BeautifulSoup
import bs4


website_name = 'arxiv.org'
example = '6.html'

example_path = os.path.join(conf.paper_abs_path(), website_name, example)
with open(example_path, 'r', encoding='utf-8') as f:
    html_content = f.read()

html_soup = BeautifulSoup(html_content,  ['lxml', 'xml'])
blocks = html_soup.find_all('meta')
abstract = list()
for b in blocks:
    try:
        print(b['name'])
    except KeyError:
        print(b)

