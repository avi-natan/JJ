import copy
import random

import failure_detectors
import helper

def all_goals_reached(annotated_plan, annotated_observation):
    # extract the pointers of the current positions from the annotated observation
    ptrs_curr = [a_o[-1][2] for a_o in annotated_observation]
    # go over the agents
    for a in range(len(ptrs_curr)):
        # if there is one agent that its current pointer does not
        # point at its last planned position, then not all goals
        # are reached. return false in this case
        if ptrs_curr[a] < len(annotated_plan[a]) - 1:
            return False
    return True

def simulate_instance(board_size, plan, faulty_agents, fault_probability, fault_speed_range,
                      fault_type, failure_detector, repeat_number, instance_number, total_instances_count):

    # logging
    print(f'######################## simulating instance {instance_number}/{total_instances_count} ########################')
    print(f'board_size: {board_size}')
    print(f'plan:')
    helper.print_matrix(plan)
    print(f'faulty_agents: {faulty_agents}')
    print(f'fault_probability: {fault_probability}')
    print(f'fault_speed_range: {fault_speed_range}')
    print(f'fault_type: {fault_type}')
    print(f'failure_detector: {failure_detector}')
    print(f'repeat_number: {repeat_number}')
    print(f'instance_number: {instance_number}')
    print(f'total_instances_count: {total_instances_count}')

    # annotate the plans
    annotated_plan = [[[t, pa] for t, pa in enumerate(plan_a)] for plan_a in plan]

    # initialize the annotated observation with initial positions
    annotated_observation = [[[0,[annotated_plan[a][0][1][0], annotated_plan[a][0][1][1]],annotated_plan[a][0][0],0]]
                             for a in range(len(annotated_plan))]

    # initialize speed change table with the trivial zero first speed change
    spdchgtab = [[] for _ in annotated_plan]
    for a in range(len(annotated_plan)):
        spdchgtab[a].append(0)

    # create the first slice of the time expansion graph, and set the planned start positions
    time_expansion_graph = [[[-1 for _x in range(board_size[1])] for _y in range(board_size[0])]]
    for a, pos in enumerate(list(map(lambda pl: pl[0], annotated_plan))):
        time_expansion_graph[0][pos[1][0]][pos[1][1]] = a

    # initialize for every agent delay counters
    delay_counters = [0 for _ in range(len(annotated_plan))]

    # initialize the failure detector
    detector = failure_detectors.make_detector(failure_detector)

    # initialize wall clock to zero
    wall_clock = 0

    # save previous, current, and next positions and pointers for failure detection
    poss_ptrs_prev = [[a, annotated_observation[a][-2][1], annotated_observation[a][-2][2]] if len(annotated_observation[a]) > 1 else [a, [-1, -1], -1] for a in range(len(annotated_observation))]
    poss_ptrs_curr = [[a, annotated_observation[a][-1][1], annotated_observation[a][-1][2]] for a in range(len(annotated_observation))]
    poss_ptrs_next = [[a, annotated_plan[a][annotated_observation[a][-1][2] + 1][1], annotated_observation[a][-1][2] + 1] if annotated_observation[a][-1][2] + 1 < len(annotated_plan[a]) else [a, [-1, -1], -1] for a in range(len(annotated_observation))]

    # while the failure detector didnt detect failure and while there are agents that didnt finish their plans
    while not detector(annotated_plan, annotated_observation, poss_ptrs_prev, poss_ptrs_curr, poss_ptrs_next) \
            and not all_goals_reached(annotated_plan, annotated_observation):
        # advance the wall clock
        wall_clock += 1

        # append a slice to timespace and copy the current positions of the agents there
        time_expansion_graph.append([[-1 for _x in range(board_size[1])] for _y in range(board_size[0])])
        for a in range(len(annotated_plan)):
            time_expansion_graph[-1][annotated_observation[a][-1][1][0]][annotated_observation[a][-1][1][1]] = a

        # prepare the list of agents yet to advance
        yet_to_advance = [a for a in range(len(annotated_plan))]

        # for every agent check if it already advanced to its last position. if yes, get it out of the
        # yet to advance list
        yta0 = []
        for a in yet_to_advance:
            if annotated_observation[a][-1][2] < len(annotated_plan[a]) - 1:
                yta0.append(a)

        # for every agent check if it has delays to be made.
        # if yes: add delay * -1j to its spdchgtab, decrease the delay,
        #         add its current position to the annotated observations,
        #         and remove it from yta
        # if no : leave it in yta
        yta1 = []
        for a in yta0:
            if delay_counters[a] > 0:
                spdchgtab[a].append(delay_counters[a] * -1j)
                delay_counters[a] = delay_counters[a] - 1
                annotated_observation[a].append(
                    [wall_clock,
                     copy.deepcopy(annotated_observation[a][-1][1]),
                     annotated_observation[a][-1][2],
                     wall_clock - annotated_observation[a][-1][2]])
            else:
                yta1.append(a)

        # for every agent in yta, calculate speed change and add it to spdchgtab.
        # agents that just got out of a delay are excempt
        for a in yta1:
            if a in faulty_agents:
                if random.uniform(0, 1) < fault_probability:
                    # decide the speed change
                    temp = list(range(fault_speed_range + 1))
                    random.shuffle(temp)
                    speed_change = temp[0]
                    # depends on the speed change type, decide if its faster, slower, or random
                    if fault_type == 'slower':
                        if spdchgtab[a] != [] and spdchgtab[a][-1] not in [-1, -1j]:
                            spdchgtab[a].append(-speed_change)
                            delay_counters[a] = speed_change - 1
                        else:
                            spdchgtab[a].append(0)
                    elif fault_type == 'faster':
                        spdchgtab[a].append(speed_change)
                    else:  # speed_variation_type == 'both':
                        if random.uniform(0, 1) < 0.5:
                            if spdchgtab[a] != [] and spdchgtab[a][-1] not in [-1, -1j]:
                                spdchgtab[a].append(-speed_change)
                                delay_counters[a] = speed_change - 1
                            else:
                                spdchgtab[a].append(0)
                        else:
                            spdchgtab[a].append(speed_change)
                else:
                    spdchgtab[a].append(0)
            else:
                spdchgtab[a].append(0)

        # sort the rest of the agents by their speed this round, second level sort is by the agents id numbers
        speeds = [spdchgtab[a][-1] for a in yta1]
        yta1 = [y for _, y in sorted(zip(speeds, yta1), reverse=True)]

        # for the agents in yta, move them on the last created time slice as much as possible from the
        # 1 step + additional for faster agents, as long as they dont collide, and append their
        # final positions to the execution table.
        for a in yta1:
            new_plan_pointer = annotated_observation[a][-1][2]
            for p in range(annotated_observation[a][-1][2] + 1,
                           annotated_observation[a][-1][2] + 1 + spdchgtab[a][-1] + 1):
                # if during this advance the agent already reached the final plan, break
                if p == len(annotated_plan[a]):
                    break
                # if the agent can advance, advance it
                if time_expansion_graph[-1][annotated_plan[a][p][1][0]][annotated_plan[a][p][1][1]] == -1:
                    time_expansion_graph[-1][annotated_plan[a][p][1][0]][annotated_plan[a][p][1][1]] = a
                    new_plan_pointer = p
                # else break out, the saved last pointer and its planned position will be appended and saved
                else:
                    break
            annotated_observation[a].append(
                [wall_clock,
                 copy.deepcopy(annotated_plan[a][new_plan_pointer][1]),
                 new_plan_pointer,
                 wall_clock-new_plan_pointer])
        # print([annotated_observation[a][-1] for a in range(len(annotated_observation))])
        # print(77)
        # extract lists of previous, current and next timed positions for failure detection
        poss_ptrs_prev = copy.deepcopy(poss_ptrs_curr)
        poss_ptrs_curr = [[a, annotated_observation[a][-1][1], annotated_observation[a][-1][2]] for a in range(len(annotated_observation))]
        poss_ptrs_next = [[a, annotated_plan[a][annotated_observation[a][-1][2] + 1][1], annotated_observation[a][-1][2] + 1] if annotated_observation[a][-1][2] + 1 < len(annotated_plan[a]) else [a, [-1, -1], -1] for a in range(len(annotated_observation))]
    if not detector(annotated_plan, annotated_observation, poss_ptrs_prev, poss_ptrs_curr, poss_ptrs_next):
        return [], [], True
    return annotated_observation, spdchgtab, False


