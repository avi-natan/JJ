import copy
import random


def get_adjacent_positions(board_size, current_position):
    # initialize empty next positions
    adjacent_positions = []

    # generate next positions
    if current_position[0] > 0:
        adjacent_positions.append([current_position[0]-1, current_position[1]])
    if current_position[0] < board_size[0]-1:
        adjacent_positions.append([current_position[0]+1, current_position[1]])
    if current_position[1] > 0:
        adjacent_positions.append([current_position[0], current_position[1]-1])
    if current_position[1] < board_size[1]-1:
        adjacent_positions.append([current_position[0], current_position[1]+1])

    return adjacent_positions

def create_naiive_plan(board_size, plan_length, agents_number):
    # initialize the plan
    plan = [[] for _ in range(agents_number)]

    # create the first slice of the time expansion graph
    time_expansion_graph = [[[-1 for _x in range(board_size[1])] for _y in range(board_size[0])]]

    # randomly generate the start positions, and put them on the time expansion graph
    start_positions = []
    for a in range(agents_number):
        start_y = random.randrange(board_size[0])
        start_x = random.randrange(board_size[1])
        while [start_y, start_x] in start_positions:
            start_y = random.randrange(board_size[0])
            start_x = random.randrange(board_size[1])
        start_positions.append([start_y, start_x])
    for a, pos in enumerate(start_positions):
        time_expansion_graph[0][pos[0]][pos[1]] = a

    # initialize current and previous positions
    pos_curr = copy.deepcopy(start_positions)
    pos_prev = [[-1,-1] for _ in range(agents_number)]

    # set the current positions as the first positions in the plan
    for a in range(agents_number):
        plan[a].append([pos_curr[a][0], pos_curr[a][1]])

    # initialize wall clock
    wall_clock = 1

    # advance the wall clock and in each iteration advance the agents 1 step
    while wall_clock < plan_length:
        # advance wall clock
        wall_clock += 1

        # add the next slice of the time expansion graph, and fill it with the current agent positions
        time_expansion_graph.append([[-1 for _ in range(board_size[1])] for _ in range(board_size[0])])
        for a in range(agents_number):
            time_expansion_graph[-1][pos_curr[a][0]][pos_curr[a][1]] = a

        # go over the agents and advance each one to a random
        # adjacent cell that is not: 1. taken or 2. its previous cell
        for a in range(agents_number):
            # get the adjacent positions
            adjacent_positions = get_adjacent_positions(board_size, pos_curr[a])
            # shuffle the positions randomly
            random.shuffle(adjacent_positions)
            # while the agent didnt advance, and there are available positions to check
            api = 0
            advanced = False
            while not advanced and api < len(adjacent_positions):
                ap = adjacent_positions[api]
                if time_expansion_graph[-1][ap[0]][ap[1]] == -1 and ap != pos_prev[a]:
                    # mark this position in the time expansion graph
                    time_expansion_graph[-1][ap[0]][ap[1]] = a
                    # update the previous and current positions
                    pos_prev[a] = pos_curr[a]
                    pos_curr[a] = ap
                    # update the plan for the agent with the current position
                    plan[a].append([pos_curr[a][0], pos_curr[a][1]])
                    # mark that the agent advanced
                    advanced = True
                else:
                    # advance to the next adjacent position
                    api += 1
            # if the agent didnt advance, remake
            if not advanced:
                # returns empty plan and a remake boolean
                return [], True
    return plan, False
