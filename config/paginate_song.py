import os
import pickle


from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from config.dbmanager import db_manager
from config.helpers import send_songs
from config.models import User, Song


def paginate_song_decor(func):
    def wrapper(update: Update, context: CallbackContext):
        user = db_manager.get_user_by_tg(update.effective_user)
        if user.status == 1:
            with open(os.path.join('.', 'cache', f'{user.id}_{user.tg_id}_{user.username}_last_dump'), 'rb') as file:
                songs = pickle.load(file)
        elif user.status == 2:
            songs = user.favorites
        else:
            songs = []

        songs, keyboard = func(user, songs)

        keyboard.append([InlineKeyboardButton('Главное меню', callback_data='menu')])

        markup = InlineKeyboardMarkup(keyboard)
        send_songs(update, songs, markup=markup, edit=True, offset=user.offset)
    return wrapper


@paginate_song_decor
def next_songs(user: User, songs: [Song]):
    user.offset += 10
    db_manager.register(user)

    if len(songs) < user.offset + 10:
        songs = songs[user.offset:]
        keyboard = [
            [InlineKeyboardButton('Назад', callback_data='previous_songs')]
        ]
    else:
        songs = songs[user.offset:user.offset + 10]
        keyboard = [
            [InlineKeyboardButton('Назад', callback_data='previous_songs'),
             InlineKeyboardButton('Вперед', callback_data='next_songs')]
        ]
    return songs, keyboard


@paginate_song_decor
def previous_songs(user: User, songs: [Song]):
    if user.offset != 0:
        user.offset -= 10
    db_manager.register(user)

    if user.offset == 0:
        songs = songs[:user.offset + 10]
        keyboard = [
            [InlineKeyboardButton('Вперед', callback_data='next_songs')]
        ]
    else:
        songs = songs[user.offset:user.offset+10]
        keyboard = [
            [InlineKeyboardButton('Назад', callback_data='previous_songs'),
             InlineKeyboardButton('Вперед', callback_data='next_songs')]
        ]

    return songs, keyboard
