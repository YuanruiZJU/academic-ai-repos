"""
We directly download the code repo for each paper
using *git clone* cmd
"""
import os
from configuration import conf
from parse import parse
from subprocess import call
from obj.paper import get_papers_from_db
from google_scholar_crawler.title_parser import parse_titles2
import shutil



def clone_repos(paper_obj):
    """
    Originally, we just download repos in each repo directory.
    Unfortunately, we find that some repos share the same name.

    And to avoid missing some repos, we first create directory
    using the repo-owner name, and then, we clone data from github
    and store it in the created directory.

    :param paper_obj: a paper obj whose attributes are from database
    """
    pd = paper_obj
    repo_name = pd.repo_name
    repo_owner = pd.repo_owner
    repo_owner_path = os.path.join(conf.repo_path, repo_owner)
    url = pd.code_link
    if not os.path.exists(repo_owner_path):
        os.makedirs(repo_owner_path)
    repo_path = os.path.join(repo_owner_path, repo_name)
    if os.path.exists(repo_path) and os.path.isdir(repo_path):
        return
    os.chdir(repo_owner_path)
    print("cloning %s" % url)
    call('git clone ' + url)

# Just a temporary function
def move_project_to_owner_dir():
    papers = get_papers_from_db()
    repo_num_map = dict()
    for pd in papers:
        repo_name = pd.repo_name
        try:
            repo_num_map[repo_name]
        except KeyError:
            repo_num_map[repo_name] = 0
        repo_num_map[repo_name] += 1

    for pd in papers:
        repo_name = pd.repo_name
        repo_owner = pd.repo_owner
        old_repo_path = os.path.join(conf.root_path, 'repos', repo_name)
        if repo_num_map[repo_name] == 1 and os.path.exists(old_repo_path):
            repo_owner_path = os.path.join(conf.repo_path, repo_owner)
            if not os.path.exists(repo_owner_path):
                os.makedirs(repo_owner_path)
            new_repo_path = os.path.join(repo_owner_path, repo_name)
            os.rename(old_repo_path, new_repo_path)
        else:
            clone_repos(pd)



def clean_dir_and_get_new_repos():
    correct_title, title_url_map = parse_titles2()
    for t in title_url_map.keys():
        url = title_url_map[t]
        terms = url.split('/')
        repo_name = terms[-1]
        repo_owner = terms[-2]
        if repo_name == '':
            repo_name = terms[-2]
            repo_owner = terms[-3]
        repo_path = os.path.join(conf.repo_path, repo_owner, repo_name)
        if os.path.exists(repo_path):
            print(repo_path)
        # repo_owner_path = os.path.join(conf.repo_path, repo_owner)
        # if not os.path.exists(repo_owner_path):
        #     os.makedirs(repo_owner_path)
        # os.chdir(repo_owner_path)
        # print("cloning %s" % url)
        # call('git clone ' + url)


if __name__ == '__main__':
    paper_data = get_papers_from_db()
    for pd in paper_data:
        clone_repos(pd)
    # clean_dir_and_get_new_repos()


