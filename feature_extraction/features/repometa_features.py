from obj.repo import Repo
from obj import BaseObj
from configuration import conf


class RepoMetaFeatures(BaseObj):
    """
    For this dimension, we leverage the information
    stored in json files of repo meta info.
    """
    #
    attrs = [ 'from_organization','has_license']
    model_name = 'repo_meta_features'

    def __init__(self, ri):
        super().__init__()
        assert isinstance(ri, Repo)
        self.language = ri.language
        if ri.organization == '' or ri.organization is None:
            self.from_organization = "personal"
        else:
            self.from_organization = "organization"
        if ri.license == '' or ri.license is None:
            self.has_license = 0
        else:
            self.has_license = 1
        self.publish_time = (conf.analyze_date - ri.created_at).days
        self.stars = ri.stars_count

    def print_as_dict(self):
        print(self.to_dict())


if __name__ == '__main__':
    from obj.repo import get_repo_info
    repo_info = get_repo_info(combine_star_events=True)
    dict_list = list()
    for ri in repo_info:
        conference = getattr(ri, 'conf')
        title = getattr(ri, 'title')
        if conference is None or conference == '':
            continue
        if title in conf.excluded_papers:
            continue
        if ri.language == '' or ri.language is None:
            continue
        dict_list.append(RepoMetaFeatures(ri).to_dict())
    from utils import dict_list2csv
    dict_list2csv(dict_list, file_path='D://repo_meta_features.csv', fieldnames=RepoMetaFeatures.attrs)



