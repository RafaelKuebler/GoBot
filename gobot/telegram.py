import logging
import telegram
import random
import atexit
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from . import settings
from .exceptions import GoGameException
from .gamehandler import GameHandler

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

    print(f"[{chat_id}] {user_name}({user_id}): New game")

    game_handler.new_game(chat_id, user_id)
    game_handler.join(chat_id, user_id, user_name)

    send_message(bot, chat_id, settings.new_game_text)


def join(bot, update):
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    user_name = update.message.from_user.name.replace('\'', '')

    print(f"[{chat_id}] {user_name}({user_id}): Join game")

    game_handler.join(chat_id, user_id, user_name)

    message = "*{}*".format(settings.start_game_text)
    send_message(bot, chat_id, message)
    show_board(bot, update)
    show_turn(bot, chat_id)


def place(bot, update, args):
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    coords = args[0]

    print(f"[{chat_id}] {user_id}: Place at {coords}")

    try:
        game_handler.place_stone(chat_id, user_id, coords)
        show_board(bot, update)
        show_turn(bot, chat_id)
    except GoGameException as exception:
        send_message(bot, chat_id, str(exception))


def pass_turn(bot, update):
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    user_name = update.message.from_user.name.replace('\'', '')

    print(f"[{chat_id}] {user_id}: Pass")

    try:
        game_handler.pass_turn(chat_id, user_id)
        if game_handler.both_players_passed(chat_id):
            game_over(bot, chat_id)
            return
        message = settings.player_passed_text.format(user_name)
        send_message(bot, chat_id, message)
        show_board(bot, update)
        show_turn(bot, chat_id)
    except GoGameException as exception:
        send_message(bot, chat_id, str(exception))


def show_board(bot, update):
    chat_id = update.message.chat_id
    image = game_handler.create_image(chat_id)
    bot.send_photo(chat_id, photo=image)


def show_turn(bot, chat_id):
    cur_player_name = game_handler.cur_player_name(chat_id)
    cur_color = game_handler.cur_player_color(chat_id)

    message = settings.cur_turn_text.format(cur_player_name, cur_color)
    send_message(bot, chat_id, message)


def display_proverb(bot, update):
    chat_id = update.message.chat_id

    proverb = random.choice(settings.go_proverbs)
    message = "\"_{}_\"".format(proverb)
    send_message(bot, chat_id, message)


def unknown(bot, update):
    chat_id = update.message.chat_id
    send_message(bot, chat_id, settings.unknown_command_text)


def send_message(bot, chat_id, text):
    bot.send_message(chat_id=chat_id, text=text, parse_mode=telegram.ParseMode.MARKDOWN)


def save_games():
    game_handler.save_games()


def game_over(bot, chat_id):
    # score = game_handler.calculate_result(chat_id)
    game_handler.remove_game(chat_id)
    send_message(bot, chat_id, settings.game_over_text)


def start_bot(key):
    logging.basicConfig(format=settings.logger_format, level=logging.INFO)

    updater = Updater(token=key)
    dispatcher = updater.dispatcher

    message_handlers = [
        CommandHandler(['start', 's'], start),
        CommandHandler(['new', 'n'], new_game),
        CommandHandler(['join', 'j'], join),
        CommandHandler(['place', 'p'], place, pass_args=True),
        CommandHandler('pass', pass_turn),
        CommandHandler(['show_board', 'sh'], show_board),
        CommandHandler(['proverb', 'pr'], display_proverb),
        MessageHandler(Filters.command, unknown)
    ]

    for handler in message_handlers:
        dispatcher.add_handler(handler)

    atexit.register(save_games)

    print('Polling...')
    updater.start_polling()
