
greeting = "*Hi!* I am *Go Sensei* and will take care of your *Go* game!"
commands = "These are my available commands:\n" \
           "  /new - start a new game\n" \
           "  /join - join an already created game\n" \
           "  /place _coords_ - play stone at given coordinates (e.g. _/place a1_)\n" \
           "  /pass - to pass your turn\n" \
           "  /proverb - display a proverb\n" \
           "  /save - to save the game on the server"

new_game_text = "You created a new game! Another player can join with the /join command."
start_game_text = "Let the game begin!"
player_passed_text = "Player {} passed"
cur_turn_text = "It is {}'s ({}) turn"
game_over_text = "The game is over. Well played!"

patience_proverbs = [
    "One moment of patience may ward off a great disaster; one moment of impatience may ruin a whole life.",
    "Patience is power; with time and patience, the mulberry leaf becomes a silk gown.",
    "Nature, time and patience are the three great physicians.",
    "Have patience, the grass will be milk soon enough.",
    "Patience is a virtue.",
    "Rice eaten in haste chokes."
]

go_proverbs = [
    "Don't play 1, 2, 3–just play 3.",
    "Play slow, win slow; play fast, lose fast.",
    "Lose your first 50 games as quickly as possible.",
    "Your enemy's key point is your own key point.",
    "Urgent points before big points.",
    "Make a fist before striking.",
    "Make territory while attacking.",
    "A rich man should not pick quarrels.",
    "Sacrifice plums for peaches.",
    "Don't go fishing while your house is on fire.",
    "Don't follow proverbs blindly.",
    "The Threat Is Stronger Than Its Execution.",
    "Distant water won't help to put out a fire close at hand.",
    "The fearful suffer a thousand deaths, the brave only one.",
    "Make a feint to the east while attacking in the west.",
    "When in doubt, tenuki (play somewhere else).",
    "People in glass houses shouldn't throw stones.",
    "Beginners play atari (state of a stone or group of stones that has only one liberty).",
    "Lead away a goat in passing.",
    "Those who are good at winning, don't usually fight.",
    "If you cannot succeed, then die gloriously.",
    "Territory really exists only in the end.",
    "In the sound of the stone your can hear its purpose.",
    "If White takes all four corners, Black should resign; if Black takes all four corners, Black should also resign.",
    "Proverbs do not apply to White.",
    "Don't reduce your own liberties."
]

ko_proverb = "If you don't like Ko don't Play Go."

error_no_coords = "Please supply coordinates!"
error_inexistent_game = "Please start a game with /new first!"
error_incorrect_turn = "It is not your turn!"
error_not_enough_players = "Another player needs to join the game with /join!"
error_already_enough_players = "The game already has 2 players!"
error_permissions = "You are not part of a current game and therefore not allowed to perform this action!"

logger_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
