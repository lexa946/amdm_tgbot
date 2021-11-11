import sqlalchemy.ext.declarative

from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import Column, Integer, Text, String, ForeignKey, Table

DATABASE_NAME = 'base.db'

Base = sqlalchemy.ext.declarative.declarative_base()
engine = sqlalchemy.create_engine(f'sqlite:///{DATABASE_NAME}', connect_args={'check_same_thread': False})
Session = sessionmaker(bind=engine)

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
    chords = Column(Text, nullable=True)
    url = Column(String(200), nullable=False)
    users = relationship('User', secondary=user_song,
                         back_populates='favorites', lazy=True)

    def __init__(self, url: str, artist: str, name: str, text: str, chords: [list, tuple]):
        self.url = url
        self.artist = artist
        self.name = name
        self.text = text
        self.chords = ' '.join(chords)

    def __repr__(self):
        return f"{self.artist} - {self.name}"


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


if __name__ == '__main__':
    engine = sqlalchemy.create_engine('sqlite:///../base.db')
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