def calculate_counterfactual(board_size, plan, faults_tab_W_minus_E, failure_detector):
    # annotate the plans
    annotated_plan = [[[t, pa] for t, pa in enumerate(plan_a)] for plan_a in plan]

    # initialize the annotated observation with initial positions
    annotated_observation = [[] for _ in range(len(annotated_plan))]
    for a in range(len(annotated_plan)):
        annotated_observation[a].append([0, [annotated_plan[a][0][1][0], annotated_plan[a][0][1][1]], annotated_plan[a][0][0], 0])

    # initialize speed change table with the first speed change
    spdchgtab = [[] for _ in annotated_plan]
    for a in range(len(annotated_plan)):
        spdchgtab[a].append(faults_tab_W_minus_E[a][0])

    # create the first slice of the time expansion graph, and set the planned start positions
    time_expansion_graph = [[[-1 for _x in range(board_size[1])] for _y in range(board_size[0])]]
    for a, pos in enumerate(list(map(lambda pl: pl[0], annotated_plan))):
        time_expansion_graph[0][pos[1][0]][pos[1][1]] = a

    # initialize for every agent delay counters
    delay_counters = [0 for _ in range(len(annotated_plan))]

    # initialize the failure detector
    detector = failure_detectors.make_detector(failure_detector)

    # initialize wall clock to zero
    wall_clock = 1

    # save previous, current, and next positions and pointers for failure detection
    poss_ptrs_prev = [[a, annotated_observation[a][-2][1], annotated_observation[a][-2][2]] if len(
        annotated_observation[a]) > 1 else [a, [-1, -1], -1] for a in range(len(annotated_observation))]
    poss_ptrs_curr = [[a, annotated_observation[a][-1][1], annotated_observation[a][-1][2]] for a in
                      range(len(annotated_observation))]
    poss_ptrs_next = [
        [a, annotated_plan[a][annotated_observation[a][-1][2] + 1][1], annotated_observation[a][-1][2] + 1] if
        annotated_observation[a][-1][2] + 1 < len(annotated_plan[a]) else [a, [-1, -1], -1] for a in
        range(len(annotated_observation))]

    # while the failure detector didnt detect failure and while there are agents that didnt finish their plans
    while not detector(annotated_plan, annotated_observation, poss_ptrs_prev, poss_ptrs_curr, poss_ptrs_next) \
            and not all_goals_reached(annotated_plan, annotated_observation):

        # append a slice to timespace and copy the current positions of the agents there
        time_expansion_graph.append([[-1 for _x in range(board_size[1])] for _y in range(board_size[0])])
        for a in range(len(annotated_plan)):
            time_expansion_graph[-1][annotated_observation[a][-1][1][0]][annotated_observation[a][-1][1][1]] = a

        # prepare the list of agents yet to advance
        yet_to_advance = [a for a in range(len(annotated_plan))]

        # for every agent check if it already advanced to its last position. if yes, get it out of the
        # yet to advance list
        yta0 = []
        for a in yet_to_advance:
            if annotated_observation[a][-1][2] < len(annotated_plan[a]) - 1:
                yta0.append(a)

        # for every agent check if it has delays to be made.
        # if yes: add delay * -1j to its spdchgtab, decrease the delay,
        #         add its current position to the annotated observations,
        #         and remove it from yta
        # if no : leave it in yta
        yta1 = []
        for a in yta0:
            if delay_counters[a] > 0:
                spdchgtab[a].append(delay_counters[a] * -1j)
                delay_counters[a] = delay_counters[a] - 1
                annotated_observation[a].append(
                    [wall_clock,
                     copy.deepcopy(annotated_observation[a][-1][1]),
                     annotated_observation[a][-1][2],
                     wall_clock - annotated_observation[a][-1][2]])
            else:
                yta1.append(a)

        # for every agent in yta, add the speed change from the fault table to spdchgtab.
        # agents that just got out of a delay are excempt
        for a in yta1:
            if wall_clock < len(faults_tab_W_minus_E[a]):
                speed_change = faults_tab_W_minus_E[a][wall_clock]
                if speed_change < 0:
                    delay_counters[a] = -1*speed_change - 1
                spdchgtab[a].append(speed_change)
            else:
                spdchgtab[a].append(0)
        # advance the wall clock
        wall_clock += 1

        # sort the rest of the agents by their speed this round, second level sort is by the agents id numbers
        speeds = [spdchgtab[a][-1] for a in yta1]
        yta1 = [y for _, y in sorted(zip(speeds, yta1), reverse=True)]

        # for the agents in yta, move them on the last created time slice as much as possible from the
        # 1 step + additional for faster agents, as long as they dont collide, and append their
        # final positions to the execution table.
        for a in yta1:
            new_plan_pointer = annotated_observation[a][-1][2]
            for p in range(annotated_observation[a][-1][2] + 1,
                           annotated_observation[a][-1][2] + 1 + spdchgtab[a][-1] + 1):
                # if during this advance the agent already reached the final plan, break
                if p == len(annotated_plan[a]):
                    break
                # if the agent can advance, advance it
                if time_expansion_graph[-1][annotated_plan[a][p][1][0]][annotated_plan[a][p][1][1]] == -1:
                    time_expansion_graph[-1][annotated_plan[a][p][1][0]][annotated_plan[a][p][1][1]] = a
                    new_plan_pointer = p
                # else break out, the saved last pointer and its planned position will be appended and saved
                else:
                    break
            annotated_observation[a].append(
                [wall_clock,
                 copy.deepcopy(annotated_plan[a][new_plan_pointer][1]),
                 new_plan_pointer,
                 wall_clock - new_plan_pointer])
        # print([annotated_observation[a][-1] for a in range(len(annotated_observation))])
        # print(77)
        # extract lists of previous, current and next timed positions for failure detection
        poss_ptrs_prev = copy.deepcopy(poss_ptrs_curr)
        poss_ptrs_curr = [[a, annotated_observation[a][-1][1], annotated_observation[a][-1][2]] for a in
                          range(len(annotated_observation))]
        poss_ptrs_next = [
            [a, annotated_plan[a][annotated_observation[a][-1][2] + 1][1], annotated_observation[a][-1][2] + 1] if
            annotated_observation[a][-1][2] + 1 < len(annotated_plan[a]) else [a, [-1, -1], -1] for a in
            range(len(annotated_observation))]
    return annotated_observation
