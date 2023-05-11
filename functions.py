import typing
from colorama import Back, Style

# Danger levels
CERTAIN_DEATH = 4
PROBABLE_DEATH = 3
POSSIBLE_DEATH = 2
HARM = 1

# Desire levels
KILL_DESIRE = 1000
FOOD_DESIRE = 100
MIDDLE_DESIRE = 10
TAIL_DESIRE = 1

# Deltas
MOVE_DELTAS = {'left': (-1, 0), 'right': (1, 0), 'up': (0, -1), 'down': (0, 1)}


# Stores game info
class Game:
    def __init__(self, game_id, board_width, board_height, game_mode, wrap, constrictor):
        self.game_id = game_id
        self.board_width = board_width
        self.board_height = board_height
        self.game_mode = game_mode
        self.wrap = wrap
        self.constrictor = constrictor

    # getters
    def get_board_width(self):
        return self.board_width

    def get_board_height(self):
        return self.board_height

    def get_wrap(self):
        return self.wrap

    def get_constrictor(self):
        return self.constrictor

    def print_info(self):
        print(f"Game ID: {self.game_id}")
        print(f"Board Width: {self.board_width}")
        print(f"Board Height: {self.board_height}")
        print(f"Game Mode: {self.game_mode}")
        print(f"Wrap: {self.wrap}")
        print(f"Constrictor: {self.constrictor}")


# Battlesnake metadata (Name, Author, Color, Head, Tail)
def info() -> typing.Dict:
    return {
        "apiversion": "1",
        "author": "Davis Stanko",
        "color": "#ff0000",
        "head": "dragon",
        "tail": "dragon",
    }


# Start of game
def start(game_state: typing.Dict):
    # create game class
    game_id = game_state["game"]["id"]

    board_width = game_state['board']['width']
    board_height = game_state['board']['height']

    game_mode = game_state["game"]["ruleset"]["name"]

    # check if game mode has wrap
    wrap = game_mode in ["wrapped", "wrapped-constrictor", "spicy-meteors"]

    # check if game mode is constrictor
    constrictor = game_mode in ["constrictor", "wrapped-constrictor"]

    # create game class
    global Current_game
    Current_game = Game(game_id, board_width, board_height,
                        game_mode, wrap, constrictor)

    # Print start message
    print(f"{Back.BLUE}Game START{Style.RESET_ALL}")
    Current_game.print_info()


# end is called when your Battlesnake finishes a game
def end(game_state: typing.Dict):
    print(f"{Back.BLUE}Game END{Style.RESET_ALL}")


def clean_move_list(moves):
    # find the minimum danger level among all moves
    min_danger = min(moves.values(), key=lambda x: x[1])[1]

    # create a new dictionary containing only the moves with the minimum danger level
    updated_moves = {move: danger for move,
                     danger in moves.items() if danger[1] == min_danger}

    # return the updated moves dictionary
    return updated_moves


def avoid_borders(player_head, board_width, board_height, moves):
    moves['left'] = (moves['left'][0],
                     CERTAIN_DEATH) if player_head['x'] == 0 else moves['left']
    moves['right'] = (
        moves['right'][0], CERTAIN_DEATH) if player_head['x'] == board_width - 1 else moves['right']
    moves['down'] = (moves['down'][0],
                     CERTAIN_DEATH) if player_head['y'] == 0 else moves['down']
    moves['up'] = (
        moves['up'][0], CERTAIN_DEATH) if player_head['y'] == board_height - 1 else moves['up']

    return clean_move_list(moves)


def avoid_snakes(game_state, player_head, moves, snakes, constrictor):
    # Check for constrictor game mode
    if not constrictor:
        # Check if the tail is going to move out of the way
        for snake in snakes:
            if snake['body'][-1] != snake['body'][-2]:  # Tail doubled up
                snake['body'].pop()

    # Check for collision with other snakes
    for snake in snakes:
        danger = CERTAIN_DEATH if snake['id'] == game_state['you']['id'] else PROBABLE_DEATH
        for move, delta in MOVE_DELTAS.items():
            adjacent_tiles = [(player_head['x'] + delta[0],
                               player_head['y'] + delta[1])]
            if adjacent_tiles in snake['body']:
                moves[move] = (moves[move][1], danger)

    return clean_move_list(moves)


def head_on_collision(game_state, player_head, moves):
    # Check future moves
    for direction, move in moves.items():
        nextMoves = []
        # Get the coordinates for each safe move
        if direction == "left":
            nextMoves.append((player_head['x'] - 1, player_head['y']))
        elif direction == "right":
            nextMoves.append((player_head['x'] + 1, player_head['y']))
        elif direction == "up":
            nextMoves.append((player_head['x'], player_head['y'] + 1))
        elif direction == "down":
            nextMoves.append((player_head['x'], player_head['y'] - 1))
        # Get the coordinates for each safe move's adjacent tile
        future_moves = []
        for x in nextMoves:
            future_moves.append((x[0] - 1, x[1]))
            future_moves.append((x[0] + 1, x[1]))
            future_moves.append((x[0], x[1] - 1))
            future_moves.append((x[0], x[1] + 1))
        # Get list of all snake bodies
        opponents = game_state['board']['snakes']
        # Remove myself from the list of opponents
        for x in opponents:
            if x['id'] == game_state["you"]["id"]:
                opponents.remove(x)
                break
        for x in future_moves:
            for oppponent in opponents:
                opponentHead = (oppponent["head"]['x'], oppponent["head"]['y'])
                # If the opponent is bigger than me
                if opponentHead == x and oppponent["length"] >= game_state["you"]["length"]:
                    # Mark the move as potentially unsafe
                    moves[direction] = (moves[direction][0], POSSIBLE_DEATH)
                    break
                # If the opponent is smaller than me
                elif opponentHead == x and oppponent["length"] < game_state["you"]["length"]:
                    # Mark the move as a potential kill
                    moves[direction] = (moves[direction][0], moves[direction][1] + KILL_DESIRE)
    # Clean move list
    moves = clean_move_list(moves)
    return moves


