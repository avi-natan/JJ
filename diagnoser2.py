import copy
import math

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

def shapley_for_system(CFS, W, cost_function):
    """
    The shapley value function for player w, a group of players W and characteristic function f is represented as:

                         ____
    Phi_w(f, W) =  _1_   \     |S|!*(n-1-|S|)![f(S u {w}) - f(S)]
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
    Phi = []
    n = len(W)
    cost_func = cost_functions.make_cost_function(cost_function)
    temp_w = 0
    for w in W:
        W_minus_w = [item for item in CFS if w not in item[0]]
        total_sum = 0
        temp_S = 0
        for S in W_minus_w:
            print(f'temp_w: {temp_w}/{n}, temp_S:{temp_S}/{len(W_minus_w)}')
            temp_S += 1
            len_S = len(S[0])
            f_S = cost_func(S)
            Sui = [item for item in CFS if helper.equivalent_sets(S[0] + [w], item[0])][0]
            f_Sui = cost_func(Sui)
            sum_S = math.factorial(len_S) * math.factorial(n-len_S-1) * (f_Sui - f_S)
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


def calculate_shapley_gold_standard(board_size, plan, W, cost_function, failure_detector):
    # calculate the gold standard, which is the shapley value
    # for each of the fault events in W giver a cost function
    # get a list of the subsets of the list
    subsets_W = helper.subsets(W)
    print(len(subsets_W))

    # initialize counterfactuals list CFS
    CFS = []

    # for each subset E of W, simulate the plan without the faults in E.
    # get the resulting executions in a counterfactuals list
    temp = 0
    for E in subsets_W:
        print(f'{temp}/{len(subsets_W)}')
        temp += 1
        # create a faults table for W\E
        W_minus_E = helper.calculate_minus_set(W, E)
        faults_tab_W_minus_E = create_faults_table(W_minus_E, len(plan))

        # simulate the plans with the faults table to get the counterfactual
        cf_E = simulator2.calculate_counterfactual(board_size, plan, faults_tab_W_minus_E, failure_detector)

        # insert the execution of W\E into the counterfactual list CFS: [E, goal_delays_E, execution_E]
        CFS.append([E, cf_E])

    # calculate shapley value for the system - what is the contribution of each fault to the grand failure
    # this is the gold standard
    print('shapley for system')
    shapley_gold = shapley_for_system(CFS, W, cost_function)

    # normalize the shpley values for the system
    values_list = list(map(lambda item: item[1], shapley_gold))
    normalized_values = helper.normalize_values_list(values_list)
    shapley_gold_normalized = copy.deepcopy(shapley_gold)
    for i, sgn in enumerate(shapley_gold_normalized):
        sgn[1] = normalized_values[i]

    return shapley_gold_normalized


def diagnose(board_size, plan, observation, diagnosis_generation_methods, cost_function, failure_detector):
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
    shapley_gold = calculate_shapley_gold_standard(board_size, plan, W, cost_function, failure_detector)

    print(9)
    # for each of the diagnosis generation methods, input the same input as the
    # gold standard and then calculate an additive shapley values - i.e., for every
    # set of diagnoses (cardinality, tempral, etc) calculate the shapley value until then
    # todo continue
    return shapley_gold
