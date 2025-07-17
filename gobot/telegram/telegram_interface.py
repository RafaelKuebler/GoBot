import html
import logging
import random

from telegram import Bot, Update
from telegram.ext import Application, ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

from gobot import settings
from gobot.go.exceptions import KoException
from gobot.telegram import proverbs
from gobot.telegram.gamehandler import GameHandler, GameHandlerException, TelegramGoGame

logger = logging.getLogger(__name__)
game_handler: GameHandler


def setup_app() -> Application:
    global game_handler

    logger.info("Setting up telegram interface")
    application = ApplicationBuilder().token(settings.get_settings().TOKEN).build()

    game_handler = GameHandler()

    logger.info("Registering message handlers...")
    application.add_handlers(
        [
            CommandHandler(["start", "s"], _start_command),
            CommandHandler(["new", "n"], _new_game_command),
            CommandHandler(["join", "j"], _join_command),
            CommandHandler(["place", "p"], _place_command, has_args=True),
            CommandHandler(["pass"], _pass_turn_command),
            CommandHandler(["show", "sh"], _show_board_command),
            CommandHandler(["proverb", "pr"], _display_proverb_command),
            MessageHandler(filters.COMMAND, _unknown_command),
        ]
    )
    application.add_error_handler(_on_error)  # type: ignore

    return application


async def _on_error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    assert update.effective_chat
    logger.error("Exception while handling an update:", exc_info=context.error)
    await send_message(
        context.bot,
        update.effective_chat.id,
        "An unexpected error ocurred! 😟 If you want to help fix it, please contact the developer! ❤️",
    )


async def _unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    assert update.effective_chat
    assert update.message
    assert update.message.from_user

    chat_id = update.effective_chat.id
    user_name = update.message.from_user.name.replace("'", "")
    logger.info(f"Chat {chat_id}, user {user_name} called an unkown command {update.message.text}")
    await send_message(context.bot, chat_id, "This command is not known to me 🤔\nPlease call /start for a list of known commands!")


async def _start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    assert update.effective_chat
    assert update.message
    assert update.message.from_user

    chat_id = update.effective_chat.id
    user_name = update.message.from_user.name.replace("'", "")
    logger.info(f"Chat {chat_id}, user {user_name} called /start")

    await send_message(
        context.bot,
        chat_id,
        "Hi! 🤗 I am <b>Go Sensei</b> and will take care of your <b>Go</b> game!",
    )
    await send_message(
        context.bot,
        chat_id,
        (
            "These are my available commands:<br>"
            "  /start - to show this introductory message<br>"
            "  /new - start a new 9x9 game<br>"
            "  /join - join an already created game<br>"
            "  /place <i>coords</i> - play a stone of your color at given coordinates (e.g. <code>/place a1</code>)<br>"
            "  /pass - to skip your turn<br>"
            "  /show - show the current board state<br>"
            "  /proverb - display a proverb"
        ),
    )
    await send_message(context.bot, chat_id, "To get started, simply send /new to this chat and have a friend join you with /join!")


async def _new_game_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    assert update.effective_chat
    assert update.message
    assert update.message.from_user

    chat_id = update.effective_chat.id
    user_id = update.message.from_user.id
    user_name = update.message.from_user.name.replace("'", "")
    board_size = 9
    if context.args:
        board_size = int(context.args[0])
    logger.info(f"Chat {chat_id}, user {user_name} called /new {board_size}")

    try:
        game_handler.new_game(chat_id, user_id, user_name, board_size)
        await send_message(context.bot, chat_id, "<b>You created a new game!</b> Another player can join with the /join command.")
    except GameHandlerException as e:
        await send_message(context.bot, chat_id, html.escape(str(e)))


async def _join_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    assert update.effective_chat
    assert update.message
    assert update.message.from_user

    chat_id = update.effective_chat.id
    user_id = update.message.from_user.id
    user_name = update.message.from_user.name.replace("'", "")
    logger.info(f"Chat {chat_id}, user {user_name} called /join")

    try:
        game = game_handler.join(chat_id, user_id, user_name)
        await send_message(context.bot, chat_id, "<b>Let the game begin!</b>")
        await _show_board_command(update, context, game)
        await _show_turn(context.bot, chat_id, game)
    except GameHandlerException as e:
        await send_message(context.bot, chat_id, html.escape(str(e)))


async def _place_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    assert update.effective_chat
    assert update.message
    assert update.message.from_user

    chat_id = update.effective_chat.id
    user_id = update.message.from_user.id
    user_name = update.message.from_user.name.replace("'", "")
    if not context.args:
        await send_message(context.bot, chat_id, "Please supply coordinates (example: <code>/place a1</code>)!")
        return
    coords = html.escape(context.args[0])
    logger.info(f"Chat {chat_id}, user {user_name} called /place at {coords}")

    try:
        game = game_handler.place_stone(chat_id, user_id, coords)
        await _show_board_command(update, context, game)
        await _show_turn(context.bot, chat_id, game)
    except KoException as e:
        await send_message(context.bot, chat_id, html.escape(str(e)))
        await send_message(context.bot, chat_id, "<i>If you don't like Ko don't Play Go.</i>")
    except GameHandlerException as e:
        await send_message(context.bot, chat_id, html.escape(str(e)))


async def _pass_turn_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    assert update.effective_chat
    assert update.message
    assert update.message.from_user

    chat_id = update.effective_chat.id
    user_id = update.message.from_user.id
    user_name = update.message.from_user.name.replace("'", "")
    logger.info(f"Chat {chat_id}, user {user_name} called /pass")

    try:
        game = game_handler.pass_turn(chat_id, user_id)
        if game.both_players_passed:
            await _game_over(context.bot, chat_id)
            return
        await send_message(context.bot, chat_id, f"Player {html.escape(user_name)} passed")
        await _show_board_command(update, context, game)
        await _show_turn(context.bot, chat_id, game)
    except GameHandlerException as e:
        await send_message(context.bot, chat_id, html.escape(str(e)))


async def _game_over(bot: Bot, chat_id: int) -> None:
    # TODO: score = game_handler.calculate_result(chat_id)
    game_handler.remove_game(chat_id)
    await send_message(bot, chat_id, "The game is over. Well played!")


async def _show_board_command(update: Update, context: ContextTypes.DEFAULT_TYPE, game_: TelegramGoGame | None = None) -> None:
    assert update.effective_chat

    chat_id = update.effective_chat.id
    game = game_ or game_handler.get_game_with_chat_id(chat_id, raise_if_not_found=True)

    try:
        image = game.take_screenshot()
        await context.bot.send_photo(chat_id, photo=image)
    except GameHandlerException as e:
        await send_message(context.bot, chat_id, str(e))


async def _show_turn(bot: Bot, chat_id: int, game: TelegramGoGame) -> None:
    if game.cur_player_name is None:
        return
    cur_player_name = html.escape(game.cur_player_name)
    cur_color = game.cur_player_color
    await send_message(bot, chat_id, f"It is {cur_player_name}'s ({cur_color}) turn")


async def _display_proverb_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    assert update.effective_chat
    assert update.message
    assert update.message.from_user

    chat_id = update.effective_chat.id
    user_name = update.message.from_user.name.replace("'", "")
    logger.info(f"Chat {chat_id}, user {user_name} called /proverb")

    proverb = random.choice(proverbs.go_proverbs)
    message = f"&quot;<i>{html.escape(proverb)}</i>&quot;"
    await send_message(context.bot, chat_id, message)


async def send_message(bot: Bot, chat_id: int, text: str) -> None:
    await bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML")
