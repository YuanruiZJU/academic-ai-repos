from obj.repo import get_repo_info
from configuration import conf
import os
from subprocess import call


cloc_results_path = os.path.join(conf.root_path, 'cloc_results')


if __name__ == '__main__':
    repo_info = get_repo_info(combine_star_events=True)
    dict_list = list()
    i = 0
    for ri in repo_info:
        conference = getattr(ri, 'conf')
        title = getattr(ri, 'title')
        paper_id = ri.paper_id
        print(paper_id)
        paper_repo_owner = getattr(ri, 'paper_repo_owner')
        paper_repo_name = getattr(ri, 'paper_repo_name')
        if conference is None or conference == '':
            continue
        if title in conf.excluded_papers:
            continue
        if ri.language == '' or ri.language is None:
            continue
        repo_path = os.path.join(conf.repo_path, paper_repo_owner, paper_repo_name)
        os.chdir(repo_path)
        dest_path = os.path.join(cloc_results_path, str(paper_id) + '.csv')
        cmd = 'cloc . --csv --out=%s --exclude-ext=json' % dest_path
        call(cmd)

