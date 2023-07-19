from src.repositories.detik import find_articles, find_document
from bs4 import BeautifulSoup
from src.models.article import Article
import numpy as np
from progress.bar import Bar
import re
import datetime
import calendar
from utils.path import get_root_dir


def compose_raw_article(raw_articles):
    # init articles
    articles = []

    for raw_article in raw_articles:
        link = raw_article.find('a')['href']

        # ensure just article will be scraped
        is_article = re.search("(https://news.|https://|https://www.)detik.com", link)
        if not is_article:
            continue

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


def write_article(article, article_filename, page=1):
    # prepare link
    link = article.link
    if page > 1:
        # find pages on an article
        link = link + '/' + str(page)

    # retrieve article
    response = find_document(link)
    soup = BeautifulSoup(response.text, 'html.parser')
    pages = soup.select('a.detail__anchor-numb')

    paragraphs = soup.select('div.detail__body-text > p')

    # write paragraphs to text
    write_paragraphs(article_filename, paragraphs)

    if len(pages) > 1:
        write_article(article, article_filename, page + 1)


def get_documents_from_articles(articles):
    documents = []

    bar = Bar('Retrieving documents', max=len(articles))
    for article in articles:
        # prepare article filename
        article_filename = str(get_root_dir()) + '/data/' + str(calendar.timegm(datetime.datetime.now().timetuple())) + '_' + article.title

        # prepare file
        f = open(article_filename, 'w')
        f.write('Title: ' + article.title + '\n\n')
        f.close()

        write_article(article, article_filename)

        bar.next()
    bar.finish()

    return documents


def scrap():
    keyword = input('Keyword: ')
    page_number = input('How many pages? (number): ')

    articles = get_articles(keyword, int(page_number))
    documents = get_documents_from_articles(articles)

    print(len(documents))
