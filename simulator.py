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

def simulate_instance(board_size, plan_length, agents_num, plans, faulty_agents_num, faulty_agents, fault_probabilities,
                      speed_variation, speed_variation_type, speed_change_table, conflict_delay_time, repeat_number,
                      instance_number, total_instances_count):

    # logging
    la = locals()
    print(f'######################## simulating instance {instance_number}/{total_instances_count} ########################')
    for k in la.keys():
        if type(la[k]) == list and type(la[k][0]) == list:
            print(f'{k}:')
            helper.print_matrix(la[k])
        else:
            print(f'{k}: {la[k]}')

    # initialize the execution
    execution = [[] for _ in plans]
    for i, e in enumerate(execution):
        e.append([plans[i][0][0], plans[i][0][1]])

    return execution
