import random
import typing
from colorama import Fore, Back

# info is called when you create your Battlesnake on play.battlesnake.com
def info() -> typing.Dict:
    print("INFO")

    return {
        "apiversion": "1",
        "author": "Davis Stanko",
        "color": "#ff0000",
        "head": "dragon",
        "tail": "dragon",
    }


# start is called when your Battlesnake begins a game
def start(game_state: typing.Dict):
    print(Fore.GREEN + "GAME START")


# end is called when your Battlesnake finishes a game
def end(game_state: typing.Dict):
    # print win or lose
    if game_state["you"]["health"] > 0:
        print(Fore.GREEN + "WIN")
    else:
        print(Fore.RED + "LOSS")

# move is called on every turn and returns your next move
# Valid moves are "up", "down", "left", or "right"
# See https://docs.battlesnake.com/api/example-move for available data
def move(game_state: typing.Dict) -> typing.Dict:
    # list of valid moves
    is_move_safe = {
        "up": True,
        "down": True,
        "left": True,
        "right": True
    }

    # define the head of the snake
    my_head = game_state["you"]["body"][0]  # Coordinates of your head

    # don't move out of bounds
    board_width = game_state['board']['width']
    board_height = game_state['board']['height']

    if my_head['x'] == 0:
        is_move_safe['left'] = False
        print("Border is left of head, don't move left")
    if my_head['x'] == board_width - 1:
        is_move_safe['right'] = False
        print("Border is right of head, don't move right")
    if my_head['y'] == 0:
        is_move_safe['down'] = False
        print("Border is below head, don't move down")
    if my_head['y'] == board_height - 1:
        is_move_safe['up'] = False
        print("Border is above head, don't move up")

    # Prevent the Battlesnake from colliding with other Battlesnakes including itself
    snakes = game_state['board']['snakes']
    for Snake in snakes:
        for body_part in Snake['body']:
            # Check if body part is to the left of head
            if body_part['x'] == my_head['x'] - 1 and body_part['y'] == my_head['y']:
                is_move_safe['left'] = False
                print("Snake is left of head, don't move left")
            # Check if body part is to the right of head
            if body_part['x'] == my_head['x'] + 1 and body_part['y'] == my_head['y']:
                is_move_safe['right'] = False
                print("Snake is right of head, don't move right")
            # Check if body part is below head
            if body_part['y'] == my_head['y'] - 1 and body_part['x'] == my_head['x']:
                is_move_safe['down'] = False
                print("Snake is below head, don't move down")
            # Check if body part is above head
            if body_part['y'] == my_head['y'] + 1 and body_part['x'] == my_head['x']:
                is_move_safe['up'] = False
                print("Snake is above head, don't move up")

    # Are there any safe moves left?
    safe_moves = []
    for move, isSafe in is_move_safe.items():
        if isSafe:
            safe_moves.append(move)

    # If no safe moves are left
    if len(safe_moves) == 0:
        print(f"{Fore.RED}MOVE {game_state['turn']} No safe moves left, moving down")
        return {"move": "down"}

    # If only one option is left
    if len(safe_moves) == 1:
        print(f"{Fore.BLUE}MOVE {game_state['turn']} Only one safe move left, moving {safe_moves[0]}")
        return {"move": safe_moves[0]}

  # ===================================================
    # Check for possible head on collisions
    for i in safe_moves:
        nextMoves = []

        # Get the coordinates for each safe move
        if i == "left":
            nextMoves.append((my_head['x']-1, my_head['y']))
        if i == "right":
            nextMoves.append((my_head['x']+1, my_head['y']))
        if i == "up":
            nextMoves.append((my_head['x'], my_head['y']+1))
        if i == "down":
            nextMoves.append((my_head['x'], my_head['y']-1))

        # Get the coordinates for each safe move's adjacent tile
        adjacentSquares = []
        for x in nextMoves:
            adjacentSquares.append((x[0]-1, x[1]))
            adjacentSquares.append((x[0]+1, x[1]))
            adjacentSquares.append((x[0], x[1]-1))
            adjacentSquares.append((x[0], x[1]+1))

        opponents = game_state['board']['snakes']
        # Remove myself from the list of opponents
        for x in opponents:
            if x['id'] == game_state["you"]["id"]:
                opponents.remove(x)
                break

        # Check if any of the adjacent squares are occupied by an opponent
        temp_is_move_safe = is_move_safe.copy()
        exit = False
        for x in adjacentSquares:
            for oppponent in opponents:
                opponentHead = (oppponent["head"]['x'], oppponent["head"]['y'])
                if opponentHead == x and len(oppponent["body"]) >= len(game_state["you"]["body"]):  # If the opponent is bigger than me
                    print(Fore.YELLOW + "NOT SAFE")
                    temp_is_move_safe[i] = False # Mark the move as potentially unsafe
                    exit = True
                    break
                if opponentHead == x and len(oppponent["body"]) < len(game_state["you"]["body"]):  # If the opponent is smaller than me
                    print(Fore.YELLOW + "attempt to kill")
                    return {"move": i}  # Try to kill the opponent
            if exit == True:
                break

        # if all moves could result in a deadly head on collision, do nothing.
        if temp_is_move_safe['up'] == False and temp_is_move_safe['down'] == False and temp_is_move_safe['left'] == False and temp_is_move_safe['right'] == False:
            print(Fore.YELLOW + "All safe moves are potential deadly head on collisions")
            
        # get all moves that are not potential deadly head on collisions
        else:
            is_move_safe = temp_is_move_safe.copy()

            # Are there any safe moves left?
            safe_moves = []
            for move, isSafe in is_move_safe.items():
                if isSafe:
                    safe_moves.append(move)

            # If only one option is left
            if len(safe_moves) == 1:
                print(f"{Fore.YELLOW}MOVE {game_state['turn']} Only one safe move left, moving {safe_moves[0]}")
                return {"move": safe_moves[0]}

    # If multiple safe moves are left, go in the direction of the food, to regain health and survive longer
    foods = game_state['board']['food']

    # Find the closest food
    closest_food = None
    closest_food_distance = 9999  # Start with an impossibly large number
    for piece_of_food in foods:
        distance = abs(my_head['x'] - piece_of_food['x']) + abs(my_head['y'] - piece_of_food['y'])
        if distance < closest_food_distance:
            closest_food = piece_of_food
            closest_food_distance = distance

    # Move towards the closest food if it's safe
    if closest_food is not None:
        if my_head['x'] < closest_food['x'] and is_move_safe['right']:
            next_move = 'right'
        elif my_head['x'] > closest_food['x'] and is_move_safe['left']:
            next_move = 'left'
        elif my_head['y'] < closest_food['y'] and is_move_safe['up']:
            next_move = 'up'
        elif my_head['y'] > closest_food['y'] and is_move_safe['down']:
            next_move = 'down'
        # 
        else:
            print(Fore.RED + "Error: No safe moves detected after food check")
    # If no food is left, move randomly
    else:
        print(Fore.RED + "No food left, moving randomly")
        try:
            next_move = random.choice(safe_moves)
        except:
            # die
            next_move = 'down'
            print(Fore.RED + "Error: No safe moves detected. Moving down.")
        print("NO FOOD")

    print(f"{Fore.BLUE}MOVE {game_state['turn']}: {next_move}")
    return {"move": next_move}
