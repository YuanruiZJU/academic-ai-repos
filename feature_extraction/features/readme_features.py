from obj import BaseObj
from obj.repo import Repo
from configuration import conf
from utils import get_readme_path
from mistune import markdown
import bs4
from bs4 import BeautifulSoup
import re
import os

candidate_framework = ['tensorflow', 'pytorch',
                       'chainer', 'caffe', 'caffe2', 'matlab',
                       'mxnet', 'paddlepaddle', 'torch']


def check_link_is_repo(link, repo_owner, paper_repo_owner):
    if 'github.com' in link:
        g_index = link.index('github.com')
        link_repo_info = link[g_index+len('github.com/'):]
        terms = link_repo_info.split('/')
        if terms[-1].strip() == '':
            terms = terms[:-1]

        if len(terms) >= 2:
            if repo_owner.lower() == terms[0].lower() or \
                    paper_repo_owner.lower() == terms[0].lower():
                return False
            elif terms[0].lower in ReadmeFeatures.github_set:
                return False
            else:
                ReadmeFeatures.github_set.add(terms[0].lower())
                return True
    return False


def check_real_cmd(code):
    cmd = code.get_text()
    cmd = cmd.lower().strip()
    if cmd.startswith('@'):
        return False
    if '=' in cmd:
        return False
    if cmd.startswith('\''):
        return False
    if cmd.startswith('\"'):
        return False
    if cmd.startswith('.'):
        return False
    if cmd.startswith('-'):
        return False
    tokens = cmd.split()
    if len(tokens) == 1:
        return False
    return True


