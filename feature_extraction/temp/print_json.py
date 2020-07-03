import pprint
import simplejson
from configuration import conf
import os


path = os.path.join(conf.root_path, 'star_statistic/adagan', 'stars', '1.json')
with open(path, 'r', encoding='utf-8') as f:
    json_obj = simplejson.load(f)
    pprint.pprint(json_obj)
