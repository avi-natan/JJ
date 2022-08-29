import random

def generate_random_start_goal(height, width):
    start_y = random.randrange(height)
    start_x = random.randrange(width)
    goal_y = random.randrange(height)
    goal_x = random.randrange(width)
    return start_y, start_x, goal_y, goal_x


def get_next_positions(board_size, current_position):
    # initialize empty next positions
    next_positions = []

    # generate next positions
    if current_position[0] > 0:
        next_positions.append([current_position[0]-1, current_position[1]])
    if current_position[0] < board_size[0]-1:
        next_positions.append([current_position[0]+1, current_position[1]])
    if current_position[1] > 0:
        next_positions.append([current_position[0], current_position[1]-1])
    if current_position[1] < board_size[1]-1:
        next_positions.append([current_position[0], current_position[1]+1])

    return next_positions


def claculate_positions_distances(next_positions, goal):
    next_positions_with_distances = []

    for i in range(len(next_positions)):
        distance_i = abs(goal[0]-next_positions[i][0]) + abs(goal[1]-next_positions[i][1])
        next_positions_with_distances.append([[next_positions[i][0], next_positions[i][1]], distance_i])

    next_positions_with_distances = sorted(next_positions_with_distances, key=lambda x: x[1], reverse=False)

    return next_positions_with_distances


def advance_one_step(board_size, board_temporal_constraints, step, agent, goal, current_position):
    # initialize the next position as the current position, it will change
    next_position = [current_position[0], current_position[1]]

    # get the available next positions the agent can advance to from its current position
    next_positions = get_next_positions(board_size, current_position)
    
    # get the next positions ordered by their distances from the goal
    next_positions_with_distances = claculate_positions_distances(next_positions, goal)

    # make sure that the temporal board is not long enough, add some steps
    if step == len(board_temporal_constraints)-1:
        board_temporal_constraints.append([[-1 for _x in range(board_size[0])] for _y in range(board_size[1])])
    
    # choose the position with the smallest distance, that is not occupied, and that is not hot swapping
    for p in next_positions_with_distances:
        if (board_temporal_constraints[step][p[0][0]][p[0][1]] == -1 and board_temporal_constraints[step+1][p[0][0]][p[0][1]] == -1) or \
                (board_temporal_constraints[step][p[0][0]][p[0][1]] != -1 and board_temporal_constraints[step+1][p[0][0]][p[0][1]] == -1 and board_temporal_constraints[step][p[0][0]][p[0][1]] != board_temporal_constraints[step+1][current_position[0][0]][current_position[0][1]]):
            next_position[0] = p[0][0]
            next_position[1] = p[0][1]
            board_temporal_constraints[step + 1][p[0][0]][p[0][1]] = agent
            break

    return next_position


def plan_single(board_size, board_temporal_constraints, a, start, goal):
    # initialize empty plan
    plan = [[start[0], start[1]]]

    # initialize step counter
    s = 0

    # initialize the current position (y,x) as the start position
    current = [start[0], start[1]]

    # while the goal is not reached, continue advancing
    while board_temporal_constraints[s][goal[0]][goal[1]] != a:
        current = advance_one_step(board_size, board_temporal_constraints, s, a, goal, current)
        plan.append(current)
        s += 1

    return plan


def create_naiive_plans(board_size, plan_length, agents_number):
    # create temporal board slices - i.e., for every plan step create a board image
    board_temporal_constraints = [[[-1 for _y in range(board_size[0])] for _x in range(board_size[1])] for _pl in range(plan_length*2)]

    # initialize the plans
    plans = []

    # initialize start and goal positions for the agents
    pl_starts = []
    pl_goals = []
    for a in range(agents_number):
        start_y, start_x, goal_y, goal_x = generate_random_start_goal(board_size[0], board_size[1])
        while abs(goal_y-start_y)+abs(goal_x-start_x) < plan_length or \
                [start_y, start_x] in pl_starts or \
                [goal_y, goal_x] in pl_goals:
            start_y, start_x, goal_y, goal_x = generate_random_start_goal(board_size[0], board_size[1])
        pl_starts.append([start_y, start_x])
        pl_goals.append([goal_y, goal_x])

    # initialize the board start positions
    for a in range(agents_number):
        board_temporal_constraints[0][pl_starts[a][0]][pl_starts[a][1]] = a

    # use naiive plan - single algorithm to generate plans
    for a in range(agents_number):
        plan = plan_single(board_size, board_temporal_constraints, a, pl_starts[a], pl_goals[a])
        plans.append(plan)
    return plans
