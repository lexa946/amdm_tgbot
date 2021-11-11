from config.models import Session
from config.models import User, Song

from telegram import User as TgUser
import sqlalchemy.orm


class DbManager:
    def __init__(self):
        self.session = Session()

    def get_user_by_tg(self, tg_user: TgUser):
        try:
            user = self.session.query(User).filter(User.tg_id == tg_user.id).one()
        except sqlalchemy.orm.exc.NoResultFound:
            user = User(tg_user.id, tg_user.username, tg_user.first_name, tg_user.last_name)
            self.register(user)
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
