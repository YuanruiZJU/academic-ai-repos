from obj.repo import get_repo_info
from datetime import datetime
from configuration import conf


def definite_time_stars(days=90):
    ri_obj_list = get_repo_info(to_dict=False)
    repo_set = set()
    statistics = 0
    for ri in ri_obj_list:
        if (ri.repo_owner, ri.repo_name) in repo_set:
            continue
        ri.combine_with_star_events()
        repo_set.add((ri.repo_owner, ri.repo_name))
        star_events = getattr(ri, 'star_events')
        good_stars = 0
        for se in star_events:
            if (se.timestamp - ri.created_at).days < days:
                good_stars += 1
        if len(star_events) > 0:
            print(good_stars / len(star_events), ri.conf, ri.created_at, ri.stars_count)
            if good_stars / len(star_events) > 0.5:
                statistics += 1
    print(statistics)


def percentage_star_at_study_date():
    """
    We can first know that whether our analysis date
    is a good date.
    """
    study_year = 2017
    study_conf = 'CVPR'
    ri_obj_list = get_repo_info(to_dict=False, combine_star_events=True)
    repo_set = set()
    for ri in ri_obj_list:
        if (ri.repo_owner, ri.repo_name) in repo_set:
            continue
        if ri.conf != study_conf or ri.year != study_year:
            continue
        repo_set.add((ri.repo_owner, ri.repo_name))
        star_events = getattr(ri, 'star_events')
        for se in star_events:
            pass





if __name__ == '__main__':
    definite_time_stars()
    # star_events_each_day()
