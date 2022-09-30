import math
from itertools import combinations

import helper
import simulator


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


def create_faults_table(faults_list, num_agents):
    # calculate a maximum length for the table
    max_len = 0
    for elem in faults_list:
        max_len = max(max_len, elem[1])

    faults_tab = [[0 for _ in range(max_len+1)] for _ in range(num_agents)]

    for elem in faults_list:
        faults_tab[elem[0]][elem[1]] = elem[2]
    return faults_tab


def extract_goal_delays(execution, plans):
    goal_delays = {}
    for a in range(len(plans)):
        goal_delays[f'{a}'] = max(0, len(execution[a]) - len(plans[a]))
    return goal_delays


def subsets(List):
    subs = []
    for i in range(0, len(List) + 1):
        combs = list(combinations(List, i))
        for comb in combs:
            lst = []
            for elem in comb:
                lst.append(elem)
            subs.append(lst)
    return subs


def system_success(goal_delays_w, threshold):
    for gdk in goal_delays_w.keys():
        if goal_delays_w[gdk] > threshold:
            return False
    return True


def equivalent_sets(param, param1):
    for i in param:
        if i not in param1:
            return False
    for i in param1:
        if i not in param:
            return False
    return True


def costs_max_agent_delay(S):
    return max(S[1].values())


def shapley_for_system(E, W):
    """
    The shapley value function for a group of players N characteristic function v is represented as:

                      ____
    Phi_i(v) =  _1_   \     |S|!*(n-|S|-1)![v(S u {i}) - v(S)]
                 n!   /___
                  S subseteq N\{i}

    function parameters:
    i - the player of N for which we calculate the shapley value
    n - |N|

    :param E: containing the values of v
    :param W: contains the group N
    :return:
    """
    # W = [1, 2, 3]
    # E = subsets(W)
    # V = [
    #     [[], 0],
    #     [[1], 80],
    #     [[2], 56],
    #     [[3], 70],
    #     [[1, 2], 100],
    #     [[1, 3], 85],
    #     [[2, 3], 72],
    #     [[1, 2, 3], 90]
    # ]
    Phi = []
    for w in W:
        N_minus_i = [item for item in E if w not in item[0]]
        total_sum = 0
        for S in N_minus_i:
            len_S = len(S[0])
            v_S = costs_max_agent_delay(S)
            Sui = [item for item in E if equivalent_sets(S[0] + [w], item[0])][0]
            v_Sui = costs_max_agent_delay(Sui)
            sum_S = math.factorial(len_S) * math.factorial(len(W)-len_S-1) * (v_Sui - v_S)
            total_sum += sum_S
        Phi_w = total_sum / math.factorial(len(W))
        Phi.append([w, Phi_w])
    return Phi


def diagnose(plans, execution, board_size, threshold):
    # logging
    print(f'######################## diagnosing ########################')
    print(f'plans:')
    helper.print_matrix(plans)
    print(f'execution')
    helper.print_matrix(execution)

    # extract goal delays per agent
    goal_delays = extract_goal_delays(execution, plans)

    # extract certain faults. certain faults are faults that certainly happened
    # during the execution. these are either speedups of an agent, or delays
    # that cannot be explained as result of collision between two agents
    W = extract_certain_faults(plans, execution)
    # get a list of the subsets of the list
    subsets_W = subsets(W)

    # initialize executions list E
    E = []

    # initialize the empty diagnosis set D
    D = []

    # for each subset of W, that is not a superset of existing diagnoses,
    # simulate the plan without the faults in the subset. get the resulting executions
    # in an executions list, and the subsets for which the system fails, get the subset inside
    # the diagnosis list D
    for w in subsets_W:
        # if helper.superset_of_element(w, D):
        #     continue
        # create a faults table for W\w
        W_minus_w = helper.calculate_minus_set(W, w)
        faults_tab = create_faults_table(W_minus_w, len(plans))

        # simulate the plans with the faults table
        execution_w = simulator.simulate_faults_table(board_size, plans, faults_tab)
        print(9)

        # extract goal delays per agent
        goal_delays_w = extract_goal_delays(execution_w, plans)

        # insert the execution of W\w into the execution list E: [w, execution]
        E.append([w, goal_delays_w, execution_w])

        # insert into D this w if simulating W\w led to system success
        if system_success(goal_delays_w, threshold):
            D.append([w, goal_delays_w, execution_w])

    # calculate shapley value for the system - what is the contribution of each fault to the grand failure
    Phi_system = shapley_for_system(E, W)

    # for each w in D, calculate the shapley values of the individual faults
    Phi_diagnoses = []
    for d in D:
        W_d = d[0]
        E_d = [item for item in E if helper.is_subset(item[0], W_d)]
        Phi_d = shapley_for_system(E_d, W_d)
        Phi_diagnoses.append([W_d, Phi_d])
    print(9)
