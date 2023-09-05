import calendar
import locale
import os
import re
from datetime import datetime
from pathlib import Path

from bs4 import BeautifulSoup
from progress.bar import Bar

from src.interfaces.scrap import ScrapInterface, ScrapperMedia
from src.models.article import Article
from src.repositories.scrapper import find_articles, find_document
from utils.path import get_root_dir, get_file_name, get_ext, to_dash_case
from utils.writer import ArticleMetadata, create_path_result, write_article_metadata, write_article


class PikiranRakyatScrapService(ScrapInterface):
    def __init__(self, keyword: str, page_number: int, folder: None | str):
        self.keyword = keyword
        self.page_number = page_number
        self.folder = folder

        self.articles: [Article] = []

    def get_article(self):
        bar = Bar('Retrieving articles information', max=self.page_number)
        for i in range(self.page_number):
            page = i + 1

            # find raw articles
            response = find_articles(self.keyword, page, ScrapperMedia.pikiran_rakyat)
            if response is None:
                print('Failed when retrieving articles information on page', page)
                continue
            soup = BeautifulSoup(response.text, 'html.parser')
            raw_articles = soup.select('.latest__item')

            # concat articles
            self.compose_raw_article(raw_articles)

            bar.next()
        bar.finish()
        return self.articles
        pass

    def compose_raw_article(self, raw_articles):
        for raw_article in raw_articles:
            # init article
            article = Article()
            article.title = raw_article.find('a', attrs={'class': 'latest__link'}).text
            article.link = raw_article.find('a', attrs={'class': 'latest__link'})['href']

            # append retrieved article to articles
            self.articles.append(article)

    def write_document_to_files(self):
        # check is articles has been retrieved
        if len(self.articles) == 0:
            print('please run the get_articles() first to retrieve articles, because documents need it')

        # set folder name if not inputted
        if self.folder is None:
            self.folder = str(calendar.timegm(datetime.now().timetuple()))

        path_folder = str(get_root_dir()) + '/data/' + self.folder + '/'

        Path(path_folder + 'pikiran-rakyat/').mkdir(parents=True, exist_ok=True)

        # get existing filenames
        existing_files = os.listdir(path_folder + 'pikiran-rakyat/')
        existing_files = ['_'.join(get_file_name(a).split('_')[1:]) for a in existing_files if get_ext(a) == 'txt']

        bar = Bar('Retrieving documents', max=len(self.articles))
        for article in self.articles:
            # prepare article filename
            article_filename = to_dash_case(article.title)

            # skip if exists
            if article_filename in existing_files:
                bar.next()
                continue

            write_pikiran_rakyat_article(article, path_folder, article_filename)

            bar.next()
        bar.finish()
        pass


def retrieve_paragraph(soup):
    ps = soup.select('article > p')
    paragraphs = []
    for paragraph in ps:
        text = paragraph.text

        # validate meaningless paragraph
        is_meaningless_paragraph = re.search("^Baca Juga:", text)
        if text == '' or text == ' ' or is_meaningless_paragraph:
            continue
        paragraphs.append(text)

    return paragraphs


def set_prefix_filename(page, soup, article_filename):
    prefix = ''
    date_tag = soup.select('meta[name="pubdate"]')
    if len(date_tag) > 0:
        date_str = date_tag[0].attrs['content']
        locale.setlocale(locale.LC_TIME, "id_ID.utf8")
        date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S%z')
        prefix = str(calendar.timegm(date.timetuple()))
    else:
        print(" Article '" + article_filename + "' doesn't have date")

    return prefix


def create_metadata(soup, article_filename, link, article):
    metadata = ArticleMetadata()
    metadata.link = link

    # write publish date and timestamp
    date_tag = soup.select('meta[name="pubdate"]')
    if len(date_tag) > 0:
        date_str = date_tag[0].attrs['content']
        locale.setlocale(locale.LC_TIME, "id_ID.utf8")
        date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S%z')
        metadata.timestamp = calendar.timegm(date.timetuple())
    else:
        print("Article '" + article_filename + "' doesn't have date")

    # write related text file on yaml file
    metadata.text_file = article_filename + '.txt'

    # write source article
    author = soup.select('meta[name="author"]')
    if len(author) > 0:
        metadata.author = author[0].attrs['content']
    else:
        print("Article '" + article_filename + "' doesn't have author")

    # write title
    metadata.title = article.title
    metadata.media = 'pikiran-rakyat'

    # write id file
    metadata.id = article_filename
    return metadata


def write_pikiran_rakyat_article(article, path_folder, article_filename, page=1, prefix=''):
    # prepare link
    link = article.link

    if page > 1:
        # find pages on an article
        link = link + '?page=' + str(page)

    # retrieve article
    response = find_document(link)
    if response is None:
        print('Failed when retrieving document on url: ', link)
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    siteType = soup.find('meta', attrs={'property': 'og:type', 'content': 'article'})
    if siteType is None:
        return

    pages = soup.select('div.paging__item')

    paragraphs = retrieve_paragraph(soup)

    # get publish timestamp to be prefix filename
    if page == 1:
        prefix = set_prefix_filename(page, soup, article_filename)

    txt_file, yml_file = create_path_result(path_folder, prefix, article_filename, ScrapperMedia.pikiran_rakyat)

    if page == 1:
        metadata = create_metadata(soup,  article_filename, link, article)
        write_article_metadata(yml_file, metadata)

    # write paragraphs to text
    write_article(txt_file, paragraphs)

    if len(pages) > 1 and page < len(pages):
        write_pikiran_rakyat_article(article, path_folder, article_filename, page + 1, prefix)


def pikiran_rakyat_scrape(keyword, page_number, folder):
    print('scrap {} on pikiran-rakyat'.format(keyword))
    scrap_service = PikiranRakyatScrapService(keyword, int(page_number), folder)
    scrap_service.get_article()
    scrap_service.write_document_to_files()
