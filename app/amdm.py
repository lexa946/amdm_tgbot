import requests
from bs4 import BeautifulSoup

from app.models import Song
from app.helpers import USER_AGENT
from app.config import settings


class AmdmManager:
    def __init__(self):
        self.main_url = settings.MAIN_URL_AMDM
        self.headers = {
            "user-agent": USER_AGENT,
        }

    def find_songs(self, name_song: str):
        url_template = f"{self.main_url}/search/page" + "{0}/"
        songs = self.__get_songs_paginator(url_template, q=name_song)
        return songs

    def popular_songs(self, interval=''):
        """
        :param interval: week, month или all, если оставить пустым - найдет популярные сейчас
        :return:
        """
        if interval:
            url_template = f"{self.main_url}/akkordi/popular/{interval}/page" + "{0}/"
        else:
            url_template = f"{self.main_url}/akkordi/popular/page" + "{0}/"
        songs = self.__get_songs_paginator(url_template)
        return songs

    def __get_songs_paginator(self, url_template: str, **params):
        page_counter = 1
        songs = []
        while True:
            url = url_template.format(page_counter)
            response = requests.get(url, params=params, headers=self.headers)
            songs_temp = self.__get_songs_from_page(response.text)
            if not songs_temp:
                break
            songs += songs_temp
            page_counter += 1
        return songs

    def __get_songs_from_page(self, html: str):
        songs = []

        soup = BeautifulSoup(html, 'lxml')

        for row in soup.select('table.items>tr td:last-child'):
            artist = row.select_one("a:first-child").text
            name = row.select_one("a:nth-child(2)").text
            url = row.select_one("a:nth-child(2)").attrs['href']
            artist_url = row.select_one("a:first-child").attrs['href']
            song = Song(url, artist, artist_url, name, None, [])
            songs.append(song)
        return songs
