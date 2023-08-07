import locale
import os

from src.repositories.detik import find_articles, find_document
from bs4 import BeautifulSoup
from src.models.article import Article
import numpy as np
from progress.bar import Bar
import re
import datetime
import calendar
from utils.path import get_root_dir, to_dash_case, get_ext, get_file_name


class DetikScrapService:
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
            response = find_articles(self.keyword, page)
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

        isFolderExists = os.path.exists(path_folder)
        if not isFolderExists:
            os.mkdir(path_folder)

        # get existing filenames
        existing_files = os.listdir(path_folder)
        existing_files = ['_'.join(get_file_name(a).split('_')[1:]) for a in existing_files if get_ext(a) == 'txt']

        bar = Bar('Retrieving documents', max=len(self.articles))
        for article in self.articles:
            # prepare article filename
            article_filename = to_dash_case(article.title)

            # skip if exists
            if article_filename in existing_files:
                bar.next()
                continue

            write_article(article, path_folder, article_filename)

            bar.next()
        bar.finish()


def write_paragraphs(article_filename, paragraphs):
    f = open(article_filename, 'a')
    for paragraph in paragraphs:
        text = paragraph.text

        # validate meaningless paragraph
        is_page_anchor_paragraph = re.search("\n\n\n\nHalaman\n\n", text)
        is_meaningless_paragraph = re.search("^Simak.*di halaman berikutnya.$", text)
        if text == '' or text == ' ' or is_page_anchor_paragraph or is_meaningless_paragraph:
            break

        # write document
        f.write(text)
        f.write('\n')

    f.close()


def append(filename, text):
    f = open(filename, 'a', encoding='utf-8')
    f.write(text)
    f.write('\n')
    f.close()


def write_article(article, path_folder, article_filename, page=1, prefix=''):
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

    paragraphs = soup.select('div.detail__body-text > p')

    # get publish timestamp to be prefix filename
    if page == 1:
        date_tag = soup.select('meta[name="publishdate"]')
        if len(date_tag) > 0:
            date_str = date_tag[0].attrs['content'].replace(' WIB', '')
            locale.setlocale(locale.LC_TIME, "id_ID.utf8")
            date = datetime.datetime.strptime(date_str, '%Y/%m/%d %H:%M:%S')
            prefix = str(calendar.timegm(date.timetuple()))
        else:
            print(" Article '" + article_filename + "' doesn't have date")

    txt_file = path_folder + '/' + prefix + '_' + article_filename + '.txt'
    yml_file = path_folder + '/' + prefix + '_' + article_filename + '.yaml'

    # write paragraphs to text
    if page == 1:
        author = soup.select('div.detail__author')

        # write publish date and timestamp
        date_tag = soup.select('meta[name="publishdate"]')
        if len(date_tag) > 0:
            date_str = date_tag[0].attrs['content'].replace(' WIB', '')
            locale.setlocale(locale.LC_TIME, "id_ID.utf8")
            date = datetime.datetime.strptime(date_str, '%Y/%m/%d %H:%M:%S')
            append(yml_file, 'date: ' + date_str)
            append(yml_file, 'timestamp: ' + str(calendar.timegm(date.timetuple())))
        else:
            print(" Article '" + article_filename + "' doesn't have date")

        # write related text file on yaml file
        append(yml_file, 'Text file: ' + article_filename + '.txt')

        # write source article
        append(yml_file, 'link: ' + link)
        if len(author) > 0:
            append(yml_file, 'author: ' + author[0].text)
        else:
            print(" Article '" + article_filename + "' doesn't have author")

        # write title
        append(yml_file, 'title: \'' + article.title.replace('\'', '"') + '\'')

        # write id file
        append(yml_file, 'id: ' + article_filename)

    # write paragraphs to text
    write_paragraphs(txt_file, paragraphs)

    if len(pages) > 1 and page < len(pages):
        write_article(article, path_folder, article_filename, page + 1, prefix)


def scrap():
    keyword = input('Keyword: ')
    page_number = input('How many pages? (number): ')

    print('\n\nWhen you fill folder name, it will make your scrapping data only go to that folder')
    print('The advantage is, it will matching the upcoming scrapping data id with the old data id on that folder')
    print('The id is a conversion from title -> lowercased -> remove unnecessary punctuation -> change space to '
          'underscore\n\n')
    print('default = {timestamp}')
    folder_input = input('Folder name: ')
    folder: None | str = None
    if folder_input != '':
        folder = folder_input

    detik_scrap_service = DetikScrapService(keyword, int(page_number), folder)
    detik_scrap_service.get_articles()
    detik_scrap_service.write_document_to_files()
