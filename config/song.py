import requests
import webbrowser

from bs4 import BeautifulSoup

from config.helpers import USER_AGENT, validate_url
from config.chord import Chord


class Song:
    def __init__(self, artist: str, name: str, url: str, url_artist: str):
        self.artist = artist
        self.name = name
        self.url = url
        self.url_artist = url_artist
        self.chords = []
        self.body = None
        # self.body = ''

        self.__html_full_page = None


    @property
    def url(self):
        return self.__url

    @url.setter
    def url(self, value: str):
        self.__url = validate_url(value)

    @property
    def url_artist(self):
        return self.__url_artist

    @url_artist.setter
    def url_artist(self, value: str):
        self.__url_artist = validate_url(value)

    def fill_chords(self):
        self.chords.clear()
        self.__html_full_page_exist()
        soup = BeautifulSoup(self.__html_full_page, 'lxml')
        for chord_row in soup.select('#song_chords img'):
            chord = Chord(chord_row.attrs['alt'], chord_row.attrs['src'])
            self.chords.append(chord)

    def fill_body(self):
        self.__html_full_page_exist()
        soup = BeautifulSoup(self.__html_full_page, 'lxml')
        body = soup.select_one('pre[itemprop="chordsBlock"]')
        self.body = str(body)

    def open_in_browser(self):
        self.fill_body()
        self.fill_chords()

        with open('index.html', 'w') as index:
            for chord in self.chords:
                index.write(f'<img src={chord.url} alt={chord.name}>')
            index.write('</br>')
            index.write(self.body)

        webbrowser.open_new('index.html')

    def __repr__(self):
        return f"{self.artist} - {self.name}"

    def __str__(self):
        return f"{self.artist} - {self.name}"

    def __html_full_page_exist(self):
        if not self.__html_full_page:
            response = requests.get(
                self.url, headers={'user-agent': USER_AGENT}
            )
            self.__html_full_page = response.text

