from configuration import conf
from parse import parse
from obj import BaseObj
from db.api import DataBaseApi
from obj.cache import Cache
import csv
from google_scholar_crawler.title_parser import parse_title_scholar
from google_scholar_crawler.title_parser import parse_titles2
import os


class Paper(BaseObj):
    attrs = ['id', 'title', 'link', 'conf', 'repo_name', 'repo_owner', 'code_link', 'year']
    model_name = 'paper'

    def __init__(self):
        super().__init__()
        self.id = None
        self.title = None
        self.link = None
        self.conf = None
        self.repo_name = None
        self.repo_owner = None
        self.code_link = None
        self.year = None

    def get_conf(self):
        return self.conf.lstrip().rstrip()

    def combine_with_citations(self):
        citations = parse_title_scholar()
        try:
            citations[self.title]
        except KeyError:
            raise
        setattr(self, 'citation', citations[self.title])

    def get_repo_desc(self):
        repo_info_path = os.path.join(conf.info_path, self.repo_owner, self.repo_name + '.json')
        if os.path.exists(repo_info_path):
            with open(repo_info_path, 'r', encoding='utf-8') as f:
                import simplejson
                json_content = simplejson.load(f)
                return json_content['description']
        else:
            return ''


def store_papers():
    """
    Version 1. Directly use the pwc data.
    Version 2. Unluckily, we find that pwc data is not clean.
               We manually cleaned our data.
               After that, we use the cleaned data and
               store the paper, repo data again.
    :return:
    """
    md_path = conf.md_path
    paper_data = parse(md_path)
    db_objs = list()

    correct_titles, title_url_map = parse_titles2()
    correct_titles_set = set(correct_titles)

    for p in paper_data:
        if p['title'] not in correct_titles_set:
            continue
        url = p['code_link']
        try:
            url = title_url_map[p['title']]
            p['code_link'] = url
        except KeyError:
            pass
        terms = url.split('/')
        p['repo_name'] = terms[-1]
        p['repo_owner'] = terms[-2]
        if p['repo_name'] == '':
            p['repo_name'] = terms[-2]
            p['repo_owner'] = terms[-3]
        p_obj = Paper()
        p_obj.from_dict(p)
        db_obj = p_obj.to_db_obj()
        db_objs.append(db_obj)
    db_api = DataBaseApi()
    db_api.insert_objs(db_objs)
    db_api.close_session()


def get_papers_from_db(with_citation=False):
    if Cache.cache_paper_data is not None:
        return Cache.cache_paper_data
    else:
        table_name = Paper.model_name
        db_api = DataBaseApi()
        papers = db_api.query_all(table_name)
        paper_obj_list = list()
        for p in papers:
            p_obj = Paper()
            p_obj.from_db_obj(p)
            if with_citation:
                p_obj.combine_with_citations()
            paper_obj_list.append(p_obj)
        db_api.close_session()
        Cache.cache_paper_data = paper_obj_list
        return paper_obj_list


def papers2csv(file_path, print_attrs=None):
    if print_attrs is not None and 'citation' in print_attrs:
        paper_data = get_papers_from_db(with_citation=True)
    else:
        paper_data = get_papers_from_db()
    write_dicts = list()
    for p in paper_data:
        write_dicts.append(p.to_dict(print_attrs))
    with open(file_path, 'w', encoding='utf-8', newline='') as csvfile:
        fieldnames = print_attrs
        if fieldnames is None:
            fieldnames = Paper.attrs
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(write_dicts)


# Temporary
def get_remaining_titles():
    paper_data = get_papers_from_db()
    citations, titles = parse_title_scholar()

    with open('../google_scholar_crawler/titles2', 'a+', encoding='utf-8') as f:
        for pd in paper_data:
            f.write(pd.title)
            f.write('\n')


if __name__ == '__main__':
    # papers = get_papers_from_db()
    # project_names = set()
    # code_links = set()
    # for p in papers:
    #     url = p.code_link
    #     terms = url.split('/')
    #     pn = terms[-1]
    #     if terms[-1] == '':
    #         pn = terms[-2]
    #     if url not in code_links and pn in project_names:
    #         print(url)
    #     project_names.add(pn)
    #     code_links.add(p.code_link)
    # print_attrs = ['title', 'conf']
    # papers2csv('repos.csv', print_attrs)
    # get_remaining_titles()
    paper_data = get_papers_from_db()
    for pd in paper_data:
        print(pd.title, pd.code_link)



