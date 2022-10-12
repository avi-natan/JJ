import copy
from itertools import combinations

import numpy


def print_matrix(matrix):
    s = [[str(e) for e in row] for row in matrix]
    max_len = max(list(map(lambda row: len(row), s)))
    s_padded = [[] for _ in s]
    for ri in range(len(s)):
        for ci in range(max_len):
            if ci < len(s[ri]):
                s_padded[ri].append(s[ri][ci])
            else:
                s_padded[ri].append('')
    lens = [max(map(len, col)) for col in zip(*s_padded)]
    fmt = '\t'.join('{{:{}}}'.format(x) for x in lens)
    table = [fmt.format(*row) for row in s_padded]
    print('\n'.join(table))


def is_superset(w, d):
    for elem in d:
        if elem not in w:
            return False
    return True


def superset_of_element(w, D):
    for d in D:
        if is_superset(w, d):
            return True
    return False


def calculate_minus_set(W, S):
    W_minus_S = []
    for elem in W:
        if elem not in S:
            W_minus_S.append([elem[0], elem[1], elem[2]])
    return W_minus_S


def is_subset(sub, sup):
    for item in sub:
        if item not in sup:
            return False
    return True


def normalize_values_list(values_list):
    # deepcopy the values first
    values_list_normalized = copy.deepcopy(values_list)

    # find the minimum value (negative one)
    minimum_value = min(values_list_normalized)

    # update the values by shifting to the 0
    for i in range(len(values_list_normalized)):
        values_list_normalized[i] = values_list_normalized[i] - minimum_value

    # sum up the updated values
    sum_values = sum(values_list_normalized)

    # divide the values by the sum
    for i in range(len(values_list_normalized)):
        values_list_normalized[i] = values_list_normalized[i] * 1.0 / sum_values if sum_values != 0.0 else 0.0

    # return the resulting list
    return values_list_normalized


def cut_execution(plan, execution, plan_step, plan_offset, spdchgtab, fth):
    cut_time = -1

    maxlen = max([len(p) for p in plan_offset])
    for t in range(maxlen):
        if cut_time != -1:
            break
        else:
            for i in range(len(plan_offset)):
                if t < len(plan_offset[i]):
                    if plan_offset[i][t] >= fth:
                        cut_time = t
                        break

    new_plan = []
    for i in plan:
        new_plan.append(copy.deepcopy(i[:cut_time + 1]))
    new_execution = []
    for i in execution:
        new_execution.append(copy.deepcopy(i[:cut_time+1]))
    new_plan_step = []
    for i in plan_step:
        new_plan_step.append(copy.deepcopy(i[:cut_time+1]))
    new_plan_offset = []
    for i in plan_offset:
        new_plan_offset.append(copy.deepcopy(i[:cut_time+1]))
    new_spdchgtab = []
    for i in spdchgtab:
        new_spdchgtab.append(copy.deepcopy(i[:cut_time]))

    # cut out cells of timesteps that their global timer in the plan step table exceeds the new last plans
    for i in range(len(new_plan_step)):
        while new_plan_step[i][-1] >= len(new_plan[i]):
            new_execution[i] = new_execution[i][:-1]
            new_plan_offset[i] = new_plan_offset[i][:-1]
            new_plan_step[i] = new_plan_step[i][:-1]
            new_spdchgtab[i] = new_spdchgtab[i][:-1]

    print('new_plan:')
    print_matrix(new_plan)
    print('new speed change table:')
    print_matrix(new_spdchgtab)
    print('new_execution:')
    print_matrix(new_execution)
    print('new_plan_step:')
    print_matrix(new_plan_step)
    print('new_plan_offset:')
    print_matrix(new_plan_offset)

    return new_plan, new_execution, new_plan_step, new_plan_offset, new_spdchgtab


def detect_cycle(source, graph, color):
    color[source] = "G"

    for v in graph[source]:
        if color[v] == "W":
            cycle = detect_cycle(v, graph, color)
            if cycle:
                return True
        elif color[v] == "G":
            return True
    color[source] = "B"
    return False


def search_cycles(graph):
    for source in graph.keys():
        color = {}
        for node in graph.keys():
            color[node] = "W"
        has_cycle = detect_cycle(source, graph, color)
        if has_cycle:
            return True
    return False

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

def equivalent_sets(set1, set2):
    for i in set1:
        if i not in set2:
            return False
    for i in set2:
        if i not in set1:
            return False
    return True


def euclidean_distance(brd_values, shg_values):
    np_brd_values = numpy.array(brd_values)
    np_shg_values = numpy.array(shg_values)
    distance = numpy.linalg.norm(np_brd_values-np_shg_values)
    return distance
