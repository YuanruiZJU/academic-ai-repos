import os
import simplejson as json
from datetime import datetime


current_dir = os.path.dirname(__file__)
pre_dir = os.path.dirname(current_dir)
config_path = os.path.join(pre_dir, "config.json")
excluded_paper_path = os.path.join(pre_dir, "exclude_papers")


class Config:
    def __init__(self):
        with open(config_path, 'rt') as f:
            config_content = f.read()
            json_obj = json.loads(config_content)
            self.__root_path = json_obj['root_path']
            self.__acd_repo = os.path.join(self.__root_path,
                                         json_obj['academic_statistics_path'])
            self.md_path = os.path.join(self.__acd_repo, json_obj['md_file'])
            self.__repo_path = os.path.join(self.__root_path, json_obj['repo_path'])
            self.__db_info = json_obj['mysql']
            self.__github_info = json_obj['github']
            self.analyze_date = datetime.strptime(json_obj['analyze_date'], '%Y-%m-%d')
            self.conf_date = json_obj['conf_date']
            with open(excluded_paper_path, 'r', encoding='utf-8') as f:
                titles = f.read().split('\n')
            self.excluded_papers = set()
            for t in titles:
                if t.lstrip().rstrip() != '':
                    self.excluded_papers.add(t)

    @property
    def repo_path(self):
        if not os.path.exists(self.__repo_path):
            os.makedirs(self.__repo_path)
        return self.__repo_path

    @property
    def root_path(self):
        return self.__root_path

    @property
    def star_path(self):
        return os.path.join(self.__root_path, 'star_events')

    @property
    def info_path(self):
        return os.path.join(self.__root_path, 'info')

    @property
    def scholar_path(self):
        return os.path.join(self.__root_path, 'scholar')

    @property
    def db_username(self):
        return self.__db_info['username']

    @property
    def db_password(self):
        return self.__db_info['password']

    @property
    def db_name(self):
        return self.__db_info['database-name']

    @property
    def github_auth(self):
        usernames = self.__github_info['username']
        passwords = self.__github_info['password']
        return usernames, passwords

    def paper_abs_path(self):
        abs_path = os.path.join(self.__root_path, 'paper_pages')
        if not os.path.exists(abs_path):
            os.makedirs(abs_path)
        return abs_path

    def paper_pdf_path(self):
        paper_path = os.path.join(self.__root_path, 'paper_pdf')
        if not os.path.exists(paper_path):
            os.makedirs(paper_path)
        return paper_path

    def cpd_result_path(self):
        cpd_path = os.path.join(self.__root_path, 'cpd_results')
        if not os.path.exists(cpd_path):
            os.makedirs(cpd_path)
        return cpd_path


if __name__ == '__main__':
    cf = Config()