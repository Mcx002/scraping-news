import requests
from requests import Response


def find_hello():
    print('hello from repo')


def find_articles(keyword, page):
    try:
        page_query = ''
        if page != 1:
            page_query = '&page=' + str(page)

        keyword = keyword.replace(' ', '+')
        url = 'https://www.detik.com/search/searchall?query=' + keyword + page_query

        response = requests.get(url, timeout=(3, 30))
        return response
    except requests.RequestException:
        return None


def find_document(url):
    try:
        return requests.get(url, timeout=(3, 30))
    except requests.RequestException:
        return None
