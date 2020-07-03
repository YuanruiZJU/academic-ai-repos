from configuration import conf
import os
from obj.paper import get_papers_from_db
from mistune import markdown
from bs4 import BeautifulSoup


class Readme(object):
    def __init__(self, repo_owner, repo_name):
        repo_path = os.path.join(conf.repo_path, repo_owner, repo_name)
        file_names = os.listdir(repo_path)
        temp_readme_files = set()
        self.readme_content = ''

        for fn in file_names:
            fn = fn.lower().lstrip().rstrip()
            if fn.startswith('readme.'):
                temp_readme_files.add(fn)
            elif fn.endswith('.md'):
                print(repo_owner, repo_name, fn)
        if 'readme.md' in temp_readme_files:
            readme_path = os.path.join(repo_path, 'readme.md')
            with open(readme_path, 'r', encoding='utf-8', errors='ignore') as f:
                self.readme_content = f.read()
        self.html_soup = None


class MarkDownReadme(Readme):
    def to_html(self):
        readme_html = markdown(self.readme_content)
        html_soup = BeautifulSoup(readme_html, 'html.parser')
        self.html_soup = html_soup

    def parse_readme_html(self):
        header_index = range(1, 7)
        for hi in header_index:
            headers = self.html_soup.find_all('h'+str(hi))
            if len(headers) == 0:
                continue
            else:
                pass


if __name__ == '__main__':
    paper_data = get_papers_from_db()
    repo_set = set()
    for pd in paper_data:
        if (pd.repo_owner, pd.repo_name) in repo_set:
            continue
        repo_set.add((pd.repo_owner, pd.repo_name))
        mdr = MarkDownReadme(pd.repo_owner, pd.repo_name)
