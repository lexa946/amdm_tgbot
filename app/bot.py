import logging
import pickle
import os

from telegram.ext import CallbackContext, ConversationHandler
from telegram import InputMediaPhoto, Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.error import BadRequest

from sqlalchemy.exc import NoResultFound

from app.dbmanager import DbManager
from app.models import User, Song, Message

from app.helpers import send_songs


from app.amdm import AmdmManager



logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

amdm_manager = AmdmManager()


def main_menu(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton('Поиск', callback_data='search')],
        [InlineKeyboardButton('Избранное', callback_data='favorites')],
        [InlineKeyboardButton('Популярное за сегодня', callback_data='popular_now')],
        [InlineKeyboardButton('Популярное за неделю', callback_data='popular_week')],
        [InlineKeyboardButton('Популярное за месяц', callback_data='popular_month')],
        [InlineKeyboardButton('Популярное за все время', callback_data='popular_all')],
    ]
    markup = InlineKeyboardMarkup(keyboard)
    query = update.callback_query
    if query:
        query.edit_message_text(text='Главное меню', reply_markup=markup)
        return ConversationHandler.END
    else:
        context.bot.send_message(update.effective_chat.id, 'Главное меню', parse_mode='html',
                                 reply_markup=markup)


def help_(update: Update, context: CallbackContext):
    text = 'Если по нажатию кнопок в меню ничего не происходит - ' \
           'попробуйте вызвать новое меню командой /menu \n' \
           'Если заметите какие-либо не точности в работе, либо есть пожелания, ' \
           'то прошу обратиться к @AnusDerganus'
    context.bot.send_message(update.effective_chat.id, text, parse_mode='html')


def start(update: Update, context: CallbackContext):
    user = DbManager.get_user_by_tg(update.effective_user)
    DbManager.register(user)
    text = "Привествую вас!\nЗдесь вы сможете найти практически любую песню, для игры на гитаре.\n" \
           "@Все песни берутся с ресурса amdm.ru"
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)
    logging.info(f'Зарегестрирован новый пользователь - {user}')
    main_menu(update, context)


def close(update: Update, context: CallbackContext):
    user = DbManager.get_user_by_tg(update.effective_user)

    for chord_id in user.last_send_chords.split(' '):
        try:
            context.bot.delete_message(user.tg_id, chord_id)
        except BadRequest:
            continue
    query = update.callback_query
    try:
        query.delete_message()
    except BadRequest:
        query.answer('Не удалось закрыть. Попробуйте вызвать /menu')


def popular(func):
    def wrapper(update: Update, context: CallbackContext):
        user = DbManager.get_user_by_tg(update.effective_user)
        user.status = 1
        user.offset = 0
        DbManager.register(user)
        keyboard = []
        markup = InlineKeyboardMarkup(keyboard)
        query = update.callback_query
        query.edit_message_text(text='Пожалуйста, подождите. Идеи поиск...')
        songs = func()
        with open(os.path.join('cache', f'{user.id}_{user.tg_id}_{user.username}_last_dump'), 'wb') as file:
            pickle.dump(songs, file)

        if len(songs) > 10:
            songs = songs[:10]
            keyboard.append([InlineKeyboardButton('Вперед', callback_data='next_songs')])
        keyboard.append([InlineKeyboardButton('Главное меню', callback_data='menu')])
        send_songs(update, songs, 'Популярные сейчас песни:\n\n', markup, edit=True)
        return "GETSONG"

    return wrapper


@popular
def popular_now():
    return amdm_manager.popular_songs()


@popular
def popular_week():
    return amdm_manager.popular_songs(interval='week')


@popular
def popular_month():
    return amdm_manager.popular_songs(interval='month')


@popular
def popular_all():
    return amdm_manager.popular_songs(interval='all')


def search(update: Update, context: CallbackContext):
    user = DbManager.get_user_by_tg(update.effective_user)
    user.status = 1
    user.offset = 0
    DbManager.register(user)
    query = update.callback_query
    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(text='Отмена', callback_data='menu')]
    ])
    query.edit_message_text(text='Введите название песни или исполнителя:', reply_markup=markup)
    return 'SEARCHSONGS'


def search_songs(update: Update, context: CallbackContext):
    user = DbManager.get_user_by_tg(update.effective_user)
    message_bot = context.bot.send_message(user.tg_id, text='Пожалуйста, подождите. Идет поиск...')

    message = Message(update.message.text, update.message.message_id, user.id)
    DbManager.register(message)

    keyboard = []
    markup = InlineKeyboardMarkup(keyboard)

    songs = amdm_manager.find_songs(update.message.text)
    songs_count = len(songs)

    with open(os.path.join('cache', f'{user.id}_{user.tg_id}_{user.username}_last_dump'), 'wb') as file:
        pickle.dump(songs, file)

    if len(songs) > 10:
        keyboard.append([InlineKeyboardButton('Вперед', callback_data='next_songs')])
        songs = songs[:10]

    keyboard.append([InlineKeyboardButton('Главное меню', callback_data='menu')])
    message_bot.delete()
    send_songs(update, songs, f'Найдено {songs_count} совпадений\n\n', markup)
    return "GETSONG"


