import copy


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


def calculate_minus_set(W, w):
    W_minus_w = []
    for elem in W:
        if elem not in w:
            W_minus_w.append([elem[0], elem[1], elem[2]])
    return W_minus_w


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
        values_list_normalized[i] = values_list_normalized[i] * 1.0 / sum_values

    # return the resulting list
    return values_list_normalized

