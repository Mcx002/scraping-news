import os

from src.repositories.detik import find_articles, find_document
from bs4 import BeautifulSoup
from src.models.article import Article
import numpy as np
from progress.bar import Bar
import re
import datetime
import calendar
from utils.path import get_root_dir, to_dash_case


def compose_raw_article(raw_articles):
    # init articles
    articles = []

    for raw_article in raw_articles:
        link = raw_article.find('a')['href']

        # ensure just article will be scraped
        # is_article = re.search("(https://news.|https://|https://www.)detik.com", link)
        # if not is_article:
        #     continue

        # init article
        article = Article()
        article.title = raw_article.find('h2', attrs={'class': 'title'}).text
        article.link = link

        # append retrieved article to articles
        articles.append(article)

    return articles


def get_articles(keyword, page_number):
    articles = []

    bar = Bar('Retrieving articles information', max=page_number)
    for i in range(page_number):
        page = i + 1

        # find raw articles
        response = find_articles(keyword, page)
        if response is None:
            print('Failed when retrieving articles information on page', page)
            continue
        soup = BeautifulSoup(response.text, 'html.parser')
        raw_articles = soup.find_all('article')

        # concat articles
        composed_articles = compose_raw_article(raw_articles)
        articles = np.concatenate((articles, composed_articles))

        bar.next()
    bar.finish()
    return articles


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
    f = open(filename, 'a')
    f.write(text)
    f.write('\n')
    f.close()


def write_article(article, path_folder, article_filename, page=1):
    txt_file = path_folder + '/' + article_filename + '.txt'
    yml_file = path_folder + '/' + article_filename + '.yaml'

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
    author = soup.select('div.detail__author')

    # write paragraphs to text
    append(yml_file, 'Text file: ' + article_filename + '.txt')
    if len(author) > 0:
        append(yml_file, 'author: ' + author[0].text)
    else:
        print(" Article '" + article_filename + "' doesn't have author")
    append(yml_file, 'title: \'' + article.title.replace('\'', '"') + '\'')
    append(yml_file, 'id: ' + article_filename)

    # write paragraphs to text
    write_paragraphs(txt_file, paragraphs)

    if len(pages) > 1 and page < len(pages):
        write_article(article, path_folder, article_filename, page + 1)


def get_documents_from_articles(articles):
    documents = []

    path_folder = str(get_root_dir()) + '/data/' + str(
        calendar.timegm(datetime.datetime.now().timetuple())) + '/'

    isFolderExists = os.path.exists(path_folder)
    if not isFolderExists:
        os.mkdir(path_folder)

    bar = Bar('Retrieving documents', max=len(articles))
    for article in articles:
        # prepare article filename
        article_filename = to_dash_case(article.title)

        write_article(article, path_folder, article_filename)

        bar.next()
    bar.finish()

    return documents


def scrap():
    keyword = input('Keyword: ')
    page_number = input('How many pages? (number): ')

    articles = get_articles(keyword, int(page_number))
    documents = get_documents_from_articles(articles)

    print(len(documents))
