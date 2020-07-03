from obj.paper import get_papers_from_db
import requests
from configuration import conf
import os
from urllib.request import urlretrieve


def download_file(download_url, path):
    urlretrieve(download_url, path)

def get_website(url):
    if url.startswith('https://'):
        temp_url = url[8:]
    else:
        assert url.startswith('http://')
        temp_url = url[7:]
    temp_index= temp_url.index('/')
    website = temp_url[:temp_index]
    return website

def preprocess_url(url):
    if url.endswith(".pdf"):
        return url
    website = get_website(url)
    if website == 'openaccess.thecvf.com':
        temp_str = url.replace('/html/', '/papers/')
        temp_str = temp_str.rstrip('.html')
        temp_str = temp_str + '.pdf'
        return temp_str
    if website == 'arxiv.org':
        temp_str = url.replace('/abs/', '/pdf/')
        temp_str = temp_str + '.pdf'
        return temp_str
    if website == 'proceedings.mlr.press':
        temp_url = url.rstrip('.html')
        end_index = temp_url.rindex('/')
        end_str = temp_url[end_index:]
        temp_str = temp_url + end_str + '.pdf'
        return temp_str
    return "Hello"



def get_paper_path(id):
    return os.path.join(conf.paper_pdf_path(), str(id)+".pdf")


def crawl_main():
    paper_data = get_papers_from_db()
    for pd in paper_data:
        print(pd.id)
        link = pd.link
        link2 = preprocess_url(link)
        save_path = get_paper_path(pd.id)
        if os.path.exists(save_path):
            continue
        print(pd.title)
        print(link2)
        if 'content_iccv' in link2:
            link2 = link2.replace('content_iccv', 'content_ICCV')
        if link2 != 'Hello':
            download_file(link2, save_path)


if __name__ == '__main__':
    # paper_data = get_papers_from_db()
    # for pd in paper_data:
    #     if preprocess_url(pd.link) == 'Hello':
    #         print(pd.link)
    crawl_main()