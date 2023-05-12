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
    # Check if the Battlesnake is at the edge of the board
    if player_head['x'] == 0:
        moves['left'] = (CERTAIN_DEATH, moves['left'][1])
    if player_head['x'] == board_width - 1:
        moves['right'] = (CERTAIN_DEATH, moves['right'][1])
    if player_head['y'] == 0:
        moves['down'] = (CERTAIN_DEATH, moves['down'][1])
    if player_head['y'] == board_height - 1:
        moves['up'] = (CERTAIN_DEATH, moves['up'][1])

    # Clean move list
    moves = clean_move_list(moves)

    # Return the updated moves dictionary
    return moves


def avoid_snakes(game_state, player_head, moves, snakes, constrictor):
    # Check for constrictor game mode
    if constrictor is False:
        # Check if the tail is going to move out of the way
        for snake in snakes:
            # Check if the snake just ate food
            if snake['body'][-1] != snake['body'][-2]:  # Tail doubled up
                # Remove the tail from the list of snakes
                snake['body'].pop()

    # Prevent the Battlesnake from colliding with other Battlesnakes including itself
    for snake in snakes:
        # if the snake is the player danger = 5 otherwise danger = 4
        danger = CERTAIN_DEATH if snake['id'] == game_state['you']['id'] else PROBABLE_DEATH
        for body_part in snake['body']:
            # Check if body part is to the left of head
            if body_part['x'] == player_head['x'] - 1 and body_part['y'] == player_head['y']:
                moves['left'] = (moves['left'][0], danger)
            # Check if body part is to the right of head
            elif body_part['x'] == player_head['x'] + 1 and body_part['y'] == player_head['y']:
                moves['right'] = (moves['right'][0], danger)
            # Check if body part is below head
            elif body_part['x'] == player_head['x'] and body_part['y'] == player_head['y'] - 1:
                moves['down'] = (moves['down'][0], danger)
            # Check if body part is above head
            elif body_part['x'] == player_head['x'] and body_part['y'] == player_head['y'] + 1:
                moves['up'] = (moves['up'][0], danger)

    # Clean move list
    moves = clean_move_list(moves)

    # Return the updated moves dictionary
    return moves


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

    # Check if there are hazards on the board
    if len(game_state['board']['hazards']) > 0:
        # Get hazard coordinates
        for i in game_state['board']['hazards']:
            if i['x'] == player_head['x'] - 1 and i['y'] == player_head['y']:
                # Hazard damage is lethal
                if hazard_damage >= player_health:
                    moves['left'] = moves['left'][1], CERTAIN_DEATH
                # Hazard damage is not lethal
                else:
                    moves['left'] = moves['left'][1], HARM
            if i['x'] == player_head['x'] + 1 and i['y'] == player_head['y']:
                # Hazard damage is lethal
                if hazard_damage >= player_health:
                    moves['right'] = moves['right'][1], CERTAIN_DEATH
                # Hazard damage is not lethal
                else:
                    moves['right'] = moves['right'][1], HARM
            if i['y'] == player_head['y'] - 1 and i['x'] == player_head['x']:
                # Check if hazard damage is lethal
                if hazard_damage >= player_health:
                    moves['down'] = moves['down'][1], CERTAIN_DEATH
                # Hazard damage is not lethal
                else:
                    moves['down'] = moves['down'][1], HARM
            if i['y'] == player_head['y'] + 1 and i['x'] == player_head['x']:
                # Check if hazard damage is lethal
                if hazard_damage >= player_health:
                    moves['up'] = moves['up'][1], CERTAIN_DEATH
                # Hazard damage is not lethal
                else:
                    moves['up'] = moves['up'][1], HARM

    # Clean move list
    moves = clean_move_list(moves)

    return moves


def aim_for_food(game_state, player_head, moves):
    # Get the coordinates for each food
    foods = game_state['board']['food']

    # Remove the food if it's in a hazard
    for food in foods:
        if food in game_state['board']['hazards']:
            foods.remove(food)

    # Find the closest food
    closest_food = None
    closest_food_distance = 9999  # Start with an impossibly large number
    for piece_of_food in foods:
        distance = abs(player_head['x'] - piece_of_food['x']) + \
            abs(player_head['y'] - piece_of_food['y'])
        if distance < closest_food_distance:
            closest_food = piece_of_food
            closest_food_distance = distance

    # Add desire to move towards food
    if closest_food is not None:
        # check if move exists and is towards food
        if 'right' in moves and player_head['x'] < closest_food['x']:
            moves['right'] = (moves['right'][0], moves['right'][1] + FOOD_DESIRE)
        if 'left' in moves and player_head['x'] > closest_food['x']:
            moves['left'] = (moves['left'][0], moves['left'][1] + FOOD_DESIRE)
        if 'up' in moves and player_head['y'] < closest_food['y']:
            moves['up'] = (moves['up'][0], moves['up'][1] + FOOD_DESIRE)
        if 'down' in moves and player_head['y'] > closest_food['y']:
            moves['down'] = (moves['down'][0], moves['down'][1] + FOOD_DESIRE)

    # No need to clean move list since no danger is added
    # Return the move list
    return moves


def aim_for_middle(game_state, player_head, moves):
    # find middle
    middle = (game_state['board']['width'] // 2,
              game_state['board']['height'] // 2)

    # Add desire to move towards middle
    if middle is not None:
        # check if move exists and is towards middle
        if 'right' in moves and player_head['x'] < middle[0]:
            moves['right'] = (moves['right'][0], moves['right'][1] + MIDDLE_DESIRE)
        if 'left' in moves and player_head['x'] > middle[0]:
            moves['left'] = (moves['left'][0], moves['left'][1] + MIDDLE_DESIRE)
        if 'up' in moves and player_head['y'] < middle[1]:
            moves['up'] = (moves['up'][0], moves['up'][1] + MIDDLE_DESIRE)
        if 'down' in moves and player_head['y'] > middle[1]:
            moves['down'] = (moves['down'][0], moves['down'][1] + MIDDLE_DESIRE)

    # No need to clean move list since no danger is added
    # Return the move list
    return moves


def chase_tail(game_state, player_head, moves):
    # find tail
    tail = game_state['you']['body'][-1]

    # Add desire to move towards tail
    # Desire +1
    # check if move exists and is towards tail
    if 'right' in moves and player_head['x'] < tail['x']:
        moves['right'] = (moves['right'][0], moves['right'][1] + TAIL_DESIRE)
    if 'left' in moves and player_head['x'] > tail['x']:
        moves['left'] = (moves['left'][0], moves['left'][1] + TAIL_DESIRE)
    if 'up' in moves and player_head['y'] < tail['y']:
        moves['up'] = (moves['up'][0], moves['up'][1] + TAIL_DESIRE)
    if 'down' in moves and player_head['y'] > tail['y']:
        moves['down'] = (moves['down'][0], moves['down'][1] + TAIL_DESIRE)
        
    # No need to clean move list since no danger is added
    # Return the move list
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
    moves = {"right": (0, 0), "left": (0, 0), "up": (0, 0), "down": (0, 0)}

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

    # Avoid hazards
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
