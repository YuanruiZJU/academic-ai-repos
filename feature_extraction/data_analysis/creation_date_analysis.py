from obj.repo import get_repo_info
from datetime import datetime
from obj.repo import Repo


def year_month2date(year, month):
    date_str = str(year) + '-' + str(month) + '-1'
    return datetime.strptime(date_str, '%Y-%m-%d')


def in_year_month(date_obj, year, month):
    assert(isinstance(date_obj, datetime))
    if date_obj.year == year and date_obj.month == month:
        return True
    return False


def extract_year_month(ri_obj):
    assert(isinstance(ri_obj, Repo))
    return ri_obj.created_at.year, ri_obj.created_at.month


if __name__ == '__main__':
    ri_objs = get_repo_info(to_dict=False, combine_paper=True)
    ri_set = set()
    each_month_counter = dict()
    study_conf = 'ICML'
    for ri in ri_objs:
        if (ri.repo_owner, ri.repo_name) in ri_set:
            continue
        if ri.conf != study_conf:
            continue
        ri_set.add((ri.repo_owner, ri.repo_name))
        year, month = extract_year_month(ri)
        try:
            each_month_counter[(year, month)]
        except KeyError:
            each_month_counter[(year, month)] = 0
        each_month_counter[(year, month)] += 1

    show_year = 2017
    for m in range(1, 13):
        try:
            print(show_year, m, each_month_counter[(show_year, m)])
        except KeyError:
            print(show_year, m, 0)