def avoid_hazards(game_state, player_head, moves, player_health):
    # Get hazard damage
    hazard_damage = game_state['game']['ruleset']['settings']['hazardDamagePerTurn']

    # Check for hazards at each adjacent position
    for move, delta in MOVE_DELTAS.items():
        adjacent_tiles = (player_head['x'] +
                          delta[0], player_head['y'] + delta[1])
        if adjacent_tiles in game_state['board']['hazards']:
            # Hazard damage is lethal
            if hazard_damage >= player_health:
                moves[move] = moves[move][1], CERTAIN_DEATH
            # Hazard damage is not lethal
            else:
                moves[move] = moves[move][1], HARM

    return clean_move_list(moves)


def aim_for_food(game_state, player_head, moves):
    # Get the coordinates for each food
    foods = [food for food in game_state['board']['food']
             if food not in game_state['board']['hazards']]

    # Find the closest food
    closest_food = min(foods, key=lambda food: abs(
        player_head['x'] - food['x']) + abs(player_head['y'] - food['y']))

    # Add desire to move towards food
    for direction, delta in MOVE_DELTAS.items():
        if direction in moves:
            x, y = player_head['x'] + delta[0], player_head['y'] + delta[1]
            if x == closest_food['x'] and y == closest_food['y']:
                moves[direction] = (moves[direction][0],
                                    moves[direction][1] + FOOD_DESIRE)

    return moves


def aim_for_middle(game_state, player_head, moves):
    # find middle
    middle = (game_state['board']['width'] // 2,
              game_state['board']['height'] // 2)

    # Add desire to move towards middle
    if 'right' in moves and player_head['x'] < middle[0]:
        moves['right'] = (moves['right'][0], moves['right'][1] + MIDDLE_DESIRE)
    if 'left' in moves and player_head['x'] > middle[0]:
        moves['left'] = (moves['left'][0], moves['left'][1] + MIDDLE_DESIRE)
    if 'up' in moves and player_head['y'] < middle[1]:
        moves['up'] = (moves['up'][0], moves['up'][1] + MIDDLE_DESIRE)
    if 'down' in moves and player_head['y'] > middle[1]:
        moves['down'] = (moves['down'][0], moves['down'][1] + MIDDLE_DESIRE)

    return moves


def chase_tail(game_state, player_head, moves):
    # find tail
    tail = game_state['you']['body'][-1]

    # Add desire to move towards tail
    if 'right' in moves and player_head['x'] < tail['x']:
        moves['right'] = (moves['right'][0], moves['right'][1] + TAIL_DESIRE)
    if 'left' in moves and player_head['x'] > tail['x']:
        moves['left'] = (moves['left'][0], moves['left'][1] + TAIL_DESIRE)
    if 'up' in moves and player_head['y'] < tail['y']:
        moves['up'] = (moves['up'][0], moves['up'][1] + TAIL_DESIRE)
    if 'down' in moves and player_head['y'] > tail['y']:
        moves['down'] = (moves['down'][0], moves['down'][1] + TAIL_DESIRE)

    return moves


# move is called on every turn
def move(game_state: typing.Dict) -> typing.Dict:
    # Print turn
    print(f"{Back.BLUE}Turn {game_state['turn']}{Style.RESET_ALL}")

    # get info from game class' getters
    board_width = Current_game.get_board_width()
    board_height = Current_game.get_board_height()
    wrap = Current_game.get_wrap()
    constrictor = Current_game.get_constrictor()

    # reset list of valid moves
    # direction, danger level, desire level
    moves = {"up": (0, 0), "down": (0, 0), "left": (0, 0), "right": (0, 0)}

    # locate the head of the snake
    player_head = game_state["you"]["body"][0]

    # get player health
    player_health = game_state["you"]["health"]

    # get snake body part coordinates
    snakes = game_state['board']['snakes']

    # Avoid borders if wrap is not enabled
    if wrap is False:
        moves = avoid_borders(player_head, board_width, board_height, moves)
        print(f"Moves after avoid_borders: {moves}")

    # Avoid snakes
    moves = avoid_snakes(game_state, player_head, moves, snakes, constrictor)
    print(f"Moves after avoid_snakes: {moves}")

    # Head on collision logic
    moves = head_on_collision(game_state, player_head, moves)
    print(f"Moves after head_on_collision: {moves}")

    # Avoid hazards if hazard are on the board
    if game_state['board']['hazards']:
        moves = avoid_hazards(game_state, player_head, moves, player_health)
        print(f"Moves after avoid_hazards: {moves}")

    # Aim for food
    moves = aim_for_food(game_state, player_head, moves)
    print(f"Moves after aim_for_food: {moves}")

    # Aim for middle
    moves = aim_for_middle(game_state, player_head, moves)
    print(f"Moves after aim_for_middle: {moves}")

    # Chase tail if not contrictor
    if not constrictor:
        moves = chase_tail(game_state, player_head, moves)
        print(f"Moves after chase_tail: {moves}")

    best_move = max(moves, key=lambda key: moves[key][1])
    print(f"Best move: {best_move}")

    # Move
    return {"move": best_move}
