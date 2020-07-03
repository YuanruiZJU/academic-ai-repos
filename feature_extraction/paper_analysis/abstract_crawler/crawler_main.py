from obj.paper import get_papers_from_db
import requests
from configuration import conf
import os
import bs4
from bs4 import BeautifulSoup


def preprocess_url(url):
    if url.endswith('pdf'):
        if 'openaccess.thecvf.com' in url:
            url = url.replace('/papers/', '/html/')
            url = url[:-3] + 'html'
        if 'arxiv.org' in url:
            url = url.replace('/pdf/', '/abs/')
            url = url[:-4]
        if 'papers.nips.cc' in url:
            url = url[:-4]
    return url


def get_paper_path(url, id):
    if url.startswith('https://'):
        temp_url = url[8:]
    else:
        assert url.startswith('http://')
        temp_url = url[7:]
    temp_index= temp_url.index('/')
    website = temp_url[:temp_index]
    website_path = os.path.join(conf.paper_abs_path(), website)
    if not os.path.exists(website_path):
        os.makedirs(website_path)
    return website, os.path.join(website_path, str(id) + '.html')


def crawl_main():
    paper_data = get_papers_from_db()
    for pd in paper_data:
        print(pd.id)
        link = pd.link
        link2 = preprocess_url(link)
        website, save_path = get_paper_path(link2, pd.id)
        response = requests.get(link2)
        with open(save_path, 'w', encoding='utf-8') as f:
            f.write(response.text)


def extract_abstract_from_arxiv(example_path):
    with open(example_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    html_soup = BeautifulSoup(html_content, ['lxml', 'xml'])
    blocks = html_soup.find_all('blockquote')
    abstract = None
    for b in blocks:
        if b['class'] == 'abstract mathjax':
            abstract = b.get_text()
    if abstract.startswith('Abstract:'):
        abstract = abstract[9:].lstrip()
    return abstract


def extract_abstract_from_openaccess(example_path):
    with open(example_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    html_soup = BeautifulSoup(html_content, ['lxml', 'xml'])
    abstract = html_soup.find_all('div', id='abstract')[0].get_text()
    return abstract


def extract_abstract_from_paper_nips(example_path):

    with open(example_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    html_soup = BeautifulSoup(html_content, ['lxml', 'xml'])
    p_objs = html_soup.find_all('p')
    abstract = None
    for p in p_objs:
        try:
            if p['class'] == 'abstract':
                abstract = p.get_text()
        except KeyError:
            pass
    assert(abstract is not None)
    return abstract


def extract_abstract_from_proceedings(example_path):
    with open(example_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    html_soup = BeautifulSoup(html_content, ['lxml', 'xml'])
    abstract = html_soup.find_all('div', id='abstract')[0].get_text()
    return abstract


if __name__ == '__main__':
    paper_data = get_papers_from_db()
    for pd in paper_data:
        print(pd.id)
        if pd.conf is None or pd.conf == '':
            continue
        else:
            website, path = get_paper_path(pd.link, pd.id)
            print(website)
            abstract_text_path = os.path.join(conf.paper_abs_path(), 'abstracts',
                                 str(pd.id) + '.txt')
            if os.path.exists(abstract_text_path):
                continue
            if website.startswith('arxiv'):
                abstract = extract_abstract_from_arxiv(path)
            elif website.startswith('openaccess'):
                abstract = extract_abstract_from_openaccess(path)
            elif website.startswith('papers'):
                abstract = extract_abstract_from_paper_nips(path)
            elif website.startswith('proceedings'):
                abstract = extract_abstract_from_proceedings(path)
            else:
                continue
            with open(abstract_text_path, 'w', encoding='utf-8') as f:
                f.write(abstract)
