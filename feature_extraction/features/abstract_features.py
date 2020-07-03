from obj import BaseObj
from obj.repo import Repo
from configuration import conf
import os
from paper_analysis import get_lda_represent


class AbstractTopicModelFeatures(BaseObj):
    attrs = ['paper_id', 'paper_title', 't1', 't2', 't3', 't4', 't5',
             't6', 't7', 't8', 't9', 't10',
             't11', 't12', 't13', 't14', 't15',
             't16', 't17', 't18', 't19', 't20', 'conference', 'year', 'citation']

    def __init__(self, ri):
        super().__init__()
        assert isinstance(ri, Repo)
        paper_id = getattr(ri, 'paper_id')
        paper_title = getattr(ri, 'title')
        self.paper_id = paper_id
        self.paper_title = '\"' + paper_title + '\"'
        self.paper_title = self.paper_title.replace('\n', ' ')
        self.paper_title = self.paper_title.replace('\"', ' ')
        self.paper_title = self.paper_title.replace('“', ' ')
        self.paper_title = self.paper_title.replace('”', ' ')
        # sys_abs_path = os.path.join(conf.paper_abs_path(), 'abstracts')
        sys_abs_path = os.path.join(conf.paper_pdf_path(), 'text')
        this_abs_path = os.path.join(sys_abs_path, str(paper_id) + '.txt')
        with open(this_abs_path, 'r', encoding='ascii', errors='ignore') as f:
            abs_content = f.read()
        v = get_lda_represent(abs_content)
        i = 1
        while i <= 20:
            setattr(self, 't'+str(i), 0)
            i += 1
        for t in v:
            topic = 't' + str(t[0]+1)
            setattr(self, topic, t[1])
        self.conference = getattr(ri, 'conf')
        self.stars = ri.stars_count
        self.year = getattr(ri, 'year')
        self.citation = getattr(ri, 'citation')


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
        dict_list.append(AbstractTopicModelFeatures(ri).to_dict())
        i += 1
    from utils import dict_list2csv

    dict_list2csv(dict_list, file_path='D://abstract_features2.csv',
                  fieldnames=AbstractTopicModelFeatures.attrs)







