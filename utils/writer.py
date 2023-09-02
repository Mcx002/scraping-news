import locale
import os.path
from calendar import calendar
from datetime import datetime
from typing import Literal

from src.interfaces.scrap import ScrapperMedia


class ArticleMetadata:
    def __init__(self):
        self.timestamp = 0
        self.text_file = ''
        self.link = ''
        self.author = ''
        self.title = ''
        self.id = ''
        self.media = ''


def write_append(filename, text):
    f = open(filename, 'a', encoding='utf-8')
    f.write(text)
    f.write('\n')
    f.close()


def write_article(article_filename, paragraphs):
    f = open(article_filename, 'a')
    for paragraph in paragraphs:
        # write document
        f.write(paragraph)
        f.write('\n')

    f.close()


def write_article_metadata(yml_file, metadata: ArticleMetadata):
    write_append(yml_file, 'timestamp: ' + str(metadata.timestamp))
    write_append(yml_file, 'date: ' + datetime.strftime(datetime.fromtimestamp(metadata.timestamp), '%Y/%m/%d %H:%M:%S'))
    write_append(yml_file, 'Text file: ' + metadata.text_file)
    write_append(yml_file, 'link: ' + metadata.link)
    write_append(yml_file, 'author: ' + metadata.author)
    write_append(yml_file, 'title: \'' + metadata.title.replace('\'', '"') + '\'')
    write_append(yml_file, 'id: ' + metadata.id)
    write_append(yml_file, 'media: ' + metadata.media)


def create_path_result(path_folder, prefix, article_filename, media: ScrapperMedia):
    txt_file = '{}{}/{}_{}.{}'.format(path_folder, media, prefix, article_filename, 'txt')
    yml_file = '{}{}/{}_{}.{}'.format(path_folder, media, prefix, article_filename, 'yaml')

    return txt_file, yml_file
