import os
import sys
import logging
import telegram
import random
from typing import List, Optional
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram.bot import Bot
from telegram.update import Update

from . import settings
from .exceptions import GoGameException
from .go.exceptions import KoException
from .gamehandler import GameHandler

__author__ = "Rafael Kübler da Silva <rafael_kuebler@yahoo.es>"
__version__ = "0.1"


class TelegramInterface:
    def __init__(self):
        self.game_handler: Optional[GameHandler] = None

    def _start(self, bot: Bot, update: Update) -> None:
        chat_id: int = update.message.chat_id
        user_name: str = update.message.from_user.name.replace('\'', '')
        logging.info(f"Chat {chat_id}, user {user_name} called /start")

        self.send_message(bot, chat_id, settings.greeting)
        self.send_message(bot, chat_id, settings.commands)

    def _new_game(self, bot: Bot, update: Update) -> None:
        chat_id: int = update.message.chat_id
        user_id: int = update.message.from_user.id
        user_name: str = update.message.from_user.name.replace('\'', '')
        logging.info(f"Chat {chat_id}, user {user_name} called /new")

        self.game_handler.new_game(chat_id, user_id)
        self.game_handler.join(chat_id, user_id, user_name)

        self.send_message(bot, chat_id, settings.new_game_text)

    def _join(self, bot: Bot, update: Update) -> None:
        chat_id: int = update.message.chat_id
        user_id: int = update.message.from_user.id
        user_name: str = update.message.from_user.name.replace('\'', '')
        logging.info(f"Chat {chat_id}, user {user_name} called /join")

        self.game_handler.join(chat_id, user_id, user_name)

        message: str = f"*{settings.start_game_text}*"
        self.send_message(bot, chat_id, message)
        self.show_board(bot, update)
        self.show_turn(bot, chat_id)

    def _place(self, bot: Bot, update: Update, args: List[str]) -> None:
        chat_id: int = update.message.chat_id
        user_id: int = update.message.from_user.id
        user_name: str = update.message.from_user.name.replace('\'', '')
        if not args:
            self.send_message(bot, chat_id, settings.error_no_coords)
            return
        coords: str = args[0]
        logging.info(f"Chat {chat_id}, user {user_name} called /place at {coords}")

        try:
            self.game_handler.place_stone(chat_id, user_id, coords)
            self.show_board(bot, update)
            self.show_turn(bot, chat_id)
        except KoException as exception:
            self.send_message(bot, chat_id, str(exception))
            ko_proverb: str = f"\"_{settings.ko_proverb}_\""
            self.send_message(bot, chat_id, ko_proverb)
        except GoGameException as exception:
            self.send_message(bot, chat_id, str(exception))

    def _pass_turn(self, bot: Bot, update: Update) -> None:
        chat_id: int = update.message.chat_id
        user_id: int = update.message.from_user.id
        user_name: str = update.message.from_user.name.replace('\'', '')
        logging.info(f"Chat {chat_id}, user {user_name} called /pass")

        try:
            self.game_handler.pass_turn(chat_id, user_id)
            if self.game_handler.both_players_passed(chat_id):
                self._game_over(bot, chat_id)
                return
            message: str = settings.player_passed_text.format(user_name)
            self.send_message(bot, chat_id, message)
            self.show_board(bot, update)
            self.show_turn(bot, chat_id)
        except GoGameException as exception:
            self.send_message(bot, chat_id, str(exception))

    def _unknown(self, bot: Bot, update: Update) -> None:
        chat_id: int = update.message.chat_id
        self.send_message(bot, chat_id, settings.unknown_command_text)

    def _game_over(self, bot: Bot, chat_id: int) -> None:
        # score = game_handler.calculate_result(chat_id)
        self.game_handler.remove_game(chat_id)
        self.send_message(bot, chat_id, settings.game_over_text)

    def show_board(self, bot: Bot, update: Update) -> None:
        chat_id: int = update.message.chat_id

        image = self.game_handler.create_image(chat_id)
        bot.send_photo(chat_id, photo=image)

    def show_turn(self, bot: Bot, chat_id: int) -> None:
        cur_player_name: str = self.game_handler.cur_player_name(chat_id)
        cur_color: str = self.game_handler.cur_player_color(chat_id)

        message = settings.cur_turn_text.format(cur_player_name, cur_color)
        self.send_message(bot, chat_id, message)

    def display_proverb(self, bot: Bot, update: Update) -> None:
        chat_id: int = update.message.chat_id
        user_name: str = update.message.from_user.name.replace('\'', '')
        logging.info(f"Chat {chat_id}, user {user_name} called /proverb")

        proverb: str = random.choice(settings.go_proverbs)
        message: str = f"\"_{proverb}_\""
        self.send_message(bot, chat_id, message)

    @staticmethod
    def send_message(bot: Bot, chat_id: int, text: str) -> None:
        bot.send_message(chat_id=chat_id, text=text, parse_mode=telegram.ParseMode.MARKDOWN)

    def start_bot(self, key: str) -> None:
        logging.info("Setting up telegram interface")
        self.game_handler = GameHandler()

        updater = Updater(token=key)
        dispatcher = updater.dispatcher

        message_handlers = [
            CommandHandler(['start', 's'], self._start),
            CommandHandler(['new', 'n'], self._new_game),
            CommandHandler(['join', 'j'], self._join),
            CommandHandler(['place', 'p'], self._place, pass_args=True),
            CommandHandler('pass', self._pass_turn),
            CommandHandler(['show', 'sh'], self.show_board),
            CommandHandler(['proverb', 'pr'], self.display_proverb),
        ]

        logging.info("Registering message handlers")
        for handler in message_handlers:
            dispatcher.add_handler(handler)
            logging.info(f"Added command {handler.command} handler")
        dispatcher.add_handler(MessageHandler(Filters.command, self._unknown))
        logging.info(f"Added unknown command handler")

        if 'MODE' not in os.environ:
            logging.error("No MODE specified!")
            sys.exit(1)
        elif os.environ.get('MODE') == 'DEBUG':
            logging.info("Start polling")
            updater.start_polling()
        elif os.environ.get('MODE') == 'RELEASE':
            port = int(os.environ.get('PORT', '8443'))
            app_name = os.environ.get('HEROKU_APP_NAME')

            logging.info("Setting up webhook")
            updater.start_webhook(listen='0.0.0.0',
                                  port=port,
                                  url_path=key)
            updater.bot.set_webhook(f'https://{app_name}.herokuapp.com/{key}')
