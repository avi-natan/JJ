from itertools import combinations

import helper


def all_goals_reached(pointers, executions):
    for a in range(len(pointers)):
        if pointers[a] < len(executions[a]) - 1:
            return False
    return True


def extract_certain_faults(plans, execution):
    fault_list = []

    # create annotated execution
    annotated_execution = [[[exe[0], 0]] for exe in execution]
    ptrs = [0 for _ in plans]
    for a in range(len(execution)):
        for t in range(1, len(execution[a])):
            while plans[a][ptrs[a]] != execution[a][t]:
                ptrs[a] += 1
            annotated_execution[a].append([execution[a][t], ptrs[a]])

    # create faults table
    fault_tab = [['ok' for _ in range(len(row)-1)] for row in annotated_execution]
    ptrs = [0 for _ in plans]
    for a in range(len(annotated_execution)):
        for t in range(len(annotated_execution[a])-1):
            if annotated_execution[a][t+1][0] == plans[a][ptrs[a]+1]:
                ptrs[a] += 1
            elif annotated_execution[a][t+1][0] == plans[a][ptrs[a]]:
                fault_tab[a][t] = 'del'
                exes = [exe for exe in range(len(annotated_execution)) if exe != a]
                for aa in exes:
                    if len(annotated_execution[aa]) > t+1:
                        positions = plans[aa][annotated_execution[aa][t][1]:annotated_execution[aa][t+1][1]+1]
                    elif len(annotated_execution[aa]) == t+1:
                        positions = plans[aa][annotated_execution[aa][t][1]]
                    else:
                        continue
                    if plans[a][ptrs[a]+1] in positions:
                        fault_tab[a][t] = 'col'
                        break
            else:
                next_ptr = ptrs[a] + 1
                while plans[a][next_ptr] != annotated_execution[a][t+1][0]:
                    next_ptr += 1
                fault_tab[a][t] = ['fst', next_ptr - 1 - ptrs[a]]
                ptrs[a] = next_ptr

    # use the faults table to extract the faults
    for a in range(len(fault_tab)):
        t = 0
        while t < len(fault_tab[a]):
            if type(fault_tab[a][t]) is str and fault_tab[a][t] == 'del':
                t1 = t + 1
                while type(fault_tab[a][t1]) is str and fault_tab[a][t1] == 'del':
                    t1 += 1
                l = t1 - t
                fault_list.append([a, t, -l])
                t = t1
            elif type(fault_tab[a][t]) is list:
                fault_list.append(([a, t, fault_tab[a][t][1]]))
                t += 1
            else:
                t += 1

    return fault_list


def diagnose(plans, execution, threshold):
    # logging
    print(f'######################## diagnosing ########################')
    print(f'plans:')
    helper.print_matrix(plans)
    print(f'execution')
    helper.print_matrix(execution)

    # extract goal delays per agent
    goal_delays = {}
    for a in range(len(plans)):
        goal_delays[f'{a}'] = max(0, len(execution[a]) - (len(plans[a]) + threshold))

    # extract certain faults. certain faults are faults that certainly happened
    # during the execution. these are either speedups of an agent, or delays
    # that cannot be explained as result of collision between two agents
    W = extract_certain_faults(plans, execution)
    # get a list of the subsets of the list
    subsets_W = []
    for i in range(0, len(W) + 1):
        combs = list(combinations(W, i))
        for comb in combs:
            lst = []
            for elem in comb:
                lst.append(elem)
            subsets_W.append(lst)
    print(9)


