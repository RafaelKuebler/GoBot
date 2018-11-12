import settings
import logging
from gamehandler import GameHandler
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

__author__ = "Rafael Kübler da Silva <rafael_kuebler@yahoo.es>"
__version__ = "0.1"

game_handler = GameHandler()


def start(bot, update):
    chat_id = update.message.chat_id
    bot.send_message(chat_id=chat_id, text=settings.greeting)
    bot.send_message(chat_id=chat_id, text=settings.commands)


def new_game(bot, update):
    chat_id = update.message.chat_id
    players = get_players(chat_id)
    game_handler.new_game(chat_id, players)
    show_board(bot, update)


def place(bot, update):
    chat_id = update.message.chat_id
    player = update.message.from_user.username
    coords = update.message.text
    try:
        game_handler.place_stone(chat_id, player, coords)
        show_board(bot, update)
    except Exception as exception:
        bot.send_message(chat_id=chat_id, text=str(exception))


def pass_turn(bot, update):
    chat_id = update.message.chat_id
    game_handler.create_image(chat_id)
    # TODO: pass
    bot.send_message(chat_id=update.message.chat_id, text=f"Player x passed")
    show_board(bot, update)


def show_board(bot, update):
    # TODO: show_board image
    chat_id = update.message.chat_id
    image = game_handler.create_image(chat_id)
    cur_player = game_handler.cur_player(chat_id)
    bot.send_message(chat_id=update.message.chat_id, text=f"*Here goes your board image*")
    bot.send_message(chat_id=update.message.chat_id, text=f"It is {cur_player}'s turn")


def unknown(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Sorry, I didn't understand that command.")


def get_players(chat_id):
    # TODO: fetch users ids in the group with chat_id
    return [f"{chat_id}:Rafael", f"{chat_id}:Willy"]


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)

    updater = Updater(token=settings.token)
    dispatcher = updater.dispatcher

    message_handlers = [
        CommandHandler('start', start),
        CommandHandler('new', new_game),
        CommandHandler('place', place),
        CommandHandler('pass', pass_turn),
        CommandHandler('show_board', show_board),
        MessageHandler(Filters.command, unknown)
    ]

    for handler in message_handlers:
        dispatcher.add_handler(handler)

    updater.start_polling()
