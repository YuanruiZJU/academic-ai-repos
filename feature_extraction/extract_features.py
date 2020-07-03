from features.abstract_features import AbstractTopicModelFeatures
from features.code_features import CodeFeatures
from features.readme_features import ReadmeFeatures
from features.repometa_features import RepoMetaFeatures
from configuration import conf
from copy import deepcopy


abs_attrs = AbstractTopicModelFeatures.attrs
code_attrs = CodeFeatures.attrs
readme_attrs = deepcopy(ReadmeFeatures.attrs)
repometa_attrs = RepoMetaFeatures.attrs

readme_attrs.remove('contain_docker')
readme_attrs.remove('contain_data')

all_attrs = abs_attrs + code_attrs + readme_attrs + repometa_attrs
all_attrs.append('stars')


if __name__ == '__main__':
    from obj.repo import get_repo_info

    repo_info = get_repo_info(combine_star_events=True)
    dict_list = list()
    i = 0
    for ri in repo_info:
        print(i)
        if ri.year == 2014:
            continue
        conference = getattr(ri, 'conf')
        title = getattr(ri, 'title')
        if conference is None or conference == '':
            continue
        if title in conf.excluded_papers:
            continue
        if ri.language == '' or ri.language is None:
            continue
        abs_feature_dict = AbstractTopicModelFeatures(ri).to_dict()
        code_feature_dict = CodeFeatures(ri).to_dict()
        readme_feature_dict = ReadmeFeatures(ri).to_dict()
        rm_feature_dict = RepoMetaFeatures(ri).to_dict()
        all_feature_dict = dict()
        if code_feature_dict['contain_docker'] + readme_feature_dict['contain_docker'] > 0:
            contain_docker = 1
        else:
            contain_docker = 0
        if code_feature_dict['contain_data'] + readme_feature_dict['contain_data'] > 0:
            contain_data = 1
        else:
            contain_data = 0
        combine_dict1 = dict(abs_feature_dict, **code_feature_dict)
        combine_dict2 = dict(combine_dict1, **readme_feature_dict)
        combine_dict3 = dict(combine_dict2, **rm_feature_dict)
        combine_dict3['contain_docker'] = contain_docker
        combine_dict3['contain_data'] = contain_data
        combine_dict3['stars'] = ri.stars_count
        dict_list.append(combine_dict3)
        i += 1
    from utils import dict_list2csv

    dict_list2csv(dict_list, file_path='D://all_features201902.csv',
                  fieldnames=all_attrs)

