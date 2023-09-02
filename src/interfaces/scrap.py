from enum import Enum


class ScrapInterface:
    def get_article(self):
        """Retrieving Article Information"""
        pass

    def compose_raw_article(self, raw_articles):
        """Composing Article Information"""
        pass

    def write_document_to_files(self):
        """Writing Article Information to files"""
        pass


class ScrapperMedia(Enum):
    detik = 'detik'
    pikiran_rakyat = 'pikiran-rakyat'