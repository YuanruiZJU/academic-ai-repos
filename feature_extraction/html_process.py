import bs4
from paper_analysis.prepare import get_lemma3
from paper_analysis.prepare import tokenize

candidate_framework = ['tensorflow', 'pytorch', 'torch',
                       'chainer', 'caffe', 'matlab',
                       'mxnet', 'paddlepaddle']


def stem_one_sentence(text):
    tokens = tokenize(text)
    stem_words = [get_lemma3(token) for token in tokens]
    stem_text = ' '.join(stem_words)
    return stem_text


class HtmlProcessing:
    def __init__(self, html_soup):
        assert isinstance(html_soup, bs4.element.Tag)
        self.soup = html_soup
        self.cache_header_soups = None

    def get_all_headers(self):
        if self.cache_header_soups is not None:
            return self.cache_header_soups
        header_prefix = 'h'
        candidate_header = [1, 2, 3, 4, 5, 6]
        headers_soup = list()
        for ch in candidate_header:
            headers = self.soup.get_all(header_prefix + str(ch))
            for h in headers:
                headers_soup.append(h)
            headers_soup += headers
        self.cache_header_soups = headers_soup
        return headers_soup

    def get_all_requirements(self):
        headers = self.get_all_headers()
        for header_soup in headers:
            header_text = header_soup.get_text()
            stem_text = stem_one_sentence(header_text)
            if get_lemma3('requirement') in stem_text:
                pass

    def get_all_result_imgs(self):
        headers = self.get_all_headers()
        result_header_soup = None
        for header_soup in headers:
            header_text = header_soup.get_text()
            stem_text = stem_one_sentence(header_text)
            if get_lemma3('result') in stem_text:
                result_header_soup = header_soup

    def get_all_tables(self):
        tables = self.soup.get_all('center')
        for t in tables:
            assert '|' in t.get_text()
        return len(tables)

    def get_all_lists(self):
        ol_lists = self.soup.get_all('ol')
        ul_lists = self.soup.get_all('ul')
        all_lists = ol_lists + ul_lists

        for l in all_lists:
            if 'pytorch'



if __name__ == '__main__':
    print(stem_one_sentence('requirement'))


