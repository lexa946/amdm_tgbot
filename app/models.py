import webbrowser

import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, Text, String, ForeignKey, Table, JSON

from app.chord import Chord
from app.config import Base
from app.helpers import USER_AGENT

user_song = Table("user_song", Base.metadata,
                  Column('user_id', Integer, ForeignKey('users.id')),
                  Column('song_id', Integer, ForeignKey('songs.id'))
                  )



class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    tg_id = Column(Integer, unique=True, nullable=False)
    username = Column(String(50), nullable=True, default='')
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    status = Column(Integer, nullable=False, default=0)
    offset = Column(Integer, nullable=False, default=0)
    last_send_chords = Column(String, nullable=True, default='')
    messages = relationship('Message', backref='user', lazy=True)
    favorites = relationship('Song', secondary=user_song,
                             back_populates='users', lazy=True)

    def __init__(self, tg_id: int, username: str, first_name: str, last_name: str):
        self.tg_id = tg_id
        self.username = username
        self.first_name = first_name
        self.last_name = last_name

    def __repr__(self):
        return f'{self.tg_id}_{self.username}'


class Song(Base):
    __tablename__ = "songs"
    id = Column(Integer, primary_key=True)
    artist = Column(String(100), nullable=False)
    name = Column(String(100), nullable=False)
    text = Column(Text, nullable=False)
    chords = Column(JSON, nullable=True)
    url = Column(String(200), nullable=False)
    artist_url = Column(String(200), nullable=True)
    users = relationship('User', secondary=user_song,
                         back_populates='favorites', lazy=True)



    def __init__(self, url: str, artist: str, artist_url:str, name: str, text: str, chords: [...]):
        self.url = url
        self.artist = artist
        self.name = name
        self.text = text
        self.chords = chords
        self.artist_url = artist_url
        self.__html_full_page = None

    def __repr__(self):
        return f"{self.artist} - {self.name}"


    def fill_chords(self):
        self.chords.clear()
        self.__html_full_page_exist()
        soup = BeautifulSoup(self.__html_full_page, 'lxml')
        for chord_row in soup.select('#song_chords img'):
            chord = Chord(chord_row.attrs['alt'], chord_row.attrs['src'])
            self.chords.append(str(chord))

    def fill_body(self):
        self.__html_full_page_exist()
        soup = BeautifulSoup(self.__html_full_page, 'lxml')
        self.text = soup.select_one('pre[itemprop="chordsBlock"]').text

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





class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True)
    text = Column(Text, default='')
    tg_id = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    def __init__(self, text, tg_id, user_id):
        self.text = text
        self.tg_id = tg_id
        self.user_id = user_id


