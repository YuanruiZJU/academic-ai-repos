def get_star_count(project_name):
    """
    Get the number of stars for a given project.

    Since we set page_size as 100, we only need to
    calculate number of star (json units) in the last
    file.
    """
    project_star_path = os.path.join(conf.star_path, project_name, 'stars')
    file_list = os.listdir(project_star_path)
    last_file_name = str(len(file_list)) + '.json'
    last_file_path = os.path.join(project_star_path, last_file_name)
    with open(last_file_path, 'r') as f:
        json_string = simplejson.load(f)
        star_count = len(json_string)
    star_count += (len(file_list)-1) * 100
    return star_count