import requests
import textwrap
import sys
import re

from bs4 import BeautifulSoup
from urllib.parse import urlparse
from parsing_scheme import *
from news_templates import NewsTemplates
from fake_useragent import UserAgent


HEADER = {'User-Agent': str(UserAgent().chrome)}


class LinkCleaner:
    """
    Чистильщик ссылок. Принимает элемент(bs4), возвращает тоже елемент(bs4)
    """
    def __init__(self, element):
        self.element = element

    # Базовая очистка. Проходимся по всему контенту элемента если есть тег <a>, вырезаем его оставляя href
    def link_clean(self, position=LINK_PARSER):
        if self.element.a:
            links = self.element.find_all('a')
            for link in links:
                try:
                    index = self.element.index(link)
                    if position == 'after':
                        self.element.contents[index].replaceWith('{} [{}]'.format(link.string, link['href']))
                    elif position == 'before':
                        self.element.contents[index].replaceWith('[{}] {}'.format(link['href'], link.string))
                except ValueError:
                    pass
        return self.element


class TextTransform:
    """
    Обработчик текста
    Принимает текст, возвращает текст
    """
    def __init__(self, text, tag_name=None):
        self.text = text
        self.tag_name = tag_name

    # Базовое форматирование.
    def base_transform(self, ident=IDENT):
        if ident:
            self.ident_line()
        self.line_break()
        if self.tag_name in ('h1', 'h2', 'h3'):
            self.text_upper()
        return self.text

    def text_upper(self):
        self.text = self.text.upper()

    def line_break(self, width=LINE_BREAK_WIDTH):
        wrap = textwrap.wrap(self.text, width=width)
        self.text = '\n'.join(wrap) + '\n'

    def ident_line(self):
        if self.tag_name not in ('h1', 'h2', 'h3'):
            self.text = '\t' + self.text


class ContentParser:
    """
    Основной класс, получает, преобразует, сохраняет.
    Вызывается при запуске программы с основным методом parse_content
    """
    regex_link = re.compile('(/[\S]*/)([a-z\d_]*)')

    def __init__(self, url, regex_link=regex_link):
        self.url = url
        self.domain = urlparse(url).hostname
        self.path = re.search(regex_link, urlparse(url).path).group(1).replace('/', '\\')
        self.file_name = re.search(regex_link, urlparse(url).path).group(2) or 'index'

    def get_content(self):
        response = requests.get(self.url, headers=HEADER).text
        soup = BeautifulSoup(response, 'html.parser')
        content = NewsTemplates(self.domain, soup).get_content_from_template()
        return content

    def parse_content(self, link=LINK):
        clean_content = []
        for element in self.get_content():
            if link:
                element = LinkCleaner(element).link_clean()
            text = TextTransform(element.text, element.name).base_transform()
            clean_content.append(text)
        self.save_content(clean_content)

    def save_content(self, content):
        path = '{}{}'.format(CUR_DIR, self.path)
        file = '{}{}'.format(self.file_name, '.txt')
        if not os.path.exists(path):
            os.makedirs(path)
        with open(path + file, 'w+', encoding='utf-8') as out:
            for line in content:
                out.write(line + '\n')


if __name__ == '__main__':
    try:
        site = ContentParser(sys.argv[1])
        site.parse_content()
    except IndexError:
        print('Укажите обязательный аргумент в виде URL')

