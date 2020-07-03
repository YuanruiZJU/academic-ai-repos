# -*- coding: utf-8 -*-
import os
import subprocess
from configuration import conf


def wrapper_change_path(func):
    cwd = os.getcwd()

    def inner(*args, **kwargs):
        return func(*args, **kwargs)


    os.chdir(cwd)
    return inner


class GitLog:
    commands = {
        'meta': 'meta_cmd',
        'numstat': 'numstat_cmd'
    }

    def __init__(self):
        self.meta_cmd = 'git log --reverse --all --pretty=format:\"commit: %H%n' \
                        'parent: %P%n' \
                        'author: %an%n' \
                        'author email: %ae%n' \
                        'time stamp: %at%n' \
                        'committer: %cn%n' \
                        'committer email: %ce%n' \
                        '%B%n\"  '
        self.numstat_cmd = 'git log --pretty=format:\"commit: %H\" --numstat -M --all --reverse '


    @wrapper_change_path
    def run(self, repo_owner, repo_name):
        target_path = os.path.join(conf.repo_path, repo_owner, repo_name)
        os.chdir(target_path)
        for cmd_name in GitLog.commands.keys():
            print (cmd_name)
            cmd = getattr(self, GitLog.commands.get(cmd_name))
            log_path = os.path.join(conf.root_path, 'log_path', repo_owner, repo_name)
            if not os.path.exists(log_path):
                os.makedirs(log_path)
            log_file_path = os.path.join(log_path, cmd_name)
            out = subprocess.check_output(cmd, shell=True).decode('utf-8',errors='ignore')
            with open(log_file_path,'w', encoding='utf-8') as f_obj2:
                f_obj2.write(out)


if __name__ == '__main__':
    gl = GitLog()
    from obj.repo import get_repo_info

    repo_info = get_repo_info(combine_star_events=True)
    i = 0
    for ri in repo_info:
        print(i)
        if ri.year == 2018 and ri.conf == 'NIPS':
            continue
        conference = getattr(ri, 'conf')
        title = getattr(ri, 'title')
        paper_repo_owner = getattr(ri, 'paper_repo_owner')
        paper_repo_name = getattr(ri, 'paper_repo_name')
        if conference is None or conference == '':
            continue
        if title in conf.excluded_papers:
            continue
        if ri.language == '' or ri.language is None:
            continue
        gl.run(paper_repo_owner, paper_repo_name)


