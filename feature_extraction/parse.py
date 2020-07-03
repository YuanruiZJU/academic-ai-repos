"""
Written by Yuanrui Fan (yrfan@zju.edu.cn)

We just treat markdown file as *Pure-Text* file.

Our goal is to extract the table that lists the
paper link and code repo in a Markdown File.
"""

import re


def parse_group(s):
    """
    We need to parse the string format
    [...](...)
    """
    groups = s.split('](')
    title = groups[0][2:]
    paper_link = groups[1][:-2]
    return title, paper_link


def parse(path):
    """
    Find each line with the format:
    | Title | conf | code | Stars |
    """
    data = list()
    year = 0
    with open(path, 'rt', encoding='utf-8') as f:
        for line in f:
            paper = dict()

            if re.search(r'##\s+\d+', line) is not None:
                year = int(line.split()[-1])

            if line.startswith('| [') and '[code]' in line:
                groups = line.split('|')
                paper['title'], paper['link'] = parse_group(groups[1])
                paper['conf'] = groups[2]
                paper['code_link'] = parse_group(groups[3])[1]
                paper['n_star'] = int(groups[4])
                assert(year != 0)
                paper['year'] = year
                data.append(paper)
    return data


if __name__ == '__main__':
    from configuration import conf
    data = parse(conf.md_path)
    print(len(data))



