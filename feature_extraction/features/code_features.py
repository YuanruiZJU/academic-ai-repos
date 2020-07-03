from obj import BaseObj
from obj.repo import Repo
from configuration import conf
import os
from obj.repo import get_repo_info
import simplejson as json
from utils import get_csv_content
from subprocess import call


candidate_extends = ['lua', 'py', 'java', 'cpp',
                     'hpp', 'h', 'c', 'ipynb',
                     'cu', 'scala', 'm', 'sh', 'makefile']


cpd_support = ['cpp', 'python', 'scala', 'java', 'matlab']

class CodeFeatures(BaseObj):

    attrs = ['num_modules', 'num_files', 'num_root_files', 'total_lines',
             'contain_docker', 'contain_data', 'num_lang', 'main_language', 'num_duplicates', 'has_shell']

    def __init__(self, ri):
        super().__init__()
        assert isinstance(ri, Repo)
        ri.combine_with_repo_desc()
        sys_repo_path = conf.repo_path
        paper_repo_owner = getattr(ri, 'paper_repo_owner')
        paper_repo_name = getattr(ri, 'paper_repo_name')
        self.paper_repo_owner = paper_repo_owner
        self.paper_repo_name = paper_repo_name
        self.paper_id = ri.paper_id
        self.repo_desc = getattr(ri, 'desc')
        self.repo_path = os.path.join(sys_repo_path, paper_repo_owner, paper_repo_name)
        self.num_modules = 0
        self.num_files = 0
        self.num_root_files = 0
        self.contain_docker = 0
        self.contain_data = 0
        self.use_notebook = 0
        # self.contain_baseline = 0
        self.comments_ratio = 0
        self.total_lines = 0
        self.num_duplicates = 0
        self.has_shell = 0
        self.language_file_map = dict()
        self.exts = set()
        self.stars = ri.stars_count
        self.extract()
        self.main_language = self.get_main_language()
        self.num_lang = len(self.language_file_map.keys())
        # self.calculate_comment_ratio()
        self.calculate_duplicates()

    def extract(self):
        file_names = os.listdir(self.repo_path)
        for fn in file_names:
            file_path = os.path.join(self.repo_path, fn)
            if 'data' in fn.lower():
                self.contain_data = 1

            if fn.startswith('.'):
                continue
            elif os.path.isdir(file_path):
                self.num_modules += 1
            # else:
            #     ext = os.path.splitext(file_path)[-1].lower()
            #     if ext in ['.cpp', '.hpp', '.cxx', '.hxx', '.c', '.h']:
            #         self.num_root_files += 1
            #     elif ext in ['.py', '.python3', '.python', '.python2']:
            #         self.num_root_files += 1
            #     elif ext == '.ipynb':
            #         self.num_root_files += 1
            #     elif ext == '.scala':
            #         self.num_root_files += 1
            #     elif ext == '.java':
            #         self.num_root_files += 1
            #     elif ext == '.m':
            #         self.num_root_files += 1
            #     elif ext == '.cu':
            #         self.num_root_files += 1
            #     elif ext == '.lua':
            #         self.num_root_files += 1
            #     elif ext in ['.sh', '.bash']:
            #         self.num_root_files += 1
            #     elif ext == '.r':
            #         self.num_root_files += 1
            #     elif ext == '.perl':
            #         self.num_root_files += 1
            #     elif ext == '.jl':
            #         self.num_root_files += 1
            elif not file_path.endswith('.md'):
                self.num_root_files += 1
            self.counter(file_path)

    def __add_language_file(self, language):
        try:
            self.language_file_map[language]
        except KeyError:
            self.language_file_map[language] = 0
        self.language_file_map[language] += 1

    def counter(self, path):
        filename = os.path.basename(path)
        if 'docker' in filename.lower():
            self.contain_docker = 1
        # if 'baseline' in filename.lower():
            # self.contain_ baseline = 1
        if os.path.isfile(path):
            ext = os.path.splitext(path)[-1].lower()
            self.exts.add(ext)
            is_code_file = True
            if ext in ['.cpp', '.hpp', '.cxx', '.hxx', '.c', '.h']:
                self.__add_language_file('c/c++')
            elif ext in ['.py', '.python3', '.python', '.python2']:
                self.__add_language_file('python')
            elif ext == '.ipynb':
                self.use_notebook = 1
            elif ext == '.scala':
                self.__add_language_file('scala')
            elif ext == '.java':
                self.__add_language_file('java')
            elif ext == '.m':
                self.__add_language_file('matlab')
            elif ext == '.cu':
                self.__add_language_file('cuda')
            elif ext == '.lua':
                self.__add_language_file('lua')
            elif ext in ['.sh', '.bash', '.bat']:
                self.__add_language_file('shell')
                self.has_shell = 1
            elif ext == '.r':
                self.__add_language_file('r')
            elif ext == '.perl':
                self.__add_language_file('perl')
            elif ext == '.jl':
                self.__add_language_file('julia')
            else:
                is_code_file = False
            if is_code_file:
                self.num_files += 1
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    lines = content.split('\n')
                    if ext != '.ipynb':
                        for l in lines:
                            if l.strip() != '':
                                self.total_lines += 1
                    else:
                        json_content = json.loads(content, strict=False)
                        try:
                            cells = json_content['cells']
                        except KeyError:
                            return
                        for c in cells:
                            if c['cell_type'] == 'code':
                                code = c['source']
                                for l in code:
                                    if l.strip() != '':
                                        self.total_lines += 1

                        try:
                            language = json_content['metadata']['kernelspec']['language']
                            self.__add_language_file(language)
                        except KeyError:
                            pass
        else:
            try:
                files = os.listdir(path)
            except:
                print(path)
                print(os.path.isfile(path))
                raise
            for f in files:
                f_path = os.path.join(path, f)
                self.counter(f_path)

    def get_main_language(self):
        max_language = ''
        max_lang_num = 0
        for key in self.language_file_map.keys():
            if self.language_file_map[key] > max_lang_num:
                max_lang_num = self.language_file_map[key]
                max_language = key
        return max_language

    def calculate_comment_ratio(self):
        cloc_dir = os.path.join(conf.root_path, 'cloc_results')
        cloc_path = os.path.join(cloc_dir, str(self.paper_id) + '.csv')
        if not os.path.exists(cloc_path):
            return
        csv_content = get_csv_content(cloc_path)
        languages = ['python', 'c++', 'c/c++ header', 'bourne shell',
                     'cuda', 'cython', 'matlab', 'c', 'java',
                     'julia', 'scala', 'r']
        comment_lines = 0
        code_lines = 0
        for d in csv_content:
            if d['language'].lower() in languages:
                comment_lines += int(d['comment'])
                code_lines += int(d['code'])
        if code_lines != 0:
            self.comments_ratio = comment_lines / code_lines
        else:
            self.comments_ratio = 0

    def cpd_duplicates(self):
        this_languages = set(self.language_file_map.keys())
        if 'c/c++' in this_languages:
            this_languages.add('cpp')
        join_set = this_languages & set(cpd_support)
        cpd_path = conf.cpd_result_path()
        this_cpd_path = os.path.join(cpd_path, self.paper_repo_owner, self.paper_repo_name)
        if not os.path.exists(this_cpd_path):
            os.makedirs(this_cpd_path)
        if len(join_set) == 0:
            return
        else:
            if 'cpp' in join_set:
                for l in join_set:
                    cmd = 'cpd --minimum-tokens 100 --language %s --files %s --format csv > %s' % \
                          (l, self.repo_path, this_cpd_path + "/" + l + '.csv')
                    print(cmd)
                    os.system(cmd)

    def calculate_duplicates(self):
        this_languages = set(self.language_file_map.keys())
        join_set = this_languages & set(cpd_support)
        cpd_path = conf.cpd_result_path()
        this_cpd_path = os.path.join(cpd_path, self.paper_repo_owner, self.paper_repo_name)
        if not os.path.exists(this_cpd_path):
            os.makedirs(this_cpd_path)
        if len(join_set) > 0:
            for l in join_set:
                cpd_result_path = this_cpd_path + '/' + l + '.csv'
                if os.path.exists(cpd_result_path):
                    with open(cpd_result_path) as f:
                        lines = f.read().strip().split('\n')
                        self.num_duplicates += len(lines) - 1



if __name__ == '__main__':
    repo_info = get_repo_info(combine_star_events=True)
    exts = set()
    i = 0
    for ri in repo_info:
        print(ri.paper_id)

        conference = getattr(ri, 'conf')
        title = getattr(ri, 'title')
        if conference is None or conference == '':
            continue
        if title in conf.excluded_papers:
            continue
        if ri.language == '' or ri.language is None:
            continue
        i += 1
        # print(i)
        # if ri.repo_owner == 'pratulsrinivasan':
        print(CodeFeatures(ri).to_dict())
        # CodeFeatures(ri).cpd_duplicates()





