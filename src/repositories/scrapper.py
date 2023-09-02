import sys
from typing import Literal

import requests

from src.interfaces.scrap import ScrapperMedia


def find_articles(keyword, page, media: ScrapperMedia):
    try:
        keyword = keyword.replace(' ', '+')
        match media:
            case ScrapperMedia.detik:
                url = 'https://www.detik.com/search/searchall?query={}&page={}'.format(keyword, page)
            case ScrapperMedia.pikiran_rakyat:
                url = 'https://www.pikiran-rakyat.com/search/?q={}&page={}'.format(keyword, page)
            case _:
                print('Scrapper Media does not exists')
                sys.exit(1)

        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        response = requests.get(url, timeout=(3, 30), headers=headers)
        return response
    except requests.RequestException:
        return None


def find_document(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        return requests.get(url, timeout=(3, 30), headers=headers)
    except requests.RequestException:
        return None

