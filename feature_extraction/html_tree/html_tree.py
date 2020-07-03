import bs4


class HtmlTreeUnit:
    def __init__(self, soup_obj, parent_tree_unit, index, html_elements):
        self.soup_obj = soup_obj
        if isinstance(soup_obj, bs4.element.Tag):
            self.tag = soup_obj.name
        else:
            assert isinstance(soup_obj, bs4.element.NavigableString)
            self.tag = None
        self.parent_tree_unit = parent_tree_unit
        self.index = index
        self.children_soup_obj = list()
        assert isinstance(html_elements, list)
        self.global_index = len(html_elements)
        self.html_elements = html_elements
        self.html_elements.append(self)
        self.add_children()

    def add_children(self):
        if isinstance(self.soup_obj, bs4.element.Tag):
            soup_children = self.soup_obj.children
            i = 0
            for soup_obj in soup_children:
                if isinstance(soup_obj, bs4.element.NavigableString):
                    string = str(soup_obj)
                    if string.rstrip().lstrip() == '':
                        continue

                child_tree_unit = HtmlTreeUnit(soup_obj, self, i, self.html_elements)
                self.children_soup_obj.append(child_tree_unit)
                i += 1

    def find_all(self, tag_name):
        ret_list = list()
        for c in self.children_soup_obj:
            assert isinstance(c, HtmlTreeUnit)
            if c.tag == tag_name:
                ret_list.append(c)
            else:
                ret_list += c.find_all(tag_name)
        return ret_list

    def find_previous(self, tag_name_prefix):
        temp_index = self.global_index - 1
        while temp_index >= 0:
            html_tree_unit = self.html_elements[temp_index]
            assert isinstance(html_tree_unit, HtmlTreeUnit)
            if html_tree_unit.tag.startswith(tag_name_prefix):
                return html_tree_unit
            temp_index -= 1
        return None

    def find_next(self, tag_name):
        pass


def create_html_tree(html_soup):
    return HtmlTreeUnit(html_soup, None, None, list())

