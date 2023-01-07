import copy
import math
# from datetime import datetime
import time

import cost_functions
import diagnosis_generators
import failure_detectors
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
    # print(f'{W}')
    Phi = []
    n = len(W)

    num_cost_f_calls = 0
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
                # print(f'memoization: shapley')
                cf_S = seen_cf[str(W_minus_S)]
            else:
                # print(f'saving at shapley {W_minus_S}')
                faults_tab_W_minus_S = create_faults_table(W_minus_S, len(plan))
                cf_S = simulator2.calculate_counterfactual(board_size, plan, faults_tab_W_minus_S, failure_wall_clock_time)
                seen.append(W_minus_S)
                seen_cf[str(W_minus_S)] = cf_S
            f_cf_S = cost_function(cf_S)
            num_cost_f_calls += 1

            # create the set Suw
            Suw = S + [w]

            # create a faults table for W\(Suw)
            W_minus_Suw = helper.calculate_minus_set(W, Suw)
            if W_minus_Suw in seen:
                # print(f'memoization: shapley')
                cf_Suw = seen_cf[str(W_minus_Suw)]
            else:
                # print(f'saving at shapley {W_minus_Suw}')
                faults_tab_W_minus_Suw = create_faults_table(W_minus_Suw, len(plan))
                cf_Suw = simulator2.calculate_counterfactual(board_size, plan, faults_tab_W_minus_Suw, failure_wall_clock_time)
                seen.append(W_minus_Suw)
                seen_cf[str(W_minus_Suw)] = cf_Suw
            f_cf_Suw = cost_function(cf_Suw)
            num_cost_f_calls += 1

            # calculate the sum for S and add it to the total sum
            sum_S = math.factorial(len_S) * math.factorial(n-len_S-1) * (f_cf_Suw - f_cf_S)
            total_sum += sum_S
        Phi_w = total_sum / math.factorial(n)
        Phi.append([w, Phi_w])
        temp_w += 1
    return Phi, num_cost_f_calls

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

    # calculate shapley value for the system - what is the contribution of each fault to the grand failure
    # this is the gold standard. use memorization
    seen = []
    seen_cf = {}

    # time logging
    start_time = time.time()
    shapley_gold, num_cost_f_calls = shapley(board_size, plan, failure_wall_clock_time, W, cost_function, seen, seen_cf)
    # time logging
    end_time = time.time()
    runtime = end_time - start_time

    # normalize the shpley values for the system
    values_list = list(map(lambda item: item[1], shapley_gold))
    normalized_values = helper.normalize_values_list(values_list)
    shapley_gold_normalized = copy.deepcopy(shapley_gold)
    for i, sgn in enumerate(shapley_gold_normalized):
        sgn[1] = normalized_values[i]

    print(f'shapley gold runtime: {runtime}')

    return shapley_gold_normalized, runtime, num_cost_f_calls


