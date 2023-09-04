import sys
import time

import requests
from decouple import config
from selenium import webdriver

from src.interfaces.scrap import ScrapperMedia


def find_articles(keyword, page, media: ScrapperMedia):
    try:
        keyword = keyword.replace(' ', '+')
        match media:
            case ScrapperMedia.detik:
                url = 'https://www.detik.com/search/searchall?query={}&page={}'.format(keyword, page)
            case ScrapperMedia.pikiran_rakyat:
                url = 'https://www.pikiran-rakyat.com/search/?q={}&page={}'.format(keyword, page)
            case ScrapperMedia.cnn_indonesia:
                url = 'https://www.cnnindonesia.com/search/?query={}&page={}'.format(keyword, page)
            case _:
                print('Scrapper Media does not exists')
                sys.exit(1)

        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/117.0'}
        response = requests.get(url, timeout=(3, 30), headers=headers)
        return response
    except requests.RequestException:
        return None


def find_dynamic_articles(keyword, page, media: ScrapperMedia):
    try:
        keyword = keyword.replace(' ', '+')
        match media:
            case ScrapperMedia.cnn_indonesia:
                url = 'https://www.cnnindonesia.com/search/?query={}&page={}'.format(keyword, page)
            case ScrapperMedia.tribunnews:
                url = 'https://www.tribunnews.com/search?q={0}&gsc.q={0}&gsc.page={1}'.format(keyword, page)
            case _:
                print('Scrapper Media does not exists')
                sys.exit(1)

        driver = webdriver.Firefox()
        driver.get(url)
        time.sleep(int(config('SELENIUM_WAIT_TIME', default=5)))
        return driver
    except requests.RequestException:
        return None


def find_document(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/117.0'}
        return requests.get(url, timeout=(3, 30), headers=headers)
    except requests.RequestException:
        return None

