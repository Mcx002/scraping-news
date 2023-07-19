import requests


def find_hello():
    print('hello from repo')


def find_articles(keyword, page):
    page_query = ''
    if page != 1:
        page_query = '&page=' + str(page)

    keyword = keyword.replace(' ', '+')
    url = 'https://www.detik.com/search/searchall?query=' + keyword + page_query

    response = requests.get(url)
    return response


def find_document(url):
    return requests.get(url)
