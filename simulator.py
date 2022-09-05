import random

import helper


def generate_speed_change_table(plans, F, fp, sv, svt):
    # initialize the speed change table to be empty
    spdchgtab = [[0 for _ in p] for p in plans]

    # go over the faulty agents, and randomly generate changes for their steps
    for a in F:
        for s in range(len(plans[a])):
            # do this only if a faulty agent executes a fault
            if random.uniform(0, 1) < fp:
                # decide the speed change
                speed_changes = list(range(sv+1))
                random.shuffle(speed_changes)
                speed_change = speed_changes[0]
                # depends on the speed change type, decide if its faster, slower, or random
                if svt == 'slower':
                    spdchgtab[a][s] = -speed_change
                elif svt == 'faster':
                    spdchgtab[a][s] = speed_change
                else:  # svt == 'both':
                    if random.uniform(0, 1) < 0.5:
                        spdchgtab[a][s] = -speed_change
                    else:
                        spdchgtab[a][s] = speed_change
    return spdchgtab

def all_goals_reached(pointers, plans):
    for a in range(len(pointers)):
        if pointers[a] < len(plans[a]) - 1:
            return False
    return True


def stuck(ptrs_curr, ptrs_prev, plans):
    if ptrs_curr != ptrs_prev:
        return False
    else:
        for a in range(len(plans)):
            if ptrs_curr[a] < len(plans[a]) - 1:
                wanted_position = [plans[a][ptrs_curr[a]+1][0], plans[a][ptrs_curr[a]+1][1]]
                for p in range(len(plans)):
                    if p != a and plans[p][-1] == wanted_position and ptrs_curr[p] == len(plans[p])-1:
                        return True
        return False


def simulate_instance(board_size, plan_length, agents_num, plans, faulty_agents_num, faulty_agents, fault_probability,
                      speed_variation, speed_variation_type, interruption_delay_time, repeat_number,
                      instance_number, total_instances_count):

    # logging
    print(f'######################## simulating instance {instance_number}/{total_instances_count} ########################')
    print(f'board_size: {board_size}')
    print(f'plan_length: {plan_length}')
    print(f'agents_num: {agents_num}')
    print(f'plans:')
    helper.print_matrix(plans)
    print(f'faulty_agents_num: {faulty_agents_num}')
    print(f'faulty_agents: {faulty_agents}')
    print(f'fault_probability: {fault_probability}')
    print(f'speed_variation: {speed_variation}')
    print(f'speed_variation_type: {speed_variation_type}')
    print(f'interruption_delay_time: {interruption_delay_time}')
    print(f'repeat_number: {repeat_number}')
    print(f'instance_number: {instance_number}')
    print(f'total_instances_count: {total_instances_count}')

    # initialize empty speed change table
    spdchgtab = [[] for _ in plans]

    # initialize empty timespace and set initial positions of agents
    timespace = [[[-1 for _ in range(board_size[1])] for _ in range(board_size[0])]]
    for a in range(len(plans)):
        timespace[0][plans[a][0][0]][plans[a][0][1]] = a

    # initialize timestep pointer and plan pointers for the agents
    ptrs_curr = [0 for _ in range(len(plans))]    # agents position pointers
    ptrs_prev = [-1 for _ in range(len(plans))]   # agents previous position pointers

    # initialize for every agent delay counters
    delays = [0 for _ in range(len(plans))]

    # initialize the execution with initial positions and the speed change table
    execution = [[] for _ in plans]
    for a, e in enumerate(execution):
        e.append([plans[a][0][0], plans[a][0][1]])

    # while at least one of the agents pointers does not point to the last planned position,
    # and while the system is not stuck
    while not all_goals_reached(ptrs_curr, plans) and not stuck(ptrs_curr, ptrs_prev, plans):
        # copy the values of the current agent plan pointers to the previous ones
        for a in range(len(ptrs_curr)):
            ptrs_prev[a] = ptrs_curr[a]

        # append a slice to timespace and copy the current positions of the agents there
        timespace.append([[-1 for _ in range(board_size[1])] for _ in range(board_size[0])])
        for a in range(len(plans)):
            timespace[-1][plans[a][ptrs_curr[a]][0]][plans[a][ptrs_curr[a]][1]] = a

        # prepare the list of agents yet to advance
        yet_to_advance = [a for a in range(len(plans))]

        # for every agent check if it already advanced to its last position. if yes, get it out of the
        # yet to advance list
        yta0 = []
        for a in yet_to_advance:
            if ptrs_curr[a] < len(plans[a])-1:
                yta0.append(a)

        # for every agent check if it has delays to be made.
        # if yes: decrease its delay by 1, get it out of yta, add 0 to its spdchgtab,
        #         and add its current position to the execution matrix
        # if no : leave it in yta
        yta1 = []
        for a in yta0:
            if delays[a] > 0:
                spdchgtab[a].append(delays[a] * -1j)
                delays[a] = delays[a] - 1
                execution[a].append([plans[a][ptrs_curr[a]][0], plans[a][ptrs_curr[a]][1]])
            else:
                yta1.append(a)

        # for every agent in yta, calculate speed change and add it to spdchgtab
        for a in yta1:
            if a in faulty_agents:
                if random.uniform(0, 1) < fault_probability:
                    # decide the speed change
                    spchgs = list(range(speed_variation+1))
                    random.shuffle(spchgs)
                    speed_change = spchgs[0]
                    # depends on the speed change type, decide if its faster, slower, or random
                    if speed_variation_type == 'slower':
                        spdchgtab[a].append(-speed_change)
                        delays[a] = speed_change - 1
                    elif speed_variation_type == 'faster':
                        spdchgtab[a].append(speed_change)
                    else:  # speed_variation_type == 'both':
                        if random.uniform(0, 1) < 0.5:
                            spdchgtab[a].append(-speed_change)
                            delays[a] = speed_change - 1
                        else:
                            spdchgtab[a].append(speed_change)
                else:
                    spdchgtab[a].append(0)
            else:
                spdchgtab[a].append(0)

        # sort the rest of the agents by their speed this round
        speeds = [spdchgtab[a][-1] for a in yta1]
        yta1_sorted = [y for _, y in sorted(zip(speeds, yta1), reverse=True)]

        # for the agents in yta, move them on the last created slide as much as possible from the
        # 1 step + additional for faster agents, as long as they dont collide, and append their
        # final positions to the execution table. if they collide, update their delays accordingly
        # to the interruption_delay_time variable.
        for a in yta1_sorted:
            new_plan_pointer = ptrs_curr[a]
            for p in range(ptrs_curr[a] + 1, ptrs_curr[a] + 1 + spdchgtab[a][-1] + 1):
                # if during this advance the agent already reached the final plan, break
                if p == len(plans[a]):
                    break
                # if the agent can advance, advance it
                if timespace[-1][plans[a][p][0]][plans[a][p][1]] == -1:
                    timespace[-1][plans[a][p][0]][plans[a][p][1]] = a
                    new_plan_pointer = p
                # else break out, the saved last pointer and its planned position will be appended and saved
                else:
                    break
            ptrs_curr[a] = new_plan_pointer
            execution[a].append([plans[a][ptrs_curr[a]][0], plans[a][ptrs_curr[a]][1]])

    print('current pointers:')
    print(ptrs_curr)
    print('previous pointers:')
    print(ptrs_prev)
    print('plans:')
    helper.print_matrix(plans)
    print('speed change table:')
    helper.print_matrix(spdchgtab)
    print('execution:')
    helper.print_matrix(execution)

    return execution, spdchgtab