def favorites(update: Update, context: CallbackContext):
    user = DbManager.get_user_by_tg(update.effective_user)
    user.status = 2
    user.offset = 0
    DbManager.register(user)
    keyboard = []
    markup = InlineKeyboardMarkup(keyboard)

    songs = user.favorites
    if len(songs) > 10:
        songs = songs[:10]
        keyboard.append([InlineKeyboardButton('Вперед', callback_data='next_songs')])
    keyboard.append([InlineKeyboardButton('Главное меню', callback_data='menu')])
    send_songs(update, songs, 'Ваши избранные песни:\n\n', markup, edit=True)
    return "GETSONG"


def add_favorites(update: Update, context: CallbackContext):
    user = DbManager.get_user_by_tg(update.effective_user)

    query = update.callback_query
    song_id = query.data.split('_')[1]
    song = DbManager.get_song_by_id(song_id)

    if song in user.favorites:
        query.answer('Уже добавлено')
    else:
        user.favorites.append(song)
        DbManager.register(user)
        query.answer('Добавлено в избранное')


def remove_favorites(update: Update, context: CallbackContext):
    user = DbManager.get_user_by_tg(update.effective_user)

    query = update.callback_query
    song_id = int(query.data.split('_')[1])
    song_del = None
    for song in user.favorites:
        if song.id == song_id:
            song_del = song

    if song_del:
        user.favorites.remove(song_del)
        DbManager.register(user)
        query.answer('Удалено из избранного')
    else:
        query.answer('Уже удалено')



def get_song(func):
    def wrapper(update: Update, context: CallbackContext):
        user = DbManager.get_user_by_tg(update.effective_user)
        try:
            song_num = int(update.message.text)
        except ValueError:
            update.message.reply_text('Не понял номер, повторите ввод.')
            return "GETSONG"

        song, keyboard = func(user, song_num)
        markup = InlineKeyboardMarkup(keyboard)
        if not song:
            update.message.reply_text('Нет песни с таким номером.')
            return "GETSONG"

        if len(song.text) <= 3900:
            media = []
            media_message_id = []
            # for chord in song.chords.split(' '):
            #     media.append(InputMediaPhoto(chord))
            try:
                media_send_data = update.message.reply_media_group(media)
                for media in media_send_data:
                    media_message_id.append(str(media.message_id))
                media_str = ' '.join(media_message_id)
                user.last_send_chords = media_str
                DbManager.register(user)
            except BadRequest:
                pass
            update.message.reply_text(song.text, parse_mode='html', reply_markup=markup)
            return "GETSONG"
        else:
            with open(os.path.join('songs', 'index.html')) as template:
                template_page = template.read()

            page_path = os.path.join('songs', f'{user.id}_{user.tg_id}_{user.username}_song.html')
            text = ""
            # for chord in song.chords.split(' '):
            #     text += f'<img src={chord}>\n'
            text += '</br>'
            text += f'<p>{song.artist} - {song.name}</p></br>'
            text += f'{song.text}'.encode('windows-1251').decode('cp1251')
            text = template_page.format(text)

            with open(page_path, 'w') as song_html:
                song_html.write(text)
            with open(page_path) as song_html:
                update.message.reply_document(song_html, reply_markup=markup,
                                              filename=f'{song.artist}-{song.name}.html',
                                              caption="Песня слишком большая для сообщения.")
            return "GETSONG"

    return wrapper


@get_song
def get_search_song(user: User, song_num: int):
    keyboard = []

    with open(os.path.join('cache', f'{user.id}_{user.tg_id}_{user.username}_last_dump'), 'rb') as file:
        try:
            song_dump = pickle.load(file)[song_num]
        except IndexError:
            return None, keyboard

    song = DbManager.get_song_by_url(song_dump.url)
    if not song:
        song = Song(song_dump.url, song_dump.artist, song_dump.artist_url, song_dump.name, song_dump.text,
                    [chord.url for chord in song_dump.chords])
        song.fill_body()
        song.fill_chords()
        DbManager.register(song)
    keyboard.append([InlineKeyboardButton('В избранное', callback_data=f'like_{song.id}')])
    keyboard.append([InlineKeyboardButton('Закрыть', callback_data='close')])

    return song, keyboard


@get_song
def get_favorite_song(user: User, song_num: int):
    keyboard = []
    try:
        song = user.favorites[song_num]
    except IndexError:
        return None, keyboard

    keyboard.append([InlineKeyboardButton('Удалить из избранного', callback_data=f'remove_{song.id}')])
    keyboard.append([InlineKeyboardButton('Закрыть', callback_data='close')])
    return song, keyboard