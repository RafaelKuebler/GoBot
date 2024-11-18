CREATE TABLE IF NOT EXISTS players (
    id int primary key,
    name varchar(100)
);

CREATE TABLE IF NOT EXISTS games (
    chat_id int primary key,
    player1 int references players (id),
    player2 int references players (id),
    size_x int NOT NULL,
    size_y int NOT NULL,
    state JSON DEFAULT '{}',
    turn_color varchar(10) NOT NULL DEFAULT 'black',
    turn_player int references players (id) NOT NULL,
    last_stone varchar(10),
    last_capt_stone varchar(10),
    player_passed varchar(11) NOT NULL
);
