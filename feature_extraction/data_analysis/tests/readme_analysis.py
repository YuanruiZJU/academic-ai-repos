from configuration import conf
import os
from mistune import markdown
from bs4 import BeautifulSoup
import bs4

owner = 'luanfujun'
name = 'deep-photo-styletransfer'

repo_path = os.path.join(conf.repo_path, owner, name)
readme_path = os.path.join(repo_path, 'readme.md')

with open(readme_path, 'r', encoding='utf-8', errors='ignore') as f:
    readme_content = f.read()

html_content = markdown(readme_content)
html_content = html_content.replace('&lt;', '<')
html_content = html_content.replace('&gt;', '>')

with open("test.html", 'w') as f:
    f.write(html_content)

html_soup = BeautifulSoup(html_content, 'html.parser')

for c in html_soup.descendants:
    try:
        print(html_soup.find_all(name="img", recursive=True))
    except:
        continue

# level_headers = dict()
# header_set = set()
# header_index = range(1, 7)
# for hi in header_index:
#     headers = html_soup.find_all('h'+str(hi))
#     if len(headers) == 0:
#         continue
#     else:
#         for hr in headers:
#             header_set.add(hr)
#             level_headers[hr] = hi
