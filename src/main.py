from src import settings
import logging
import telegram
from src.key import token
from src.gamehandler import GameHandler
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from src.exceptions import GoGameException
import random
import atexit

__author__ = "Rafael Kübler da Silva <rafael_kuebler@yahoo.es>"
__version__ = "0.1"

game_handler = GameHandler()


def start(bot, update):
    chat_id = update.message.chat_id
    send_message(bot, chat_id, settings.greeting)
    send_message(bot, chat_id, settings.commands)


def new_game(bot, update):
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    user_name = update.message.from_user.name.replace('\'', '')
    game_handler.new_game(chat_id, user_id, user_name)
    send_message(bot, chat_id, settings.new_game_text)


def join(bot, update):
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    user_name = update.message.from_user.name.replace('\'', '')
    game_handler.join(chat_id, user_id, user_name)
    send_message(bot, chat_id, settings.start_game_text)
    show_board(bot, update)


def place(bot, update):
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    coords = update.message.text.replace('/place ', '')
    try:
        game_handler.place_stone(chat_id, user_id, coords)
        show_board(bot, update)
    except GoGameException as exception:
        send_message(bot, chat_id, str(exception))


def pass_turn(bot, update):
    chat_id = update.message.chat_id
    game_handler.create_image(chat_id)
    # TODO: pass
    send_message(bot, chat_id, f"Player x passed")
    show_board(bot, update)


def show_board(bot, update):
    chat_id = update.message.chat_id
    cur_player_name = game_handler.cur_player_name(chat_id)
    cur_color = game_handler.cur_player_color(chat_id)
    image = game_handler.create_image(chat_id)
    bot.send_photo(chat_id, photo=image)
    # TODO: extract string
    send_message(bot, chat_id, f"It is {cur_player_name}'s ({cur_color}) turn")


def display_proverb(bot, update):
    chat_id = update.message.chat_id
    proverb = random.choice(settings.go_proverbs)
    send_message(bot, chat_id, f"\'_{proverb}_\'")


def unknown(bot, update):
    chat_id = update.message.chat_id
    send_message(bot, chat_id, settings.unknown_command_text)


def send_message(bot, chat_id, text):
    bot.send_message(chat_id=chat_id, text=text, parse_mode=telegram.ParseMode.MARKDOWN)


def save_games():
    game_handler.save_games()


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
        CommandHandler('proverb', display_proverb),
        MessageHandler(Filters.command, unknown)
    ]

    for handler in message_handlers:
        dispatcher.add_handler(handler)

    atexit.register(save_games)

    print('Starting polling')
    updater.start_polling()
