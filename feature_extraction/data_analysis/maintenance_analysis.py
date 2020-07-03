from git_analysis import analyze_git_logs
from git_analysis import analyze_git_numstat
from configuration import conf


if __name__ == '__main__':
    from obj.repo import get_repo_info

    repo_info = get_repo_info(combine_star_events=True)
    dict_list = list()
    i = 0

    for ri in repo_info:
        # print(i)
        if ri.year == 2018 and ri.conf == 'NIPS':
            continue
        conference = getattr(ri, 'conf')
        title = getattr(ri, 'title')
        if conference is None or conference == '':
            continue
        if title in conf.excluded_papers:
            continue
        if ri.language == '' or ri.language is None:
            continue
        paper_repo_owner = getattr(ri, 'paper_repo_owner')
        paper_repo_name = getattr(ri, 'paper_repo_name')
        logs = analyze_git_logs.retrieve_git_logs(paper_repo_owner, paper_repo_name)
        print(len(logs), 'https://github.com/'+paper_repo_owner+'/'+paper_repo_name, ri.title)
        stat_dict = analyze_git_numstat.get_numstats(paper_repo_owner, paper_repo_name)
        i += 1
