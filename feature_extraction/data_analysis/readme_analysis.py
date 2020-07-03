from configuration import conf
import os
from mistune import markdown
from bs4 import BeautifulSoup
from obj.paper import get_papers_from_db
import arff

STRING_TYPE = 'STRING'
threshold = 121

attrs = [
    ('popularity', ['unpopular', 'popular']),
    # ('stars', REAL_TYPE),
    ('readme', STRING_TYPE)
]

headers = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']


paper_data = get_papers_from_db()
tuples = list()
for p in paper_data:
    owner = p.repo_owner
    name = p.repo_name
    title = p.title

    repo_path = os.path.join(conf.repo_path, owner, name)
    readme_path = os.path.join(repo_path, 'readme.md')

    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8', errors='ignore') as f:
            readme_content = f.read()

        html_content = markdown(readme_content)

        html_soup = BeautifulSoup(html_content, 'html.parser')
        header_results = list()
        for header in headers:
            header_results += html_soup.find_all(header)

        for c in html_soup.children:
            if c in header_results:
                header_string = c.get_text().lower().rstrip().lstrip()
                if header_string == title.lower().rstrip().lstrip():
                    continue
                elif header_string == name.lower().rstip().lstrip():
                    continue


