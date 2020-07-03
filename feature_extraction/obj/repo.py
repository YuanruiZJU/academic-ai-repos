from obj import BaseObj
from obj.paper import Paper
from obj.paper import get_papers_from_db
from configuration import conf
import os
from db.api import DataBaseApi
import simplejson
from datetime import datetime
from obj.cache import Cache
import csv
from obj.star_event import get_star_events


class Repo(BaseObj):
    attrs = ['paper_id', 'repo_name', 'repo_owner', 'created_at',
             'stars_count', 'forks_count', 'subscribers_count',
             'network_count', 'language', 'license',
             'organization']
    model_name = 'repo'

    def __init__(self, paper_obj=None):
        super().__init__()
        self.paper_id = None
        self.id = None
        if paper_obj is None:
            self.repo_name = None
            self.repo_owner = None
        else:
            assert isinstance(paper_obj, Paper)
            self.repo_name = paper_obj.repo_name
            self.repo_owner = paper_obj.repo_owner
        self.created_at = None
        self.stars_count = None
        self.forks_count = None
        self.subscribers_count = None
        self.network_count = None
        self.language = None
        self.license = None
        self.organization = None

    def __from_json_obj(self, repo_json_obj):
        """
        We find that people can change the name of their repo.
        The owner of the repo can also be changed.

        Luckily, the url for crawling the data that are composed
        by the original owner and name is still useful.

        Hence, from json data, we update the owner and name of
        the repo.
        """
        self.repo_name = repo_json_obj['name']   # Update Repo Name
        self.repo_owner = repo_json_obj['owner']['login']  # Update Repo Owner
        created_at_str = repo_json_obj['created_at']
        self.created_at = datetime.strptime(created_at_str, '%Y-%m-%dT%H:%M:%SZ')
        self.stars_count = repo_json_obj['stargazers_count']
        self.forks_count = repo_json_obj['forks_count']
        self.subscribers_count = repo_json_obj['subscribers_count']
        self.network_count = repo_json_obj['network_count']
        self.language = repo_json_obj['language']
        license = repo_json_obj['license']
        if license is None:
            self.license = None
        else:
            self.license = license['name']
        try:
            self.organization = repo_json_obj['organization']['login']
        except KeyError:
            self.organization = None

    def from_json(self):
        json_path = os.path.join(conf.info_path, self.repo_owner, self.repo_name + '.json')
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                json_obj = simplejson.load(f)
                self.__from_json_obj(json_obj)
        else:
            print('Repo %s/%s not found!' % (self.repo_owner, self.repo_name))

    @property
    def repo_path(self):
        sys_repos_path = conf.repo_path
        path = os.path.join(sys_repos_path, self.repo_owner, self.repo_name)
        if os.path.exists(path):
            return path
        else:
            return None

    def combine_with_paper(self):
        paper_data = get_papers_from_db(with_citation=True)
        paper_obj = paper_data[self.paper_id - 1]
        setattr(self, 'title', paper_obj.title)
        setattr(self, 'conf', paper_obj.get_conf())
        setattr(self, 'year', paper_obj.year)
        setattr(self, 'citation', getattr(paper_obj, 'citation'))
        setattr(self, 'paper_repo_owner', paper_obj.repo_owner)
        setattr(self, 'paper_repo_name', paper_obj.repo_name)

    def combine_with_star_events(self):
        self.combine_with_paper()
        star_event_dict = get_star_events(to_dict=True)
        paper_repo_owner = getattr(self, 'paper_repo_owner')
        paper_repo_name = getattr(self, 'paper_repo_name')
        try:
            star_events = star_event_dict[(paper_repo_owner, paper_repo_name)]
        except KeyError:
            star_events = list()
        setattr(self, 'star_events', star_events)
        self.stars_count = len(star_events)

    def combine_with_repo_desc(self):
        if getattr(self, 'paper_repo_owner', None) is None:
            self.combine_with_paper()
        paper_repo_owner = getattr(self, 'paper_repo_owner')
        paper_repo_name = getattr(self, 'paper_repo_name')
        repo_info_path = os.path.join(conf.info_path, paper_repo_owner,
                                      paper_repo_name + '.json')
        description = ''
        if os.path.exists(repo_info_path):
            with open(repo_info_path, 'r', encoding='utf-8') as f:
                import simplejson
                json_content = simplejson.load(f)
                description = json_content['description']
        if description is None:
            description = ''
        setattr(self, 'desc', description)

