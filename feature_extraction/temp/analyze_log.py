from configuration import conf
import os


log_file = 'download_log.txt'
log_path = os.path.join(conf.root_path, log_file)


with open(log_path, 'rt') as f:
    last_line = None
    has_problem_repo = list()
    for line in f:
        if line.startswith('Cloning') or line.startswith('Checking') or line.startswith('Filtering'):
            last_line = line
            continue
        else:
            if last_line is not None:
                print(last_line)
                if last_line.startswith('Cloning'):
                    has_problem_repo.append(last_line[14:-5])
            print(line)
            last_line = None

    print(has_problem_repo)

