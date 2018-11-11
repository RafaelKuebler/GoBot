import settings
import logging
from exceptions import InexistentGameException, IncorrectTurnException,\
    CoordOccupiedException, AlreadyEnoughPlayersException
from gamehandler import GameHandler
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

__author__ = "Rafael Kuebler da Silva <rafael_kuebler@yahoo.es>"
__version__ = "0.1"

game_handler = GameHandler()


def start(bot, update):
    chat_id = update.message.chat_id
    bot.send_message(chat_id=chat_id, text=settings.greeting)
    bot.send_message(chat_id=chat_id, text=settings.commands)


def get_players(chat_id):
    return ["Rafael", "Willy"]  #TODO


def new_game(bot, update):
    chat_id = update.message.chat_id
    players = get_players(chat_id)
    result = game_handler.new_game(chat_id, players)
    bot.send_message(chat_id=update.message.chat_id, text=result)


def place(bot, update):
    chat_id = update.message.chat_id
    player = update.message.from_user.username
    coords = update.message.text
    try:
        result = game_handler.place_stone(chat_id, player, coords)
        bot.send_message(chat_id=chat_id, text=result)
    except InexistentGameException:
        bot.send_message(chat_id=chat_id, text="Please start a game with /new first!")
    except IncorrectTurnException:
        bot.send_message(chat_id=chat_id, text="It is not your turn!")
    except CoordOccupiedException:
        bot.send_message(chat_id=chat_id, text="This coordinate already holds a stone!")


def pass_turn(bot, update):
    pass
    #bot.send_message(chat_id=update.message.chat_id, text=f"Player x passed")


def unknown(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Sorry, I didn't understand that command.")


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
        MessageHandler(Filters.command, unknown)
    ]

    for handler in message_handlers:
        dispatcher.add_handler(handler)

    updater.start_polling()
