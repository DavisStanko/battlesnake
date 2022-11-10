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
    # get gamewmode
    game_mode = game_state["game"]["ruleset"]["name"]
    print("Game Mode: " + game_mode)
    # print game id to watch game later
    print(game_state["game"]["id"] + Fore.RESET)


# end is called when your Battlesnake finishes a game
def end(game_state: typing.Dict):
    print(Fore.GREEN + "GAME END" + Fore.RESET)


# move is called on every turn
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

    # get board dimensions
    board_width = game_state['board']['width']
    board_height = game_state['board']['height']

    ############################
    # don't move out of bounds
    if my_head['x'] == 0:
        is_move_safe['left'] = False
        print("Border left")
    if my_head['x'] == board_width - 1:
        is_move_safe['right'] = False
        print("Border right")
    if my_head['y'] == 0:
        is_move_safe['down'] = False
        print("Border below ")
    if my_head['y'] == board_height - 1:
        is_move_safe['up'] = False
        print("Border above ")

    ############################
    # ignore the tail of the snakes if they can't eat food
    # we can tell that a snake just ate if it's tail is doubled up
    snakes = game_state['board']['snakes']
    for Snake in snakes:
        # check if [-1] == [-2]
        if Snake['body'][-1] != Snake['body'][-2]:  # if the tail is not doubled up
            # set the tail coordinates to (-1, -1) so they don't affect our calculations but are still in the list for length calculations
            Snake['body'][-1] = {'x': -1, 'y': -1}

    ############################
    # Prevent the Battlesnake from colliding with other Battlesnakes including itself
    for Snake in snakes:
        for body_part in Snake['body']:
            # Check if body part is to the left of head
            if body_part['x'] == my_head['x'] - 1 and body_part['y'] == my_head['y']:
                is_move_safe['left'] = False
                print("Snake left")
            # Check if body part is to the right of head
            if body_part['x'] == my_head['x'] + 1 and body_part['y'] == my_head['y']:
                is_move_safe['right'] = False
                print("Snake right")
            # Check if body part is below head
            if body_part['y'] == my_head['y'] - 1 and body_part['x'] == my_head['x']:
                is_move_safe['down'] = False
                print("Snake below")
            # Check if body part is above head
            if body_part['y'] == my_head['y'] + 1 and body_part['x'] == my_head['x']:
                is_move_safe['up'] = False
                print("Snake above")

    # Are there any safe moves left?
    safe_moves = []
    for move, isSafe in is_move_safe.items():
        if isSafe:
            safe_moves.append(move)

    # If no safe moves are left
    if len(safe_moves) == 0:
        next_move = 'down'
        print(f"{Fore.BLUE}TURN {game_state['turn']} Going {next_move}{Fore.RESET} {Back.RED}(No safe moves left){Back.RESET}")
        return {"move": next_move, "shout": "I'm gonna die!"}

    # If only one option is left
    if len(safe_moves) == 1:
        next_move = safe_moves[0]
        print(f"{Fore.BLUE}TURN {game_state['turn']} Going {next_move} (Forced){Fore.RESET}")
        return {"move": next_move}

    ############################
    # Head on collision avoidance
    # Check future moves
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
        future_moves = []
        for x in nextMoves:
            future_moves.append((x[0]-1, x[1]))
            future_moves.append((x[0]+1, x[1]))
            future_moves.append((x[0], x[1]-1))
            future_moves.append((x[0], x[1]+1))

        # Get list of all snake bodies
        opponents = game_state['board']['snakes']
        # Remove myself from the list of opponents
        for x in opponents:
            if x['id'] == game_state["you"]["id"]:
                opponents.remove(x)
                break

        # Check if any of the adjacent squares are occupied by an opponent to predict head on collisions
        temp_is_move_safe = is_move_safe.copy()
        exit = False
        for x in future_moves:
            for oppponent in opponents:
                opponentHead = (oppponent["head"]['x'], oppponent["head"]['y'])
                if opponentHead == x and len(oppponent["body"]) >= len(game_state["you"]["body"]):  # If the opponent is bigger than me
                    print(f"{Fore.YELLOW}Possible head on collision with {oppponent['id']}{Fore.RESET}")
                    temp_is_move_safe[i] = False  # Mark the move as potentially unsafe
                    exit = True
                    break
                elif opponentHead == x and len(oppponent["body"]) < len(game_state["you"]["body"]):  # If the opponent is smaller than me
                    next_move = i
                    print(f"{Fore.BLUE}TURN {game_state['turn']} Going {next_move} (Attempt to kill {oppponent['id']}){Fore.RESET}")
                    print(f"Opponent length = {len(oppponent['body'])} | My length = {len(game_state['you']['body'])}")
                    return {"move": next_move}  # Try to kill the opponent
            if exit == True:
                break

        # if all moves could result in a deadly head on collision, do nothing.
        if temp_is_move_safe['up'] == False and temp_is_move_safe['down'] == False and temp_is_move_safe['left'] == False and temp_is_move_safe['right'] == False:
            print(f"{Fore.YELLOW}All safe moves are potential deadly head on collisions{Fore.RESET}")

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
                next_move = safe_moves[0]
                print(f"{Fore.BLUE}TURN {game_state['turn']} Going {next_move} (Forced){Fore.RESET}")
                return {"move": next_move}

    ############################
    # check if there are hazards on the board
    temp_is_move_safe = is_move_safe.copy()

    # if there are hazards
    if len(game_state['board']['hazards']) > 0:
        # avoid hazard sauce if possible
        for i in game_state['board']['hazards']:
            if i['x'] == my_head['x'] - 1 and i['y'] == my_head['y']:
                temp_is_move_safe['left'] = False
                print("Hazard left")
            if i['x'] == my_head['x'] + 1 and i['y'] == my_head['y']:
                temp_is_move_safe['right'] = False
                print("Hazard right")
            if i['y'] == my_head['y'] - 1 and i['x'] == my_head['x']:
                temp_is_move_safe['down'] = False
                print("Hazard below")
            if i['y'] == my_head['y'] + 1 and i['x'] == my_head['x']:
                temp_is_move_safe['up'] = False
                print("Hazard above")

            # if all moves enter a hazard, do nothing.
            if temp_is_move_safe['up'] == False and temp_is_move_safe['down'] == False and temp_is_move_safe['left'] == False and temp_is_move_safe['right'] == False:
                print(f"{Fore.YELLOW}All safe moves are potential deadly head on collisions{Fore.RESET}")

            # get all moves that aren't onto hazards
            else:
                is_move_safe = temp_is_move_safe.copy()

                safe_moves = []
                for move, isSafe in is_move_safe.items():
                    if isSafe:
                        safe_moves.append(move)

                # If only one option is left, go there
                if len(safe_moves) == 1:
                    next_move = safe_moves[0]
                    print(f"{Fore.BLUE}TURN {game_state['turn']} Going {next_move} (Forced){Fore.RESET}")
                    return {"move": next_move}

    ############################
    # Calculate the distance to the closest food
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
        distance = abs(my_head['x'] - piece_of_food['x']) + abs(my_head['y'] - piece_of_food['y'])
        if distance < closest_food_distance:
            closest_food = piece_of_food
            closest_food_distance = distance

    # Move towards the closest food if it's safe
    if closest_food is not None:
        if my_head['x'] < closest_food['x'] and is_move_safe['right']:
            next_move = 'right'
            print(f"{Fore.BLUE}TURN {game_state['turn']} Going {next_move} (Moving towards food){Fore.RESET}")
            return {"move": next_move}
        elif my_head['x'] > closest_food['x'] and is_move_safe['left']:
            next_move = 'left'
            print(f"{Fore.BLUE}TURN {game_state['turn']} Going {next_move} (Moving towards food){Fore.RESET}")
            return {"move": next_move}
        elif my_head['y'] < closest_food['y'] and is_move_safe['up']:
            next_move = 'up'
            print(f"{Fore.BLUE}TURN {game_state['turn']} Going {next_move} (Moving towards food){Fore.RESET}")
            return {"move": next_move}
        elif my_head['y'] > closest_food['y'] and is_move_safe['down']:
            next_move = 'down'
            print(f"{Fore.BLUE}TURN {game_state['turn']} Going {next_move} (Moving towards food){Fore.RESET}")
            return {"move": next_move}

        # If no safe moves go to the closest food then move randomly
        else:
            print(f"{Fore.YELLOW}No safe moves towards food{Fore.RESET}")
            # random safe move
            try:
                next_move = random.choice(safe_moves)
                print(f"{Fore.BLUE}TURN {game_state['turn']} Going {next_move} (Random safe move){Fore.RESET}")
                return {"move": next_move}
            # no safe moves left
            except:
                # die
                next_move = 'down'
                print(f"{Fore.BLUE}TURN {game_state['turn']} Going {next_move}{Fore.RESET} {Back.RED}(No safe moves left){Back.RESET}")
                return {"move": next_move, "shout": "I'm gonna die!"}

    ############################
    # If no food is left, move randomly
    else:
        print(f"{Fore.YELLOW}No food left{Fore.RESET}")
        # random safe move
        try:
            next_move = random.choice(safe_moves)
            print(f"{Fore.BLUE}TURN {game_state['turn']} Going {next_move} (Random safe move){Fore.RESET}")
            return {"move": next_move}
        # no safe moves left
        except:
            next_move = 'down'
            print(f"{Fore.BLUE}TURN {game_state['turn']} Going {next_move}{Fore.RESET} {Back.RED}(No safe moves left){Back.RESET}")
            return {"move": next_move, "shout": "I'm gonna die!"}
