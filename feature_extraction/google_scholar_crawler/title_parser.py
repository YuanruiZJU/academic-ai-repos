import re
import os
from obj.cache import Cache


def parse_title_scholar():
    if Cache.cache_citations is not None:
        return Cache.cache_citations

    current_dir = os.path.dirname(__file__)
    i = 0
    with open(os.path.join(current_dir, 'titles'), 'r', encoding='utf-8') as f:
        citations = dict()
        file_content = f.read()
        for line in file_content.split('\n'):
            i += 1
            if line.startswith('?') or line.startswith('#'):
                print(line)
            elif line == '':
                continue
            else:
                match = re.match(r'[0-9]+', line).group()
                citation = int(match)
                citations[i] = citation
                title_start =line.index('}') + 1
                title = line[title_start:]
                title = title.lstrip().rstrip()
                citations[title] = citation
    Cache.cache_citations = citations
    return citations


def parse_titles2():
    if Cache.cache_correct_titles is not None:
        return Cache.cache_correct_titles, Cache.cache_title_url
    current_dir = os.path.dirname(__file__)
    title_list = list()
    title_url_map = dict()
    with open(os.path.join(current_dir, 'titles2'), 'r', encoding='utf-8') as f:
        file_content = f.read()
        lines = file_content.split('\n')
        for l in lines:
            if l.startswith('1'):
                temp = l[2:]
                if temp.startswith('{'):
                    title = temp[temp.index('}') + 2:].lstrip().rstrip()
                else:
                    title = temp.lstrip().rstrip()
                title_list.append(title)
            else:
                temp = l[2:]
                if re.match(r'\{https://github.com/\S+\}', temp):
                    l_index = temp.index('{') + 1
                    r_index = temp.index('}')
                    url = temp[l_index:r_index]
                    title = temp[r_index+2:].lstrip().rstrip()
                    title_list.append(title)
                    title_url_map[title] = url
    Cache.cache_correct_titles = title_list
    Cache.cache_title_url = title_url_map
    return title_list, title_url_map


if __name__ == '__main__':
    parse_titles2()