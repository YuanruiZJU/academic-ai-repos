import requests
import simplejson
from configuration import conf
import os
from obj.paper import Paper
from obj.repo import get_repo_info
import math


star_str = 'stargazers'
usernames, passwords = conf.github_auth
page_size = 100
max_pages = 400


class StargazerCrawler:

    """
    We use REST API provided by Github to get information
    of each star event for each repository.

    Note the usage of the following REST API parameters
    page: which page do you need
    per_page: page size

    For each page, we check whether the number of returned
    instances is equal to the page size *page_size*
    """

    def __init__(self, paper_obj):
        assert(isinstance(paper_obj, Paper))
        self.paper_id = getattr(paper_obj, 'id')
        self.repo_name = paper_obj.repo_name
        self.repo_owner = paper_obj.repo_owner
        self.initial_url = 'https://api.github.com/repos/'
        self.page = 0
        self.per_page = page_size
        self.end_crawl = False

        if not self.check_repo_in_disk():
            self.end_crawl = True
            print('Repo %s not in disk!' % self.repo_name)

        if not self.end_crawl:
            print('Crawling data for %s\'s Repo %s' % (self.repo_owner, self.repo_name))
            self.repo_info = get_repo_info(to_dict=True)[self.paper_id]
            # if self.check_all_data_in_disk():
            #     self.end_crawl = True
            #     print('Repo %s downloaded' % self.repo_name)
            self.page = self.get_start_page() - 1

    def check_repo_in_disk(self):
        this_repo_path = os.path.join(conf.repo_path, self.repo_owner, self.repo_name)
        return os.path.exists(this_repo_path)

    def get_start_page(self):
        this_star_path = os.path.join(conf.star_path, self.repo_owner, self.repo_name)
        if not os.path.exists(this_star_path):
            return 1
        file_names = os.listdir(this_star_path)
        last_index = len(file_names)
        i = 1
        while i < last_index:
            file_path = os.path.join(this_star_path, str(i)+'.json')
            with open(file_path, 'r', encoding='utf-8') as f:
                json_content = simplejson.load(f)
                if len(json_content) < 100:
                    break
            i += 1
        return i

    def check_all_data_in_disk(self):
        this_star_path = os.path.join(conf.star_path, self.repo_owner, self.repo_name)
        star_count = self.repo_info.stars_count
        last_file_index = math.ceil(star_count / 100)
        if last_file_index > 400:
            last_file_index = 400
        last_file_name = str(last_file_index) + '.json'
        last_file_path = os.path.join(this_star_path, last_file_name)
        if os.path.exists(last_file_path):
            with open(last_file_path, 'r') as f:
                json_obj = simplejson.load(f)
                if len(json_obj) + (last_file_index - 1) * 100 >= star_count:
                    return True
                if len(json_obj) + (last_file_index - 1) * 100 >= 40000:
                    return True
        return False

    def generate_url(self):
        assert(self.page > 0)
        tmp_url = self.initial_url + self.repo_owner + '/' + self.repo_name + '/'
        tmp_url = tmp_url + star_str + '?page=%s' % self.page
        tmp_url = tmp_url + '&per_page=%s' % self.per_page
        return tmp_url

    def get_next_page(self):
        self.page += 1
        print('start crawling page %s' % self.page)
        if self.page > max_pages:
            self.end_crawl = True
        if self.end_crawl:
            print('Crawling process should end!')
            return None
        rest_url = self.generate_url()
        headers = {'Accept': 'application/vnd.github.v3.star+json'}
        response = requests.get(rest_url, headers=headers, auth=(usernames[0], passwords[0]))
        result_json = simplejson.loads(response.text)
        if len(result_json) < self.per_page:
            self.end_crawl = True
        return result_json

    def result_to_disk(self, result_json):
        if result_json is not None:
            this_star_path = os.path.join(conf.star_path, self.repo_owner, self.repo_name)
            store_path = this_star_path
            if not os.path.exists(store_path):
                os.makedirs(store_path)
            dest_path = os.path.join(store_path, '%s.json' % self.page)
            with open(dest_path, 'w', encoding='utf-8') as f:
                simplejson.dump(result_json, f)


if __name__ == '__main__':
    pass

