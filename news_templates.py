# from bs4 import BeautifulSoup
import re


class NewsTemplates:
    def __init__(self, domain, soup):
        self.domain = domain
        self.soup = soup

    def get_content_from_template(self):
        if self.domain == 'ria.ru':
            return self.ria_news()
        elif self.domain == 'news.rambler.ru':
            return self.rambler_news()
        elif self.domain == 'www.gazeta.ru':
            return self.gazeta_news()
        elif self.domain == 'lenta.ru':
            return self.lenta_news()
        else:
            return self.base_news()

    def ria_news(self):
        content = self.soup.find_all(['div', 'h1', 'h2', 'h3'], {'class': re.compile('article__(text|title)')})
        return content

    def rambler_news(self):
        content = self.soup.find_all(['div', 'h1', 'h2', 'h3'], {'class': re.compile('__(paragraph|title)')})
        return content

    def gazeta_news(self):
        content = self.soup.find(['article'], {'class': re.compile('article-text')})
        content = content.find_all(['p', 'h1', 'h2', 'h3'])
        return content

    def lenta_news(self):
        content = self.soup.find(['div'], {'class': re.compile('topic__content')})
        content = content.find_all(['p', 'h1'])
        return content

    def base_news(self):
        content = self.soup.find_all(['p', 'h1', 'h2', 'h3'])
        return content
