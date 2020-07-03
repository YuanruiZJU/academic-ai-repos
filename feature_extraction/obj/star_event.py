from obj import BaseObj
from datetime import datetime
from obj.paper import Paper
from obj.paper import get_papers_from_db
from configuration import conf
import os
import simplejson
from db.api import DataBaseApi
from obj.cache import Cache


class StarEvent(BaseObj):
    attrs = ['repo_owner', 'repo_name', 'star_user', 'timestamp']
    model_name = 'star_event'

    def __init__(self, paper_obj=None):
        super().__init__()
        self.repo_owner = None
        self.repo_name = None
        if paper_obj is not None:
            assert isinstance(paper_obj, Paper)
            self.repo_owner = paper_obj.repo_owner
            self.repo_name = paper_obj.repo_name
        self.star_user = None
        self.timestamp = None

    def from_json_obj(self, json_obj):
        time_str = json_obj['starred_at']
        self.timestamp = datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%SZ')
        if self.timestamp > conf.analyze_date:
            self.timestamp = None
        self.star_user = json_obj['user']['login']


def store_star_event():
    """
    For each repo:
        find all pages of json data;
        for each page of json data:
            for each json_obj in the page:
                store it into db.
    """
    paper_data = get_papers_from_db()
    db_obj_list = list()
    i = 1
    repo_set = set()
    for pd in paper_data:
        if (pd.repo_owner, pd.repo_name) in repo_set:
            continue
        print(i)
        repo_set.add((pd.repo_owner, pd.repo_name))
        json_dir_path = os.path.join(conf.star_path, pd.repo_owner, pd.repo_name)
        if not os.path.exists(json_dir_path):
            continue
        file_names = os.listdir(json_dir_path)
        file_number = len(file_names)
        j = 1
        while j <= file_number:
            json_path = os.path.join(json_dir_path, str(j)+'.json')
            j += 1
            with open(json_path, 'r', encoding='utf-8') as f:
                json_obj_list = simplejson.load(f)
                for json_obj in json_obj_list:
                    se = StarEvent(pd)
                    se.from_json_obj(json_obj)
                    if se.timestamp is not None:
                        db_obj_list.append(se.to_db_obj())
                    if len(db_obj_list) == 20000:
                        db_api = DataBaseApi()
                        db_api.insert_objs(db_obj_list)
                        db_api.close_session()
                        db_obj_list = list()

        i += 1
    if len(db_obj_list) > 0:
        db_api = DataBaseApi()
        db_api.insert_objs(db_obj_list)
        db_api.close_session()


def get_star_events(to_dict=False):
    if to_dict:
        if Cache.cache_star_events_dict is not None:
            return Cache.cache_star_events_dict
        db_api = DataBaseApi()
        table_name = StarEvent.model_name
        star_events = db_api.query_all(table_name)
        star_events_dict = dict()
        for se in star_events:
            se_obj = StarEvent()
            se_obj.from_db_obj(se)
            try:
                star_events_dict[(se_obj.repo_owner, se_obj.repo_name)]
            except KeyError:
                star_events_dict[(se_obj.repo_owner, se_obj.repo_name)] = list()
            star_events_dict[(se_obj.repo_owner, se_obj.repo_name)].append(se_obj)
        db_api.close_session()
        Cache.cache_star_events_dict = star_events_dict
        return star_events_dict
    else:
        if Cache.cache_star_events_list is not None:
            return Cache.cache_star_events_list
        db_api = DataBaseApi()
        table_name = StarEvent.model_name
        star_events = db_api.query_all(table_name)
        star_events_list = list()
        for se in star_events:
            se_obj = StarEvent()
            se_obj.from_db_obj(se)
            star_events_list.append(se_obj)
        Cache.cache_star_events_list = star_events_list
        db_api.close_session()
        return star_events_list


if __name__ == '__main__':
    # get_star_events(to_dict=True)
    store_star_event()
