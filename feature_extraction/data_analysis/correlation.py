from obj.repo import get_repo_info
from google_scholar_crawler.title_parser import parse_title_scholar
from obj.paper import get_papers_from_db
import scipy
import scipy.stats


paper_scholar_map = dict()

citations = parse_title_scholar()
repo_info = get_repo_info(to_dict=True, combine_star_events=True)
paper_data = get_papers_from_db()

sc_list = list()
citation_list = list()

conf = 'ICML'
year = 2018

for pd in paper_data:
    paper_id = getattr(pd, 'id')
    try:
        ri = repo_info[paper_id]
    except KeyError:
        continue
   # pd.conf.lstrip().rstrip() == conf and
    if pd.year == year:
        stars_count = ri.stars_count
        citation = citations[pd.title]
        sc_list.append(stars_count)
        citation_list.append(citation)

print(len(citation_list))


print(scipy.stats.spearmanr(sc_list, citation_list))