def store_repo_info():
    paper_data = get_papers_from_db()
    db_objs = list()
    for pd in paper_data:
        pd_id = getattr(pd, 'id')
        print(pd_id)
        r = Repo(pd)
        r.from_json()
        r.paper_id = pd_id
        if r.stars_count is None:
            continue
        db_objs.append(r.to_db_obj())
    db_api = DataBaseApi()
    db_api.insert_objs(db_objs)
    db_api.close_session()


def get_repo_info(to_dict=False, combine_paper=False, combine_star_events=False):
    """
    We make sure that we only access database once
    and get all the data, and then, cache the data!
    """
    db_api = DataBaseApi()
    table_name = Repo.model_name
    repo_info = db_api.query_all(table_name)
    if to_dict:
        if Cache.cache_repo_info_dict is not None:
            return Cache.cache_repo_info_dict
        ri_obj_dict = dict()
        for ri in repo_info:
            ri_obj = Repo()
            ri_obj.from_db_obj(ri)
            if combine_paper:
                ri_obj.combine_with_paper()
            if combine_star_events:
                ri_obj.combine_with_star_events()
            ri_obj_dict[ri_obj.paper_id] = ri_obj
        Cache.cache_repo_info_dict = ri_obj_dict
        ret_obj_collection = ri_obj_dict
    else:
        if Cache.cache_repo_info_list is not None:
            return Cache.cache_repo_info_list
        ri_obj_list = list()
        for ri in repo_info:
            ri_obj = Repo()
            ri_obj.from_db_obj(ri)
            if combine_paper:
                ri_obj.combine_with_paper()
            if combine_star_events:
                ri_obj.combine_with_star_events()
            ri_obj_list.append(ri_obj)
        Cache.cache_repo_info_list = ri_obj_list
        ret_obj_collection = ri_obj_list
    db_api.close_session()
    return ret_obj_collection


def get_owner_repo_map():
    """
    We use repo owner and repo name to distinguish
    one repo from another.
    """
    repo_info_list = get_repo_info(to_dict=False)
    ret_map = dict()
    for ri in repo_info_list:
        key = (ri.repo_owner, ri.repo_name)
        try:
            ret_map[key]
        except KeyError:
            ret_map[key] = list()
        ret_map[key].append(ri.paper_id)
    paper_data = get_papers_from_db()
    paper_map = dict()
    for pd in paper_data:
        paper_map[pd.id] = (pd.repo_owner, pd.repo_name)

    for (o, n) in ret_map.keys():
        pids = ret_map[(o, n)]
        for pid in pids:
            if paper_map[pid] != (o, n):
                print(o, n),
                print(paper_map[pid])
    return ret_map


def repos2csv(file_path):
    print_attrs = ['title', 'conf', 'year', 'repo_name', 'repo_owner', 'created_at',
                   'stars_count', 'forks_count', 'subscribers_count',
                   'network_count', 'language', 'license',
                   'organization']
    repos_info = get_repo_info(combine_star_events=True)
    repo_dicts = list()
    repo_set = set()
    for repo in repos_info:
        if (repo.repo_owner, repo.repo_name) in repo_set:
            continue
        repo_set.add((repo.repo_owner, repo.repo_name))
        temp_dict = repo.to_dict(required_attrs=print_attrs)
        repo_dicts.append(temp_dict)
    with open(file_path, 'w', encoding='utf-8', newline='') as csvfile:
        fieldnames = print_attrs
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(repo_dicts)


if __name__ == '__main__':
    # repos2csv(file_path='repos.csv')
    store_repo_info()


