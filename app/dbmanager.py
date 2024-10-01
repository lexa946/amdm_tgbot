from sqlalchemy import select
from sqlalchemy.orm import selectinload

from telegram import User as TgUser

from app.models import User, Song
from app.config import session_maker


class DbManager:
    @classmethod
    def get_user_by_tg(cls, tg_user: TgUser):
        with session_maker() as session:
            user = session.scalar(
                select(User).where(User.tg_id == tg_user.id).options(
                    selectinload(User.favorites)
                )
            )
            if not user:
                user = User(tg_user.id, tg_user.username, tg_user.first_name, tg_user.last_name)
                cls.register(
                    user
                )
            return user

    @classmethod
    def get_song_by_id(cls, id_):
        with session_maker() as session:
            query = select(Song).where(Song.id == id_).options(
                selectinload(Song.users)
            )
            song = session.scalar(query)
            return song

    @classmethod
    def get_song_by_url(cls, url):
        with session_maker() as session:
            query = select(Song).where(Song.url == url)
            song = session.scalar(query)
            return song

    @classmethod
    def register(cls, data):
        with session_maker() as session:
            session.add(data)
            session.commit()
