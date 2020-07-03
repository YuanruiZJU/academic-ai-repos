from obj.repo import get_repo_info
from obj.paper import get_papers_from_db


def get_anomaly_repo():
    repo_info_list = get_repo_info(to_dict=False)
    ret_map = dict()
    paper_data = get_papers_from_db()
    for ri in repo_info_list:
        key = (ri.repo_owner, ri.repo_name)
        try:
            ret_map[key]
        except KeyError:
            ret_map[key] = list()
        ret_map[key].append(ri.paper_id)
    for key in ret_map.keys():
        if len(ret_map[key]) > 1:
            for pid in ret_map[key]:
                print(paper_data[pid-1].title)


if __name__ == '__main__':
    get_anomaly_repo()