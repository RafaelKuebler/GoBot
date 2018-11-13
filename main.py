import settings
import logging
import telegram
from key import token
from gamehandler import GameHandler
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from io import BytesIO
from exceptions import GoGameException

__author__ = "Rafael Kübler da Silva <rafael_kuebler@yahoo.es>"
__version__ = "0.1"

game_handler = GameHandler()


def start(bot, update):
    chat_id = update.message.chat_id
    bot.send_message(chat_id=chat_id, text=settings.greeting, parse_mode=telegram.ParseMode.MARKDOWN)
    bot.send_message(chat_id=chat_id, text=settings.commands, parse_mode=telegram.ParseMode.MARKDOWN)


def new_game(bot, update):
    chat_id = update.message.chat_id
    game_handler.new_game(chat_id, update.message.from_user.id)
    bot.send_message(chat_id=chat_id, text='You created a new game! Another player can join with the /join command.')


def join(bot, update):
    chat_id = update.message.chat_id
    game_handler.join(chat_id, update.message.from_user.id)
    bot.send_message(chat_id=chat_id, text='Let the game begin!')
    show_board(bot, update)


def place(bot, update):
    chat_id = update.message.chat_id
    player = update.message.from_user.id
    coords = update.message.text.replace('/place ', '')
    try:
        game_handler.place_stone(chat_id, player, coords)
        show_board(bot, update)
    except GoGameException as exception:
        bot.send_message(chat_id=chat_id, text=str(exception))


def pass_turn(bot, update):
    chat_id = update.message.chat_id
    game_handler.create_image(chat_id)
    # TODO: pass
    bot.send_message(chat_id=update.message.chat_id, text=f"Player x passed")
    show_board(bot, update)


def show_board(bot, update):
    chat_id = update.message.chat_id
    cur_player = game_handler.cur_player(chat_id)
    image = game_handler.create_image(chat_id)
    bio = BytesIO()
    bio.name = 'image.jpeg'
    image.save(bio, 'JPEG')
    bio.seek(0)
    bot.send_photo(chat_id, photo=bio)
    bot.send_message(chat_id=update.message.chat_id, text=f"It is {cur_player}'s turn")


def unknown(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Sorry, I didn't understand that command.")


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)

    updater = Updater(token=token)
    dispatcher = updater.dispatcher

    message_handlers = [
        CommandHandler('start', start),
        CommandHandler('new', new_game),
        CommandHandler('join', join),
        CommandHandler('place', place),
        CommandHandler('pass', pass_turn),
        CommandHandler('show_board', show_board),
        MessageHandler(Filters.command, unknown)
    ]

    for handler in message_handlers:
        dispatcher.add_handler(handler)

    print('Starting polling')
    updater.start_polling()
