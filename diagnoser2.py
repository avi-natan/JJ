import copy
import math
from datetime import datetime

import cost_functions
import helper
import simulator2


def create_faults_table(faults_list, num_agents):
    # calculate a maximum length for the table
    max_len = 0
    for elem in faults_list:
        max_len = max(max_len, elem[1])

    faults_tab = [[0 for _ in range(max_len+1)] for _ in range(num_agents)]

    for elem in faults_list:
        faults_tab[elem[0]][elem[1]] = elem[2]
    return faults_tab

def shapley(board_size, plan, failure_wall_clock_time, W, cost_function, seen, seen_cf):
    """
    The shapley value function for player w, a group of players W and characteristic function f is represented as:

                         ____
    Phi_w(f, W) =  _1_   \     |S|!*(n-1-|S|)![f(cf(S u {w})) - f(cf((S))]
                    n!   /___
                  S subseteq (W\{w})
    """
    # W = [1, 2, 3]
    # CFS = subsets(W)
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
    print(f'{W}')
    Phi = []
    n = len(W)
    cost_func = cost_functions.make_cost_function(cost_function)
    temp_w = 0
    for w in W:
        W_minus_w = [item for item in W if item != w]
        subsets_W_minus_w = helper.subsets(W_minus_w)
        total_sum = 0
        temp_S = 0
        for S in subsets_W_minus_w:
            # print(f'temp_w: {temp_w}/{n}, temp_S:{temp_S}/{len(subsets_W_minus_w)}')
            temp_S += 1
            # save the length of S
            len_S = len(S)

            # create a faults table for W\S
            W_minus_S = helper.calculate_minus_set(W, S)
            if W_minus_S in seen:
                cf_S = seen_cf[str(W_minus_S)]
            else:
                print(f'{W_minus_S}')
                faults_tab_W_minus_S = create_faults_table(W_minus_S, len(plan))
                cf_S = simulator2.calculate_counterfactual(board_size, plan, faults_tab_W_minus_S, failure_wall_clock_time)
                seen.append(W_minus_S)
                seen_cf[str(W_minus_S)] = cf_S
            f_cf_S = cost_func(cf_S)

            # create the set Suw
            Suw = S + [w]

            # create a faults table for W\(Suw)
            W_minus_Suw = helper.calculate_minus_set(W, Suw)
            if W_minus_Suw in seen:
                cf_Suw = seen_cf[str(W_minus_Suw)]
            else:
                print(f'{W_minus_Suw}')
                faults_tab_W_minus_Suw = create_faults_table(W_minus_Suw, len(plan))
                cf_Suw = simulator2.calculate_counterfactual(board_size, plan, faults_tab_W_minus_Suw, failure_wall_clock_time)
                seen.append(W_minus_Suw)
                seen_cf[str(W_minus_Suw)] = cf_Suw
            f_cf_Suw = cost_func(cf_Suw)

            # calculate the sum for S and add it to the total sum
            sum_S = math.factorial(len_S) * math.factorial(n-len_S-1) * (f_cf_Suw - f_cf_S)
            total_sum += sum_S
        Phi_w = total_sum / math.factorial(n)
        Phi.append([w, Phi_w])
        temp_w += 1
    return Phi

def extract_certain_faults(plan, observation):
    fault_list = []

    # create faults table and initialize the first trivial faults values to 'ok'
    fault_tab = [[] for _ in observation]
    for a in range(len(observation)):
        fault_tab[a].append('ok')
    # go over the observation and depends on each two
    # consecutive observed steps, populate the faults table
    for a in range(len(observation)):
        for t in range(len(observation[a])-1):
            # if the next observed position is the one
            # following the current one, do nothing
            if observation[a][t+1][2] == observation[a][t][2]+1:
                fault_tab[a].append('ok')
            # if the next observed position is the same
            # as the current observed position, do:
            elif observation[a][t+1][2] == observation[a][t][2]:
                # first of all set the value of
                # the fault table to delayed
                tmp = 'del'
                # then, check to see if the was actually a collision
                other_agents = [aa for aa in range(len(observation)) if aa != a]
                for aa in other_agents:
                    if len(observation[aa]) > t+1:
                        positions = plan[aa][observation[aa][t][2]:observation[aa][t+1][2]+1]
                    elif len(observation[aa]) == t+1:
                        positions = [plan[aa][observation[aa][t][2]]]
                    else:
                        continue
                    if plan[a][observation[a][t][2]+1] in positions:
                        tmp = 'col'
                        break
                fault_tab[a].append(tmp)
            else:
                fault_tab[a].append(['fst', observation[a][t+1][2]-observation[a][t][2]-1])

    # use the faults table to extract the faults
    for a in range(len(fault_tab)):
        t = 0
        while t < len(fault_tab[a]):
            if type(fault_tab[a][t]) is str and fault_tab[a][t] == 'del':
                t1 = t + 1
                while t1 < len(fault_tab[a]) and type(fault_tab[a][t1]) is str and fault_tab[a][t1] == 'del':
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


def calculate_shapley_gold_standard(board_size, plan, W, cost_function, failure_wall_clock_time):
    print('shapley gold standard')

    # time logging
    start_time = datetime.now()

    # calculate shapley value for the system - what is the contribution of each fault to the grand failure
    # this is the gold standard. use memorization
    seen = []
    seen_cf = {}
    shapley_gold = shapley(board_size, plan, failure_wall_clock_time, W, cost_function, seen, seen_cf)

    # normalize the shpley values for the system
    values_list = list(map(lambda item: item[1], shapley_gold))
    normalized_values = helper.normalize_values_list(values_list)
    shapley_gold_normalized = copy.deepcopy(shapley_gold)
    for i, sgn in enumerate(shapley_gold_normalized):
        sgn[1] = normalized_values[i]

    # time logging
    end_time = datetime.now()
    runtime = end_time - start_time

    print(f'shapley gold runtime: {runtime}')

    return shapley_gold_normalized, runtime


def diagnose(board_size, plan, observation, cost_function, diagnosis_generation_methods, failure_wall_clock_time):
    # logging
    print(f'######################## diagnosing ########################')
    print(f'plan:')
    helper.print_matrix(plan)
    print(f'observation')
    helper.print_matrix(observation)

    # extract certain faults. certain faults are faults that certainly happened
    # during the execution. these are either speedups of an agent, or delays
    # that cannot be explained as result of collision between two agents
    W = extract_certain_faults(plan, observation)
    print(W)
    print(len(W))

    # calculate gold standard shapley values for the faulty events w in W
    shapley_gold, runtime_gold = calculate_shapley_gold_standard(board_size, plan, W, cost_function, failure_wall_clock_time)

    print(9)
    # for each of the diagnosis generation methods, input the same input as the
    # gold standard and then calculate an additive shapley values - i.e., for every
    # set of diagnoses (cardinality, tempral, etc) calculate the shapley value until then
    # todo continue
    return shapley_gold, runtime_gold
