from telegram.ext import Updater, ConversationHandler, CallbackQueryHandler, MessageHandler, Filters, CommandHandler

from app.bot import search, search_songs, get_search_song, main_menu, favorites, get_favorite_song, popular_now, \
    popular_week, popular_month, popular_all, start, add_favorites, remove_favorites, close, help_
from app.config import settings
from app.paginate_song import next_songs, previous_songs



updater = Updater(token=settings.BOT_TOKEN, use_context=True)
dispatcher = updater.dispatcher

conv_handler_search = ConversationHandler(
    entry_points=[CallbackQueryHandler(search, pattern='search')],
    states={
        'SEARCHSONGS': [MessageHandler(Filters.text, search_songs)],
        'GETSONG': [MessageHandler(Filters.text, get_search_song)]
    },
    fallbacks=[CallbackQueryHandler(main_menu, pattern='menu'),
               CommandHandler('menu', main_menu)],
)

conv_handler_favorites = ConversationHandler(
    entry_points=[CallbackQueryHandler(favorites, pattern='favorites')],
    states={
        'GETSONG': [MessageHandler(Filters.text, get_favorite_song)]
    },
    fallbacks=[CallbackQueryHandler(main_menu, pattern='menu'),
               CommandHandler('menu', main_menu)]
)

for func, func_name in zip(
        [popular_now, popular_week, popular_month, popular_all],
        ['popular_now', 'popular_week', 'popular_month', 'popular_all'],
):
    dispatcher.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(func, pattern=f'{func_name}')],
        states={
            'GETSONG': [MessageHandler(Filters.text, get_search_song)]
        },
        fallbacks=[CallbackQueryHandler(main_menu, pattern='menu'),
                   CommandHandler('menu', main_menu)]
    ))

dispatcher.add_handler(conv_handler_search)
dispatcher.add_handler(conv_handler_favorites)

dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('menu', main_menu))
dispatcher.add_handler(CommandHandler('help', help_))
dispatcher.add_handler(CallbackQueryHandler(next_songs, pattern='^next_songs$'))
dispatcher.add_handler(CallbackQueryHandler(previous_songs, pattern='^previous_songs$'))
dispatcher.add_handler(CallbackQueryHandler(add_favorites, pattern='^like_'))
dispatcher.add_handler(CallbackQueryHandler(remove_favorites, pattern='^remove_'))
dispatcher.add_handler(CallbackQueryHandler(close, pattern='close'))

updater.start_polling()
