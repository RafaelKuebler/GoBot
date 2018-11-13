from src.go import GoGame


go = GoGame()

command = input()
while command != 'quit':
    go.place_stone(command)

    stones = go.board.stones
    relevant = []
    for row in stones:
        for stone in row:
            if stone is not None:
                relevant.append(stone)
    print(f'Current stones: {relevant}')
    command = input()
