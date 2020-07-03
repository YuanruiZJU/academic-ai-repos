import csv
from configuration import conf
import os


def dict_list2csv(dict_list, file_path, fieldnames):
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for d in dict_list:
            writer.writerow(d)


def get_readme_doc_from_path(path):
    filenames = os.listdir(path)
    readme_file_set = set()
    for fn in filenames:
        if fn.lower().startswith('readme.') or fn.lower() == 'readme':
            readme_file_set.add(fn.lower())
    if len(readme_file_set) == 0:
        return ''
    elif 'readme.md' in readme_file_set:
        return os.path.join(path, 'readme.md')
    else:
        assert len(readme_file_set) == 1
        return os.path.join(path, list(readme_file_set)[0])


def get_readme_path(repo_owner, repo_name):
    sys_repo_path = conf.repo_path
    this_repo_path = os.path.join(sys_repo_path, repo_owner, repo_name)
    return get_readme_doc_from_path(this_repo_path)


def get_csv_content(path):
    with open(path, 'r') as f:
        file_content = f.read()
    lines = file_content.split('\n')
    dict_list = list()
    for l in lines[1:]:
        if l.strip() == '':
            break
        terms = l.split(',')
        t = dict()
        t['language'] = terms[1].lower()
        t['comment'] = int(terms[3])
        t['code'] = int(terms[4])
        dict_list.append(t)
    return dict_list


def in_our_extensions(path):
    ext = os.path.splitext(path)[1]
    extensions = ['.cpp', '.hpp', '.cxx', '.hxx', '.c', '.h',
                  '.py', '.python3', '.python', '.python2',
                  '.ipynb', '.scala', '.java', '.m', '.cu',
                  '.sh', '.bash', '.r', '.perl', '.jl']
    return ext in extensions


