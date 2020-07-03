from obj.repo import get_repo_info
import arff
import os
from configuration import conf
from mistune import markdown
import bs4


attr_list = ['stars', 'readme']
STRING_TYPE = 'STRING'
REAL_TYPE = 'NUMERIC'

threshold = 121

attrs = [
    ('popularity', ['unpopular', 'popular']),
    # ('stars', REAL_TYPE),
    ('readme', STRING_TYPE)
]


def parse_markdown(readme_content):
    html = markdown(readme_content)
    text = bs4.BeautifulSoup(html, 'html.parser').get_text()
    return text


def md2arff():
    ri_obj_list = get_repo_info(to_dict=False, combine_star_events=True)
    repo_set = set()
    data = dict()
    data['attributes'] = attrs
    data['description'] = ''
    data['relation'] = 'readme'
    readme_file_set = set()
    inline_data = list()
    for ri in ri_obj_list:
        if (ri.repo_owner, ri.repo_name) in repo_set:
            continue
        repo_set.add((ri.repo_owner, ri.repo_name))
        paper_repo_owner = getattr(ri, 'paper_repo_owner')
        paper_repo_name = getattr(ri, 'paper_repo_name')
        repo_path = os.path.join(conf.repo_path, paper_repo_owner, paper_repo_name)

        assert os.path.exists(repo_path)
        file_list = os.listdir(repo_path)
        readme_path = ''
        for f in file_list:
            if f.lower().startswith('readme.'):
                readme_path = os.path.join(repo_path, f)
                break
        if readme_path == '':
            readme_content = ''
        else:
            with open(readme_path, 'r', encoding='utf-8', errors='ignore') as readme_f:
                readme_content = readme_f.read()

        if readme_path != '' and f.lower() == 'readme.md':
                readme_content = parse_markdown(readme_content)

        readme_content = readme_content.lower()
        readme_content = readme_content.replace('\n', ' ')
        readme_content = readme_content.replace('\"', ' ')
        readme_content = readme_content.replace('\'', ' ')
        inline_data_unit = list()
        if ri.stars_count >= threshold:
            inline_data_unit.append('popular')
        else:
            inline_data_unit.append('unpopular')
        inline_data_unit.append(readme_content)
        inline_data.append(inline_data_unit)

    data['data'] = inline_data

    file_content = arff.dumps(data)
    arff_path = os.path.join(conf.root_path, 'text_analysis.arff')
    with open(arff_path, 'w', encoding='utf-8') as f:
        f.write(file_content)


if __name__ == '__main__':
    md2arff()


