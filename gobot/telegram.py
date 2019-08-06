import os
import sys
import logging
import telegram
import random
import atexit
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

from . import settings
from .exceptions import GoGameException
from .go.exceptions import KoException
from .gamehandler import GameHandler

__author__ = "Rafael Kübler da Silva <rafael_kuebler@yahoo.es>"
__version__ = "0.1"

game_handler = GameHandler()


def start(bot, update) -> None:
    # TODO: parameter types
    chat_id: int = update.message.chat_id
    user_name: str = update.message.from_user.name.replace('\'', '')
    logging.info(f"Chat {chat_id}, user {user_name} called /start")

    send_message(bot, chat_id, settings.greeting)
    send_message(bot, chat_id, settings.commands)


def new_game(bot, update) -> None:
    # TODO: parameter types
    chat_id: int = update.message.chat_id
    user_id: int = update.message.from_user.id
    user_name: str = update.message.from_user.name.replace('\'', '')
    logging.info(f"Chat {chat_id}, user {user_name} called /new")

    game_handler.new_game(chat_id, user_id)
    game_handler.join(chat_id, user_id, user_name)

    send_message(bot, chat_id, settings.new_game_text)


def join(bot, update) -> None:
    # TODO: parameter types
    chat_id: int = update.message.chat_id
    user_id: int = update.message.from_user.id
    user_name: str = update.message.from_user.name.replace('\'', '')
    logging.info(f"Chat {chat_id}, user {user_name} called /join")

    game_handler.join(chat_id, user_id, user_name)

    message: str = f"*{settings.start_game_text}*"
    send_message(bot, chat_id, message)
    show_board(bot, update)
    show_turn(bot, chat_id)


def place(bot, update, args) -> None:
    # TODO: parameter types
    chat_id: int = update.message.chat_id
    user_id: int = update.message.from_user.id
    user_name: str = update.message.from_user.name.replace('\'', '')
    if not args:
        send_message(bot, chat_id, settings.error_no_coords)
        return
    coords: str = args[0]
    logging.info(f"Chat {chat_id}, user {user_name} called /place at {coords}")

    try:
        game_handler.place_stone(chat_id, user_id, coords)
        show_board(bot, update)
        show_turn(bot, chat_id)
    except KoException as exception:
        send_message(bot, chat_id, str(exception))
        ko_proverb: str = f"\"_{settings.ko_proverb}_\""
        send_message(bot, chat_id, ko_proverb)
    except GoGameException as exception:
        send_message(bot, chat_id, str(exception))


def pass_turn(bot, update) -> None:
    # TODO: parameter types
    chat_id: int = update.message.chat_id
    user_id: int = update.message.from_user.id
    user_name: str = update.message.from_user.name.replace('\'', '')
    logging.info(f"Chat {chat_id}, user {user_name} called /pass")

    try:
        game_handler.pass_turn(chat_id, user_id)
        if game_handler.both_players_passed(chat_id):
            game_over(bot, chat_id)
            return
        message: str = settings.player_passed_text.format(user_name)
        send_message(bot, chat_id, message)
        show_board(bot, update)
        show_turn(bot, chat_id)
    except GoGameException as exception:
        send_message(bot, chat_id, str(exception))


def show_board(bot, update) -> None:
    # TODO: parameter types
    chat_id: int = update.message.chat_id

    image = game_handler.create_image(chat_id)
    bot.send_photo(chat_id, photo=image)


def show_turn(bot, chat_id) -> None:
    # TODO: parameter types
    cur_player_name: str = game_handler.cur_player_name(chat_id)
    cur_color: str = game_handler.cur_player_color(chat_id)

    message = settings.cur_turn_text.format(cur_player_name, cur_color)
    send_message(bot, chat_id, message)


def display_proverb(bot, update) -> None:
    # TODO: parameter types
    chat_id: int = update.message.chat_id
    user_name: str = update.message.from_user.name.replace('\'', '')
    logging.info(f"Chat {chat_id}, user {user_name} called /proverb")

    proverb: str = random.choice(settings.go_proverbs)
    message: str = f"\"_{proverb}_\""
    send_message(bot, chat_id, message)


def unknown(bot, update) -> None:
    # TODO: parameter types
    chat_id: int = update.message.chat_id
    send_message(bot, chat_id, settings.unknown_command_text)


def send_message(bot, chat_id, text) -> None:
    # TODO: parameter types
    bot.send_message(chat_id=chat_id, text=text, parse_mode=telegram.ParseMode.MARKDOWN)


def save_games() -> None:
    game_handler.save_games()


def game_over(bot, chat_id) -> None:
    # score = game_handler.calculate_result(chat_id)
    game_handler.remove_game(chat_id)
    send_message(bot, chat_id, settings.game_over_text)


def start_bot(key: str) -> None:
    logging.basicConfig(format=settings.logger_format, level=logging.INFO)

    updater = Updater(token=key)
    dispatcher = updater.dispatcher

    message_handlers = [
        CommandHandler(['start', 's'], start),
        CommandHandler(['new', 'n'], new_game),
        CommandHandler(['join', 'j'], join),
        CommandHandler(['place', 'p'], place, pass_args=True),
        CommandHandler('pass', pass_turn),
        CommandHandler(['show', 'sh'], show_board),
        CommandHandler(['proverb', 'pr'], display_proverb),
    ]

    logging.info("Registering message handlers...")
    for handler in message_handlers:
        dispatcher.add_handler(handler)
        logging.info(f"Added command {handler.command} handler")
    dispatcher.add_handler(MessageHandler(Filters.command, unknown))
    logging.info(f"Added unknown command handler")

    atexit.register(save_games)

    if 'MODE' not in os.environ:
        logging.error("No MODE specified!")
        sys.exit(1)
    elif os.environ.get('MODE') == 'DEBUG':
        logging.info("Started polling")
        updater.start_polling()
    elif os.environ.get('MODE') == 'RELEASE':
        port = int(os.environ.get('PORT', '8443'))
        app_name = os.environ.get('HEROKU_APP_NAME')

        updater.start_webhook(listen='0.0.0.0',
                              port=port,
                              url_path=key)
        updater.bot.set_webhook(f'https://{app_name}.herokuapp.com/{key}')