def calculate_shapley_using_dgm(board_size, plan, W, cost_function, failure_detector, failure_wall_clock_time, diagnosis_generator, max_x, min_x):
    # generate the subsets of W
    subsets_W = helper.subsets(W)[1:]

    # sort the subsets according to the diagnosis generator
    sorting_start = time.time()
    # todo: the last part of the below ine (i.e., [:5]) is there to skip calculating using later batches than 1-5
    sorted_subsets_W = diagnosis_generator(subsets_W, failure_wall_clock_time, len(plan[0]), max_x, min_x)[:5]
    sorting_end = time.time()
    delta_sorting = sorting_end - sorting_start

    # initialize memorization data structures
    seen = []
    seen_cf = {}

    # initialize a diagnoses datastructure
    sorted_diagnoses = []
    # for every batch of the sorted subsets do:
    for batch in sorted_subsets_W:
        # initialize a diagnosis batch. set the order number (cardinality, time step, etc) and the runtime of the
        # diagnoses ordering (its an overhead)
        # [batch number, number of diagnoses, number of function calls, runtime, diagnoses list]
        diagnosis_batch = [batch[0], 0, 0, delta_sorting, []]
        # for each subset in the current subset batch do:
        for S in batch[1]:
            # calculate the minus set
            W_minus_S = helper.calculate_minus_set(W, S)
            # retreive the counterfactual, either from memory or by generating it
            if W_minus_S in seen:
                # print(f'memoization: calculate_shapley_using_dgm')
                cf_S = seen_cf[str(W_minus_S)]
            else:
                # print(f'saving at calculate_shapley_using_dgm {W_minus_S}')
                faults_tab_W_minus_S = create_faults_table(W_minus_S, len(plan))
                cf_S = simulator2.calculate_counterfactual(board_size, plan, faults_tab_W_minus_S, failure_wall_clock_time)
                seen.append(W_minus_S)
                seen_cf[str(W_minus_S)] = cf_S
            # if the counterfactual is not failing then S is a diagnosis
            if not failure_detector([], cf_S, [], [], []):
                # update the number of diagnoses in this batch
                diagnosis_batch[1] += 1
                # calculate shapley values for S
                S_start = time.time()
                shapley_S, num_cost_f_calls = shapley(board_size, plan, failure_wall_clock_time, S, cost_function, seen, seen_cf)
                S_end = time.time()
                delta_S = S_end - S_start
                diagnosis_batch[2] = diagnosis_batch[2] + num_cost_f_calls
                diagnosis_batch[3] = diagnosis_batch[3] + delta_S
                # normalize the shpley values for S
                values_list = list(map(lambda item: item[1], shapley_S))
                normalized_values = helper.normalize_values_list(values_list)
                shapley_S_normalized = copy.deepcopy(shapley_S)
                for i, ssn in enumerate(shapley_S_normalized):
                    ssn[1] = normalized_values[i]
                # inset S into the diagnosis batch together with its shapley value
                diagnosis_batch[4].append([S, shapley_S_normalized])
        # calculate the aggregated shapley value until this point
        aggregated = [[fe, 0.0] for fe in W]
        for agg in aggregated:
            fe = agg[0]
            for sd in sorted_diagnoses:
                for dg in sd[8]:
                    if fe in dg[0]:
                        sh_d_fe = list(filter(lambda f: f[0] == fe, dg[1]))[0][1]
                        agg[1] = agg[1] + sh_d_fe
            for dg in diagnosis_batch[4]:
                if fe in dg[0]:
                    sh_d_fe = list(filter(lambda f: f[0] == fe, dg[1]))[0][1]
                    agg[1] = agg[1] + sh_d_fe
        # normalize the aggregted shapley values
        values_list = list(map(lambda item: item[1], aggregated))
        normalized_values = helper.normalize_values_list(values_list)
        aggregated_normalized = copy.deepcopy(aggregated)
        for i, an in enumerate(aggregated_normalized):
            an[1] = normalized_values[i]
        # finally insert the current diagnosis batch into the diagnoses datastructure
        if len(sorted_diagnoses) > 0:
            sorted_diagnoses.append(
                [diagnosis_batch[0], diagnosis_batch[1], diagnosis_batch[1] + sorted_diagnoses[-1][2], diagnosis_batch[2], diagnosis_batch[2] + sorted_diagnoses[-1][4],     diagnosis_batch[3], diagnosis_batch[3] + sorted_diagnoses[-1][6], aggregated_normalized, diagnosis_batch[4]])
        else:
            sorted_diagnoses.append(
                [diagnosis_batch[0], diagnosis_batch[1], diagnosis_batch[1], diagnosis_batch[2], diagnosis_batch[2],     diagnosis_batch[3], diagnosis_batch[3], aggregated_normalized, diagnosis_batch[4]])
    return sorted_diagnoses

def diagnose(board_size, plan, observation, cost_function, failure_detector, diagnosis_generation_methods, failure_wall_clock_time):
    # logging
    print(f'######################## diagnosing ########################')
    print(f'plan:')
    helper.print_matrix(plan)
    print(f'observation')
    helper.print_matrix(observation)

    # initialize cost function
    cost_func = cost_functions.make_cost_function(cost_function)

    # initialize failure detector
    detector = failure_detectors.make_detector(failure_detector)

    # extract certain faults. certain faults are faults that certainly happened
    # during the execution. these are either speedups of an agent, or delays
    # that cannot be explained as result of collision between two agents
    W = extract_certain_faults(plan, observation)
    print(W)
    print(len(W))

    # calculate gold standard shapley values for the faulty events w in W
    shapley_gold, runtime_gold, num_cost_f_calls = calculate_shapley_gold_standard(board_size, plan, W, cost_func, failure_wall_clock_time)

    only_vals = [item[1] for item in shapley_gold]

    # for each of the diagnosis generation methods, input the same input as the
    # gold standard and then calculate an additive shapley values - i.e., for every
    # set of diagnoses (cardinality, tempral, etc) calculate the shapley value until then
    results_dgm = []
    for dgm in diagnosis_generation_methods:
        # make a diagnosis generator
        diagnosis_generator = diagnosis_generators.make_diagnosis_generator(dgm)
        result_dgm = calculate_shapley_using_dgm(board_size, plan, W, cost_func, detector, failure_wall_clock_time, diagnosis_generator, max(only_vals), min(only_vals))
        results_dgm.append([dgm, result_dgm])

    # for each of the dgm results (foreach method there are the batch results) calcualte
    # the euclidean distance between the aggregated shapley value of the result to the
    # shapley value of the gold standard
    shg_values = [item[1] for item in shapley_gold]
    for rd in results_dgm:
        for batch in rd[1]:
            brd_values = [item[1] for item in batch[7]]
            distance = helper.euclidean_distance(brd_values, shg_values)
            batch.insert(1, distance)
            batch.insert(1, len(W))
            # batch.insert(2, -1)
    # finalize the dgm resuts and prepare them for output of this function
    # [name, [[batch number, # faulty events, distance, batch # diagnoses, comulated # diagnoses, batch # cost f calls, comulated # cost f calls, batch runtime, commulated runtime, shapley value]]]
    results_dgm.insert(0, ['gold', [[0, len(W), 0, 0, 0, num_cost_f_calls, num_cost_f_calls, runtime_gold, runtime_gold, shapley_gold]]])
    return results_dgm
