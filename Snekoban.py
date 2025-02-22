"""
6.1010 Lab 4:
Snekoban Game
"""

import json
import typing

# NO ADDITIONAL IMPORTS!


direction_vector = {
    "up": (-1, 0),
    "down": (+1, 0),
    "left": (0, -1),
    "right": (0, +1),
}


def make_new_game(level_description):
    """
    Given a description of a game state, create and return a game
    representation of your choice.

    The given description is a list of lists of lists of strs, representing the
    locations of the objects on the board (as described in the lab writeup).

    For example, a valid level_description is:

    [
        [[], ['wall'], ['computer']],
        [['target', 'player'], ['computer'], ['target']],
    ]

    The exact choice of representation is up to you; but note that what you
    return will be used as input to the other functions.
    """
    computer = set()
    player = set()
    wall = set()
    target = set()
    for row in range(len(level_description)):
        for col in range(len(level_description[0])):
            if  "computer" in level_description[row][col]:
                computer.add((row, col))
            if "player" in level_description[row][col]:
                player.add((row, col))
            if "wall" in level_description[row][col]:
                wall.add((row, col))
            if "target" in level_description[row][col]:
                target.add((row, col))
    return {
        "computer": computer,
        "player": player,
        "wall": wall,
        "target": target,
        "dimensions": (len(level_description), len(level_description[0])),
    }


def victory_check(game):
    """
    Given a game representation (of the form returned from make_new_game),
    return a Boolean: True if the given game satisfies the victory condition,
    and False otherwise.
    """
    if game["computer"] == set() or game["target"] == set():
        return False
    else:
        for i in game["target"]:
            if i not in game["computer"]:
                return False
        for i in game["computer"]:
            if i not in game["target"]:
                return False
    return True


def step_game(game, direction):
    """
    Given a game representation (of the form returned from make_new_game),
    return a new game representation (of that same form), representing the
    updated game after running one step of the game.  The user's input is given
    by direction, which is one of the following:
        {'up', 'down', 'left', 'right'}.

    This function should not mutate its input.
    """

    new_game = game.copy()
    new_game["computer"] = new_game["computer"].copy()
    new_game["player"] = new_game["player"].copy()
    for i in new_game["player"]:
        current = i
    new_pos = update_from_direction(direction, current)
    if new_pos in game["wall"]:
        return game
    elif new_pos in game["computer"]:
        comp_pos = update_from_direction(direction, new_pos)
        if comp_pos in game["wall"] or comp_pos in game["computer"]:
            return game
        new_game["computer"].add(comp_pos)
        new_game["computer"].discard(new_pos)
    new_game["player"].add(new_pos)
    new_game["player"].discard(current)
    return new_game


def update_from_direction(direction, current):
    new_pos = (current[0] + direction_vector[direction][0],
               current[1] + direction_vector[direction][1])
    return new_pos


def dump_game(game):
    """
    Given a game representation (of the form returned from make_new_game),
    convert it back into a level description that would be a suitable input to
    make_new_game (a list of lists of lists of strings).

    This function is used by the GUI and the tests to see what your game
    implementation has done, and it can also serve as a rudimentary way to
    print out the current state of your game for testing and debugging on your
    own.
    """

    new_list = []
    for row in range(game["dimensions"][0]):
        row_list = []
        for col in range(game["dimensions"][1]):
            col_list = []
            if (row, col) in game["wall"]:
                col_list.append("wall")
            if (row, col) in game["target"]:
                col_list.append("target")
            if (row, col) in game["computer"]:
                col_list.append("computer")
            if (row, col) in game["player"]:
                col_list.append("player")
            row_list.append(col_list)
        new_list.append(row_list)
    return new_list


def solve_puzzle(game):
    """
    Given a game representation (of the form returned from make_new_game), find
    a solution.

    Return a list of strings representing the shortest sequence of moves ("up",
    "down", "left", and "right") needed to reach the victory condition.

    If the given level cannot be solved, return None.
    """
    if victory_check(game):
        return []

    direction = ["up", "down", "left", "right"]
    agenda = [
        (game,),
    ]
    visited = set()
    while agenda:
        this_path = agenda.pop(0)
        current_state = this_path[-1]
        player_list = current_state["player"]
        computer_list = current_state["computer"]
        objects_to_move = (frozenset(player_list), frozenset(computer_list))
        if objects_to_move not in visited:
            for next in direction:
                next_state = step_game(current_state, next)

                if victory_check(next_state):
                    this_path = this_path + (next_state,)
                    return state_to_direction(this_path)

                agenda.append(this_path + (next_state,))
                visited.add(objects_to_move)
    return None


def state_to_direction(this_path):
    """
    takes in a list of states that represent the path to solving the game
    and returns the associated directions to get from state to state.
    """
    direction_list = []
    for state in range(len(this_path) - 1):
        for i in this_path[state]["player"]:
            player1 = i
        for i in this_path[state + 1]["player"]:
            player2 = i
        difference = (player2[0] - player1[0], player2[1] - player1[1])
        if difference == (1, 0):
            direction_list.append("down")
        elif difference == (-1, 0):
            direction_list.append("up")
        elif difference == (0, 1):
            direction_list.append("right")
        elif difference == (0, -1):
            direction_list.append("left")
    return direction_list


if __name__ == "__main__":
    # level_description = [
    #     [["wall"], ["wall"], ["wall"], ["wall"], ["wall"], ["wall"], ["wall"]],
    #     [["wall"], [], [], [], [], [], ["wall"]],
    #     [["wall"], [], [], [], [], [], ["wall"]],
    #     [["wall"], [], ["target"], ["computer"], ["player"], [], ["wall"]],
    #     [["wall"], [], ["target"], ["computer"], [], [], ["wall"]],
    #     [["wall"], [], [], [], [], [], ["wall"]],
    #     [["wall"], ["wall"], ["wall"], ["wall"], ["wall"], ["wall"], ["wall"]],
    # ]

    # # print(make_new_game(level_description))

    # game = {
    #     "computer": {(3, 3), (4, 3)},
    #     "player": {(3, 4)},
    #     "wall": {
    #         (4, 0),
    #         (4, 6),
    #         (0, 2),
    #         (0, 5),
    #         (1, 0),
    #         (1, 6),
    #         (6, 2),
    #         (6, 5),
    #         (3, 0),
    #         (5, 0),
    #         (5, 6),
    #         (3, 6),
    #         (0, 1),
    #         (0, 4),
    #         (6, 1),
    #         (6, 4),
    #         (0, 0),
    #         (0, 3),
    #         (2, 0),
    #         (0, 6),
    #         (2, 6),
    #         (6, 0),
    #         (6, 6),
    #         (6, 3),
    #     },
    #     "target": {(3, 2), (4, 2)},
    #     "dimensions": (7, 7),
    # }

    # # print(dump_game(game))

    # print(step_game(game, "left"))

    # # copy_of_dictionary(game)

    # solve_puzzle(game)

    pass
