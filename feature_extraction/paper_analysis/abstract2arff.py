import arff
from obj.paper import get_papers_from_db
import os
from configuration import conf
from obj.repo import get_repo_info

STRING_TYPE = 'STRING'
REAL_TYPE = 'NUMERIC'

attrs = [
    ('popularity', ['unpopular', 'popular']),
    ('text', STRING_TYPE)
]

threshold = 150

def get_data():
    data = dict()
    data['attributes'] = attrs
    data['description'] = ''
    data['relation'] = 'abs'
    repo_infos = get_repo_info(combine_star_events=True)
    data_list = list()
    for ri in repo_infos:
        d = list()
        if ri.year == 2018 and ri.conf == 'NIPS':
            continue
        conference = getattr(ri, 'conf')
        title = getattr(ri, 'title')
        if conference is None or conference == '':
            continue
        if title in conf.excluded_papers:
            continue
        if ri.language == '' or ri.language is None:
            continue
        if ri.stars_count >= threshold:
            d.append('popular')
        else:
            d.append('unpopular')

        # abs_path = os.path.join(conf.paper_abs_path(), 'abstracts')
        abs_path = os.path.join(conf.paper_pdf_path(), 'text')
        this_abs_path = os.path.join(abs_path, str(ri.paper_id) + '.txt')
        with open(this_abs_path, 'r', encoding='ascii', errors="ignore") as f:
            file_content = f.read()
        content = file_content.lower()
        content = content.replace('\r', ' ')
        content = content.replace('\n', ' ')
        content = content.replace('\"', ' ')
        content = content.replace('\'', ' ')
        d.append(content)
        data_list.append(d)

    data['data'] = data_list
    file_content = arff.dumps(data)
    arff_path = os.path.join(conf.root_path, 'paper_analysis.arff')
    with open(arff_path, 'w', encoding='utf-8') as f:
        f.write(file_content)
    return data_list


if __name__ == '__main__':
    get_data()







