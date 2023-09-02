import locale
import os
from pathlib import Path

from bs4 import BeautifulSoup

from src.interfaces.scrap import ScrapInterface, ScrapperMedia
from src.models.article import Article
from progress.bar import Bar
import re
import datetime
import calendar

from src.repositories.scrapper import find_articles, find_document
from utils.writer import write_article, ArticleMetadata, write_article_metadata, create_path_result
from utils.path import get_root_dir, to_dash_case, get_ext, get_file_name, create_path_folder_if_not_exists


class DetikScrapService(ScrapInterface):
    def __init__(self, keyword: str, page_number: int, folder: None | str):
        self.keyword = keyword
        self.page_number = page_number
        self.folder = folder

        self.articles: [Article] = []

    def get_articles(self):
        bar = Bar('Retrieving articles information', max=self.page_number)
        for i in range(self.page_number):
            page = i + 1

            # find raw articles
            response = find_articles(self.keyword, page, ScrapperMedia.detik)
            if response is None:
                print('Failed when retrieving articles information on page', page)
                continue
            soup = BeautifulSoup(response.text, 'html.parser')
            raw_articles = soup.find_all('article')

            # concat articles
            self.compose_raw_article(raw_articles)

            bar.next()
        bar.finish()
        return self.articles

    def compose_raw_article(self, raw_articles):
        for raw_article in raw_articles:
            link = raw_article.find('a')['href']

            # init article
            article = Article()
            article.title = raw_article.find('h2', attrs={'class': 'title'}).text
            article.link = link

            # append retrieved article to articles
            self.articles.append(article)

    def write_document_to_files(self):
        # check is articles has been retrieved
        if len(self.articles) == 0:
            print('please run the get_articles() first to retrieve articles, because documents need it')

        # set folder name if not inputted
        if self.folder is None:
            self.folder = str(calendar.timegm(datetime.datetime.now().timetuple()))

        path_folder = str(get_root_dir()) + '/data/' + self.folder + '/'

        Path(path_folder + 'detik/').mkdir(parents=True, exist_ok=True)

        # get existing filenames
        existing_files = os.listdir(path_folder + 'detik/')
        existing_files = ['_'.join(get_file_name(a).split('_')[1:]) for a in existing_files if get_ext(a) == 'txt']

        bar = Bar('Retrieving documents', max=len(self.articles))
        for article in self.articles:
            # prepare article filename
            article_filename = to_dash_case(article.title)

            # skip if exists
            if article_filename in existing_files:
                bar.next()
                continue

            write_detik_article(article, path_folder, article_filename)

            bar.next()
        bar.finish()


def retrieve_paragraph(soup):
    ps = soup.select('div.detail__body-text > p')
    paragraphs = []
    for paragraph in ps:
        text = paragraph.text

        # validate meaningless paragraph
        is_page_anchor_paragraph = re.search("\n\n\n\nHalaman\n\n", text)
        is_meaningless_paragraph = re.search("^Simak.*di halaman berikutnya.$", text)
        if text == '' or text == ' ' or is_page_anchor_paragraph or is_meaningless_paragraph:
            break
        paragraphs.append(text)

    return paragraphs


def set_prefix_filename(page, soup, article_filename):
    prefix = ''
    date_tag = soup.select('meta[name="publishdate"]')
    if len(date_tag) > 0:
        date_str = date_tag[0].attrs['content'].replace(' WIB', '')
        locale.setlocale(locale.LC_TIME, "id_ID.utf8")
        date = datetime.datetime.strptime(date_str, '%Y/%m/%d %H:%M:%S')
        prefix = str(calendar.timegm(date.timetuple()))
    else:
        print(" Article '" + article_filename + "' doesn't have date")

    return prefix


def create_metadata(soup, article_filename, link, article):
    metadata = ArticleMetadata()
    # write paragraphs to text
    author = soup.select('div.detail__author')

    # write publish date and timestamp
    date_tag = soup.select('meta[name="publishdate"]')
    if len(date_tag) > 0:
        date_str = date_tag[0].attrs['content'].replace(' WIB', '')
        locale.setlocale(locale.LC_TIME, "id_ID.utf8")
        date = datetime.datetime.strptime(date_str, '%Y/%m/%d %H:%M:%S')
        metadata.timestamp = calendar.timegm(date.timetuple())
    else:
        print(" Article '" + article_filename + "' doesn't have date")

    # write related text file on yaml file
    metadata.text_file = article_filename + '.txt'

    # write source article
    metadata.link = link
    if len(author) > 0:
        metadata.author = author[0].text
    else:
        print(" Article '" + article_filename + "' doesn't have author")

    # write title
    metadata.title = article.title
    metadata.media = 'detik'

    # write id file
    metadata.id = article_filename
    return metadata


def write_detik_article(article, path_folder, article_filename, page=1, prefix=''):
    # prepare link
    link = article.link

    # retrieve article
    response = find_document(link)
    if response is None:
        print('Failed when retrieving document on url: ', link)
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    siteType = soup.find('meta', attrs={'property': 'og:type', 'content': 'article'})
    if siteType is None:
        return

    if page > 1:
        # find pages on an article
        link = link + '/' + str(page)

    pages = soup.select('a.detail__anchor-numb')

    paragraphs = retrieve_paragraph(soup)

    # get publish timestamp to be prefix filename
    if page == 1:
        prefix = set_prefix_filename(page, soup, article_filename)

    txt_file, yml_file = create_path_result(path_folder, prefix, article_filename, ScrapperMedia.detik)

    if page == 1:
        metadata = create_metadata(soup,  article_filename, link, article)
        write_article_metadata(yml_file, metadata)

    # write paragraphs to text
    write_article(txt_file, paragraphs)

    if len(pages) > 1 and page < len(pages):
        write_detik_article(article, path_folder, article_filename, page + 1, prefix)


def scrap(keyword, page_number, folder):
    print('scrap {} on detik'.format(keyword))
    detik_scrap_service = DetikScrapService(keyword, int(page_number), folder)
    detik_scrap_service.get_articles()
    detik_scrap_service.write_document_to_files()


