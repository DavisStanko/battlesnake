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


def clean_move_list(moves):
    # find the minimum danger level among all moves
    min_danger = min(moves.values(), key=lambda x: x[0])[0]

    # create a new dictionary containing only the moves with the minimum danger level
    updated_moves = {move: danger for move, danger in moves.items() if danger[0] == min_danger}

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
    # Ignore tails unless constrictor
    snakes_copy = snakes.copy()
    if not constrictor:
        for snake in snakes_copy:
            snake['body'].pop()

    # Prevent the Battlesnake from colliding with other Battlesnakes including itself
    for snake in snakes_copy:
        # if the snake is the player danger = 5 otherwise danger = 4
        danger = CERTAIN_DEATH if snake['id'] == game_state['you']['id'] else PROBABLE_DEATH
        for body_part in snake['body']:
            # Check if body part is to the left of head
            if body_part['x'] == player_head['x'] - 1 and body_part['y'] == player_head['y']:
                moves['left'] = (danger, moves['left'][1])
            # Check if body part is to the right of head
            elif body_part['x'] == player_head['x'] + 1 and body_part['y'] == player_head['y']:
                moves['right'] = (danger, moves['right'][1])
            # Check if body part is below head
            elif body_part['x'] == player_head['x'] and body_part['y'] == player_head['y'] - 1:
                moves['down'] = (danger, moves['down'][1])
            # Check if body part is above head
            elif body_part['x'] == player_head['x'] and body_part['y'] == player_head['y'] + 1:
                moves['up'] = (danger, moves['up'][1])

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
                    moves[direction] = (POSSIBLE_DEATH, moves[direction][1])
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
                # check if move in moves
                if 'left' in moves:
                    # Hazard damage is lethal
                    if hazard_damage >= player_health:
                        moves['left'] = (CERTAIN_DEATH, moves['left'][1])
                    # Hazard damage is not lethal
                    else:
                        moves['left'] = (HARM, moves['left'][1])
                
            if i['x'] == player_head['x'] + 1 and i['y'] == player_head['y']:
                # check if move in moves
                if 'right' in moves:
                    # Hazard damage is lethal
                    if hazard_damage >= player_health:
                        moves['right'] = (CERTAIN_DEATH, moves['right'][1])
                    # Hazard damage is not lethal
                    else:
                        moves['right'] = (HARM, moves['right'][1])
            if i['y'] == player_head['y'] - 1 and i['x'] == player_head['x']:
                # check if move in moves
                if 'down' in moves:
                    # Hazard damage is lethal
                    if hazard_damage >= player_health:
                        moves['down'] = (CERTAIN_DEATH, moves['down'][1])
                    # Hazard damage is not lethal
                    else:
                        moves['down'] = (HARM, moves['down'][1])
            if i['y'] == player_head['y'] + 1 and i['x'] == player_head['x']:
                # check if move in moves
                if 'up' in moves:
                    # Hazard damage is lethal
                    if hazard_damage >= player_health:
                        moves['up'] = (CERTAIN_DEATH, moves['up'][1])
                    # Hazard damage is not lethal
                    else:
                        moves['up'] = (HARM, moves['up'][1])

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


def pathfind_to_tail(start, target, obstacles, board_width, board_height):
    """
    Use BFS to find if there's a path from start to target avoiding obstacles.
    Returns True if path exists, False otherwise.
    """
    from collections import deque
    
    # Edge case: if start is the same as target
    if start == target:
        return True
    
    # Initialize BFS
    queue = deque([start])
    visited = set([start])
    
    # Directions: up, down, left, right
    directions = [(0, 1), (0, -1), (-1, 0), (1, 0)]
    
    while queue:
        current_x, current_y = queue.popleft()
        
        # Check all adjacent cells
        for dx, dy in directions:
            next_x, next_y = current_x + dx, current_y + dy
            next_pos = (next_x, next_y)
            
            # Check bounds
            if next_x < 0 or next_x >= board_width or next_y < 0 or next_y >= board_height:
                continue
            
            # Check if already visited
            if next_pos in visited:
                continue
                
            # Check if it's an obstacle
            if next_pos in obstacles:
                continue
            
            # Check if we reached the target
            if next_pos == target:
                return True
            
            # Add to queue and mark as visited
            queue.append(next_pos)
            visited.add(next_pos)
    
    return False


def chase_tail(game_state, player_head, moves):
    """
    Enhanced tail chasing logic that uses pathfinding to avoid dead ends.
    Marks moves as HARM if they would eliminate the path to the tail.
    """
    # Get current snake body
    snake_body = game_state['you']['body']
    board_width = game_state['board']['width']
    board_height = game_state['board']['height']
    
    # Calculate where the tail will be after the snake moves (tail advances one position)
    # The new tail position will be the second-to-last segment of the current body
    if len(snake_body) > 1:
        future_tail = (snake_body[-2]['x'], snake_body[-2]['y'])
    else:
        # If snake is length 1, tail stays at head position
        future_tail = (player_head['x'], player_head['y'])
    
    # Build obstacles set (all snake bodies except the current tail, plus other snakes)
    obstacles = set()
    
    # Add our own body (excluding the tail which will move)
    for i, segment in enumerate(snake_body[:-1]):  # Exclude tail
        obstacles.add((segment['x'], segment['y']))
    
    # Add other snakes' bodies
    for snake in game_state['board']['snakes']:
        if snake['id'] != game_state['you']['id']:
            for segment in snake['body']:
                obstacles.add((segment['x'], segment['y']))
    
    # Add hazards as obstacles
    for hazard in game_state['board']['hazards']:
        obstacles.add((hazard['x'], hazard['y']))
    
    # Check each possible move
    move_directions = {
        'up': (0, 1),
        'down': (0, -1),
        'left': (-1, 0),
        'right': (1, 0)
    }
    
    for direction, (dx, dy) in move_directions.items():
        if direction in moves:
            # Calculate new head position after this move
            new_head_x = player_head['x'] + dx
            new_head_y = player_head['y'] + dy
            new_head_pos = (new_head_x, new_head_y)
            
            # Create obstacles for this specific move (add current head position as obstacle)
            move_obstacles = obstacles.copy()
            move_obstacles.add((player_head['x'], player_head['y']))
            
            # Check if there's still a path from new head position to future tail
            has_path = pathfind_to_tail(new_head_pos, future_tail, move_obstacles, board_width, board_height)
            
            if not has_path:
                # No path to tail means potential dead end - mark as HARM
                moves[direction] = (HARM, moves[direction][1])
            else:
                # Path exists, add small tail desire bonus
                moves[direction] = (moves[direction][0], moves[direction][1] + TAIL_DESIRE)
    
    # Clean move list to ensure we don't trap ourselves
    moves = clean_move_list(moves)
    
    return moves