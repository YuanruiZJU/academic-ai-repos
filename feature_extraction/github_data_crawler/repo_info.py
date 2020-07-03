import requests
import simplejson
from configuration import conf
import os
from obj.paper import Paper


usernames, passwords = conf.github_auth


class RepoInfoCrawler:
    def __init__(self, paper_obj):
        assert(isinstance(paper_obj, Paper))
        self.repo_name = paper_obj.repo_name
        self.repo_owner = paper_obj.repo_owner
        self.repo_exist = True
        if not self.check_repo_in_disk():
            self.repo_exist = False
        self.url = 'https://api.github.com/repos/' + self.repo_owner + '/' + self.repo_name

    @staticmethod
    def save_path(repo_owner, repo_name):
        if not os.path.exists(conf.info_path):
            os.makedirs(conf.meta_path)
        save_path = os.path.join(conf.info_path, repo_owner)
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        save_path = os.path.join(save_path, repo_name + '.json')
        return save_path

    def check_repo_in_disk(self):
        this_repo_path = os.path.join(conf.repo_path, self.repo_owner, self.repo_name)
        return os.path.exists(this_repo_path)

    def check_data_in_disk(self):
        this_info_path = os.path.join(conf.info_path, self.repo_owner, self.repo_name+'.json')
        return os.path.exists(this_info_path)

    def crawl_to_disk(self):
        if not self.repo_exist:
            return False
        if self.check_data_in_disk():
            return False
        print(self.url)
        response = requests.get(self.url, auth=(usernames[0], passwords[0]))
        with open(RepoInfoCrawler.save_path(self.repo_owner, self.repo_name), 'w+', encoding='utf-8') as f:
            f.write(response.text)
        return True


def print_repo_info():
    owner = 'trakaros'
    repo = 'MPIIGaze.json'
    f_path = os.path.join(conf.info_path, owner, repo)
    with open(f_path, 'r', encoding='utf-8') as f:
        json_obj = simplejson.load(f)
        import pprint
        pprint.pprint(json_obj)


if __name__ == '__main__':
    print_repo_info()

