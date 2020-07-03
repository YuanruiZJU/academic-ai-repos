from obj.paper import get_papers_from_db
from github_data_crawler.repo_stargazer import StargazerCrawler
from github_data_crawler.repo_info import RepoInfoCrawler
import time


def crawl_repo_stargazer():
    papers = get_papers_from_db()
    for p in papers:
        s = StargazerCrawler(p)
        while not s.end_crawl:
            result_json = s.get_next_page()
            s.result_to_disk(result_json)
            time.sleep(0.5)


def crawl_repo_info():
    papers = get_papers_from_db()
    for p in papers:
        r = RepoInfoCrawler(p)
        r.crawl_to_disk()


if __name__ == '__main__':
    crawl_repo_stargazer()
    # crawl_repo_info()


