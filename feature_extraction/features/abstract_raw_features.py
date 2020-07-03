from obj import BaseObj
from obj.repo import Repo
from configuration import conf
import os


class AbstractRawFeatures(BaseObj):
    attrs = ['paper_id', 'abstract_text']

    def __init__(self, ri):
        super().__init__()
        assert isinstance(ri, Repo)
        paper_id = getattr(ri, 'paper_id')
        self.paper_id = paper_id
        sys_abs_path = os.path.join(conf.paper_abs_path(), 'abstracts')
        this_abs_path = os.path.join(sys_abs_path, str(paper_id) + '.txt')
        with open(this_abs_path, 'r', encoding='ascii', errors='ignore') as f:
            self.abstract_text = f.read()
        self.abstract_text = self.abstract_text.replace('\n', ' ')
        self.abstract_text.strip()


if __name__ == '__main__':
    from obj.repo import get_repo_info

    repo_info = get_repo_info(combine_star_events=True)
    dict_list = list()
    i = 0
    for ri in repo_info:
        print(i)
        conference = getattr(ri, 'conf')
        title = getattr(ri, 'title')
        if conference is None or conference == '':
            continue
        if title in conf.excluded_papers:
            continue
        if ri.language == '' or ri.language is None:
            continue
        dict_list.append(AbstractRawFeatures(ri).to_dict())
        i += 1
    from utils import dict_list2csv

    dict_list2csv(dict_list, file_path='D://abstract_features2.csv',
                  fieldnames=AbstractRawFeatures.attrs)





