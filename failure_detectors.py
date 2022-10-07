import copy

import helper


def reduction_positions_to_graph(poss_ptrs_curr, poss_ptrs_next):
    # make graph as such:
    # 1. each current position is directly connected to its next position (null and existing).
    # 2. each existing next position is connected to itself in the previous positions list.
    # 3. each null next position is connected to all the curr positions that have existing next positions.
    adjacency_list = {}
    for a in range(len(poss_ptrs_curr)):
        adjacency_list[f'{poss_ptrs_curr[a]}-c'] = [f'{poss_ptrs_next[a]}-n']
    for a in range(len(poss_ptrs_next)):
        adjacency_list[f'{poss_ptrs_next[a]}-n'] = []
        if poss_ptrs_next[a][1:] != [[-1,-1],-1]:
            for a2 in range(len(poss_ptrs_curr)):
                if poss_ptrs_curr[a2][1] == poss_ptrs_next[a][1]:
                    adjacency_list[f'{poss_ptrs_next[a]}-n'].append(f'{poss_ptrs_curr[a2]}-c')
        else:
            for a2 in range(len(poss_ptrs_curr)):
                if poss_ptrs_next[a2][1:] != [[-1,-1],-1]:
                    adjacency_list[f'{poss_ptrs_next[a]}-n'].append(f'{poss_ptrs_curr[a2]}-c')
    return adjacency_list


def detector_stuck(annotated_plan, annotated_observation, poss_ptrs_prev, poss_ptrs_curr, poss_ptrs_next):
    # print(f'poss_ptrs_prev: {poss_ptrs_prev}')
    # print(f'poss_ptrs_curr: {poss_ptrs_curr}')
    # print(f'poss_ptrs_next: {poss_ptrs_next}')
    # if the current pointers are different from the previous return false - i.e., there is a chance to advance
    if poss_ptrs_prev != poss_ptrs_curr:
        return False
    # go over the agents and check if the reason is some agent that
    # its finish position is in the path of another agent
    for a in range(len(annotated_plan)):
        # an agent that its current pointer is less than the plan length
        # didnt finish its run. we inspect these agents
        if poss_ptrs_curr[a][2] < len(annotated_plan[a]) - 1:
            # get the next position of that agent according to plan
            next_position = [annotated_plan[a][poss_ptrs_curr[a][2]+1][1][0], annotated_plan[a][poss_ptrs_curr[a][2]+1][1][1]]
            # print(f'{a}: next_position: {next_position}')
            # go over the other agents and check whether for one of them the next position
            # of the current agent is its final position, and it already arrived there
            for a2 in range(len(annotated_plan)):
                if a2 != a and annotated_plan[a2][-1][1] == next_position and poss_ptrs_curr[a2][2] == annotated_plan[a2][-1][0]:
                    print(f'stuck')
                    return True
    # if this is not the reason, check if there is a stucking
    # cycle over a group of agents
    # make graph as such:
    # 1. each current position is directly connected to its next position (null and existing).
    # 2. each existing next position is connected to itself in the previous positions list.
    # 3. each null next position is connected to all the curr positions that have existing next positions.
    graph = reduction_positions_to_graph(poss_ptrs_curr, poss_ptrs_next)
    # dfs over the graph to find cycles
    found_cycles = helper.search_cycles(graph)
    if found_cycles:
        print('cycle')
        return True
    return False

def make_detector(failure_detector):
    if failure_detector[:9] == 'fd_max_of':
        # todo implement
        print('fd_max_offset')
        print(f'threshold: {failure_detector[14:]}')
        return detector_stuck
    elif failure_detector[:9] == 'fd_sum_of':
        # todo implement
        print('fd_sum_offset')
        print(f'threshold: {failure_detector[14:]}')
        return detector_stuck
    elif failure_detector[:9] == 'fd_max_at':
        # todo implement
        print('fd_max_at_location')
        print(f'threshold: {failure_detector[19:]}')
        return detector_stuck
    elif failure_detector[:9] == 'fd_sum_at':
        # todo implement
        print('fd_sum_at_location')
        print(f'threshold: {failure_detector[19:]}')
        return detector_stuck
    else:   # failure_detector == 'fd_stuck':
        return detector_stuck