class ReadmeFeatures(BaseObj):
    attrs = ['num_lists', 'code_blocks', 'code_elements', 'contain_project_page', 'contain_data', 'contain_docker',
        'contain_trained_model', 'dynamic_images', 'images', 'tables',
        'has_video', 'github_links', 'framework'
    ]

    github_set = set()

    def __init__(self, ri):
        super().__init__()
        assert isinstance(ri, Repo)
        ReadmeFeatures.github_set = set()
        if getattr(ri, 'paper_repo_owner', None) is None:
            ri.combine_with_paper()
        self.repo_owner = ri.repo_owner
        self.repo_name = ri.repo_name
        self.paper_repo_owner = getattr(ri, 'paper_repo_owner')
        self.paper_repo_name = getattr(ri, 'paper_repo_name')
        readme_path = get_readme_path(self.paper_repo_owner, self.paper_repo_name)
        if readme_path == '':
            self.readme_content = ''
            self.html_soup = None
            self.plain_readme = ''
            self.html_content = ''
        elif readme_path.endswith('.md'):
            with open(readme_path, 'r', encoding='utf-8', errors='ignore') as f:
                self.readme_content = f.read()
                html_content = markdown(self.readme_content)
                html_content = html_content.replace('&lt;', '<')
                html_content = html_content.replace('&gt;', '>')
                self.html_content = html_content
                self.html_soup = BeautifulSoup(html_content, 'lxml')
                # import pdb
                # pdb.set_trace()
                self.plain_readme = self.html_soup.get_text().lower()
        else:
            with open(readme_path, 'r', encoding='utf-8', errors='ignore') as f:
                self.readme_content = f.read()
                self.html_soup = None
                self.html_content = ''
                self.plain_readme = self.readme_content.lower()
        self.stars = ri.stars_count
        self.framework = 'Unknown'
        self.num_lists = 0
        # self.num_lines_cmd = 0
        self.code_blocks = 0
        self.contain_project_page = 0
        self.contain_data = 0
        self.contain_docker = 0
        self.contain_trained_model = 0
        self.contain_contact = 0
        self.dynamic_images = 0
        self.images = 0
        self.tables = 0
        self.has_video = 0
        self.github_links = 0
        self.num_tokens = 0
        self.code_elements = 0
        self.get_lists()
        # self.get_code_steps()
        self.get_code_blocks()
        self.check_links()
        self.check_images_and_tables()
        self.get_framework_from_readme()

    def get_lists(self):
        # if self.html_soup is not None:
        #     for c in self.html_soup.children:
        #         if c.name in ['ol', 'ul']:
        #             self.num_lists += 1
        self.num_lists = self.html_content.count('<ol>') + self.html_content.count('<ul>')

    # def get_code_steps(self):
    #     if self.html_soup is not None:
    #         code_elements = self.html_soup.find_all('code')
    #         for ce in code_elements:
    #             code_text_lines = ce.get_text().split('\n')
    #             for l in code_text_lines:
    #                 if l.startswith(' '):
    #                     continue
    #                 l_simple = l.lstrip().rstrip()
    #                 if l_simple == '':
    #                     continue
    #                 if l_simple.startswith('/') or l_simple.startswith('#') or l_simple.startswith('"'):
    #                     continue
    #                 if check_real_cmd(ce):
    #                     self.num_lines_cmd += 1

    def get_code_blocks(self):
        code_block_counts = self.readme_content.count('```')
        self.code_blocks = int(code_block_counts / 2)
        ticks_count = self.readme_content.count('`')
        self.code_elements = int((ticks_count - code_block_counts * 3)/2)
        # if self.html_soup is None:
        #     self.code_blocks = 0
        # else:
        #     code_block_objs = self.html_soup.find_all('code')
        #     for obj in code_block_objs:
        #         code_content = obj.get_text()
        #         if re.search(r'title\s*=', code_content) is not None:
        #             temp_code_blocks -= 1
        #             continue
        #         if re.search(r'author\s*=', code_content) is not None:
        #             temp_code_blocks -= 1
        #             continue
        #         self.code_blocks += 1
        #     self.code_elements = self.code_blocks - temp_code_blocks
        #     self.code_blocks = temp_code_blocks
        #     if self.code_blocks < 0:
        #         self.code_blocks = 0

    def check_links(self):
        project_page_pattern = re.search(r'project\s+page', self.plain_readme)
        if project_page_pattern is not None:
            self.contain_project_page = 1

        train_model_pattern = re.search(r'pre(-)?trained\s+|\s+trained\s+model|trained\s+\S+\s+model|pre(-)?trained',
                                        self.plain_readme)
        if train_model_pattern is not None:
            self.contain_trained_model = 1

        if 'docker' in self.plain_readme:
            self.contain_docker = 1

        if self.html_soup is not None:
            links = self.html_soup.find_all('a')
        else:
            links = list()
        for l in links:
            assert isinstance(l, bs4.element.Tag)
            try:
                http_link = l['href'].lower()
            except KeyError:
                continue
            link_text = l.get_text().lower()
            if 'arxiv.org' in http_link or 'nips.cc' in http_link \
                or 'openaccess' in http_link \
                or 'proceedings.mlr' in http_link:
                continue

            if 'youtu' in link_text:
                self.has_video = 1

            if check_link_is_repo(http_link, self.repo_owner, self.paper_repo_owner):
                self.github_links += 1
            previous_ele = l.previous_element
            next_ele = l.next_element.next_element
            pe_str = ''
            ne_str = ''
            if isinstance(previous_ele, bs4.element.NavigableString):
                pe_str = str(previous_ele).lower()
            if isinstance(next_ele, bs4.element.NavigableString):
                ne_str = str(next_ele).lower()
            try:
                pe_rindex = pe_str.rindex('. ')
            except ValueError:
                pe_rindex = -2
            try:
                ne_lindex = ne_str.index('. ')
            except ValueError:
                ne_lindex = len(ne_str)
            sentence = pe_str[pe_rindex+2:] + link_text + ne_str[:ne_lindex]
            if 'project' in sentence:
                self.contain_project_page = 1
            if 'docker' in sentence:
                self.contain_docker = 1
            if 'data' in sentence:
                self.contain_data = 1
            if 'video' in sentence or 'youtube' in sentence:
                self.has_video = 1

    def check_images_and_tables(self):
        if self.html_content != '':
            self.images = self.html_content.count('<img')
            self.dynamic_images = self.html_content.count('.gif')
            self.tables = self.html_content.count('<center')
            # images = self.html_soup.find_all('img')
            # for im in images:
            #     image_path = im['src'].lower()
            #     if image_path.endswith('.gif'):
            #         self.dynamic_images += 1
            # self.images = len(images)
            # tables = self.html_soup.find_all('center')
            # self.tables = len(tables)

    def get_framework_from_readme(self):
        from paper_analysis.prepare import tokenize
        tokens = tokenize(self.plain_readme)
        self.num_tokens = len(tokens)
        for t in tokens:
            if t in candidate_framework:
                self.framework = t
                break





if __name__ == '__main__':
    from obj.repo import get_repo_info

    repo_info = get_repo_info(combine_star_events=True)
    dict_list = list()
    i = 0
    for ri in repo_info:
        if ri.repo_owner == 'luanfujun':
            print(ri.paper_repo_owner)
            conference = getattr(ri, 'conf')
            title = getattr(ri, 'title')
            if conference is None or conference == '':
                continue
            if title in conf.excluded_papers:
                continue
            if ri.language == '' or ri.language is None:
                continue
            i += 1
            print(ReadmeFeatures(ri).to_dict())

