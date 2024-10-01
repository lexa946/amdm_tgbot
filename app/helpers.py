USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 YaBrowser/24.7.0.0 Safari/537.36"


def validate_url(url: str):
    if not isinstance(url, str):
        raise Exception("URL должн быть строкой")

    url = url.strip('/')
    if not url.startswith("https://"):
        url = f'https://{url}'
    return url


def group(iterable, count):
    """ Группировка элементов последовательности по count элементов """

    return list(zip(*[iter(iterable)] * count))



def send_songs(update, songs, captive='', markup=None, edit=False, offset=0):
    text = ''
    text += captive
    for i, song in enumerate(songs):
        text += f'{i+offset}. {song.artist}-{song.name}\n'
    text += '\nПришли мне номер песни, а я тебе текст и аккорды.'

    if edit:
        query = update.callback_query
        query.edit_message_text(text=text, reply_markup=markup)
    else:
        update.message.reply_text(text, parse_mode='html', reply_markup=markup)