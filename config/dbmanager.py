from config.models import Session
from config.models import User, Song

from telegram import User

class DbManager:
    def __init__(self):
        self.session = Session()

    def get_user_by_tg_id(self, tg_user: User):
        try:
            user = self.session.query(User).filter(User.tg_id == tg_user.id).one()
        except:
            pass
        return user

    def get_song_by_id(self, id):
        song = self.session.query(Song).filter(Song.id == id).one()
        return song

    def get_song_by_url(self, url):
        song = self.session.query(Song).filter(Song.url == url).one()
        return song


    def register(self, data):
        self.session.add(data)
        self.session.commit()

db_manager = DbManager()
