from google_scholar_crawler.scholar import *
import simplejson
import os

class ScholarCrawler:
    def __init__(self, title, paper_id):
        self.paper_id = paper_id
        self.title = title
        self.querier = ScholarQuerier()
        settings = ScholarSettings()
        self.querier.apply_settings(settings)
        self.sleep_time = 10
        self.end_crawl = False

        print('Crawling scholar data for paper %s' % self.title)
        if self.check_data_on_disk():
            self.end_crawl = True

    def check_data_on_disk(self):
        scholar_path = 'scholar'
        store_path = os.path.join(scholar_path, str(self.paper_id) + '.json')
        return os.path.exists(store_path)

    def scholar_to_disk(self):
        articles = self.crawl_for_paper()
        if len(articles) == 0:
            return False
        scholar_path = 'scholar'
        if not os.path.exists(scholar_path):
            os.makedirs(scholar_path)
        store_path = os.path.join(scholar_path, str(self.paper_id) + '.json')
        with open(store_path, 'w', encoding='utf-8') as f:
            simplejson.dump(articles, f)
        return True

    def crawl_for_paper(self):
        query = SearchScholarQuery()
        query_phrase = self.title.lower()
        query.set_phrase(query_phrase)
        query.set_scope(True)
        query.set_num_page_results(10)
        self.querier.send_query(query)
        result_articles = list()
        for a in self.querier.articles:
            result_articles.append(a.as_dict())
        return result_articles


if __name__ == '__main__':
    with open('titles', 'r', encoding='utf-8') as f:
        titles = f.read().split('\n')
    start_number = 65
    i = 0
    for t in titles:
        if t != '':
            i += 1
            if i < start_number:
                continue
            sc = ScholarCrawler(t, i)
            try:
                response = sc.scholar_to_disk()
                print(i)
                if not response:
                    break
            except:
                pass

