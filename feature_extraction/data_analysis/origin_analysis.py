from obj.paper import get_papers_from_db
from configuration import conf
import os
import re

paper_data = get_papers_from_db(with_citation=True)
i = 1
for pd in paper_data:
    repo_owner = pd.repo_owner
    repo_name = pd.repo_name
    repo_path = os.path.join(conf.repo_path, repo_owner, repo_name)
    if i > 378:
        print(pd.title, pd.code_link)
        print(pd.repo_owner)
        print(pd.link)

        if os.path.exists(repo_path):
            file_list = os.listdir(repo_path)
            readme_path = ''
            for f in file_list:
                if f.lower().startswith('readme.'):
                    readme_path = os.path.join(repo_path, f)
            if readme_path == '':
                readme_content = ''
            else:
                with open(readme_path, 'r', encoding='utf-8', errors='ignore') as readme_f:
                    readme_content = readme_f.read()
            temp = readme_content.lower()

            repo_desc = pd.get_repo_desc()

            if repo_desc is None:
                repo_desc = ''
            print(repo_desc)

            contain_citation = 'cite' in temp or 'citation' in temp
            if re.search(r'author\s*=\s*{', temp):
                contain_citation = True
                lines = temp.split('\n')
                for l in lines:
                    if re.search(r'author\s*=\s*{', l):
                        print(l)
            if contain_citation:
                print('contain citation')
            if 'our preprint' in temp or 'our paper' in temp or 'our work' in temp:
                print('original paper')

            contain_official = 'official' in temp or 'official' in repo_desc.lower()
            if contain_official:
                print('suspiciously official')

            contain_code_for = 'code for' in temp or 'official' in repo_desc.lower()
            if contain_code_for:
                print('coding for exists')

            contain_accompany = 'accompany' in temp or 'accompany' in repo_desc.lower()
            if contain_accompany:
                print('accompany exists')

            contain_paper_title = False
            if pd.title.lower() in temp:
                contain_paper_title = True
            if pd.title.lower() in repo_desc.lower():
                contain_paper_title = True
            if contain_paper_title:
               print('contain paper title')

            contain_reimplementation = False
            if 're-implementation' in temp or 'reimplementation' in temp:
                contain_reimplementation = True
            if 're-implementation' in repo_desc.lower() or 'reimplementation' in repo_desc.lower():
                contain_reimplementation = True
            if contain_reimplementation:
                print('contain reimplementation')

        input()
    i += 1
