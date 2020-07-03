from google_scholar_crawler.scholar import *
from pprint import pprint

querier = ScholarQuerier()
settings = ScholarSettings()
querier.apply_settings(settings)
query = SearchScholarQuery()
query.set_phrase('Obfuscated Gradients Give a False Sense of Security: Circumventing Defenses to Adversarial Examples')
# query.set_scope(True)
query.set_num_page_results(1)
querier.send_query(query)
for a in querier.articles:
    pprint(a.as_dict())
