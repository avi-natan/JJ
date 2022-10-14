def dgm_cardi_asc(subsets, failure_wall_clock_time):
    # no sorting here

    # divide to batches
    sorted_batches = []
    min_cardi = len(subsets[0])
    max_cardi = len(subsets[-1])
    for c in range(min_cardi, max_cardi+1):
        # note, in the beginning the order is recorded (c for cardinality in this case)
        batch_c = [c, [s for s in subsets if len(s) == c]]
        sorted_batches.append(batch_c)
    return sorted_batches

def dgm_tempo_dsc(subsets, failure_wall_clock_time):
    sorted_batches = []
    min_t = 1
    max_t = failure_wall_clock_time
    seen = []
    for t in range(max_t, min_t-1, -1):
        # print(t)
        batch_t = [max_t - t + 1, []]
        for s in subsets:
            if s not in seen:
                if t <= min([fa[1] for fa in s]):
                    batch_t[1].append(s)
                    seen.append(s)
        sorted_batches.append(batch_t)
    return sorted_batches

def dgm_tempo_asc(subsets, failure_wall_clock_time):
    sorted_batches = []
    min_t = 1
    max_t = failure_wall_clock_time
    seen = []
    for t in range(min_t, max_t+1, 1):
        # print(t)
        batch_t = [t, []]
        for s in subsets:
            if s not in seen:
                if t >= max([fa[1] for fa in s]):
                    batch_t[1].append(s)
                    seen.append(s)
        sorted_batches.append(batch_t)
    return sorted_batches

def dgm_delay_dsc(subsets, failure_wall_clock_time):
    # for each subset, calculate its delay sum
    delays = [sum([fe[2] for fe in subset]) for subset in subsets]

    # divide to batches
    sorted_batches = []
    max_delay = max(min(delays), 0)
    min_delay = max(delays)
    for d in range(max_delay, min_delay + 1):
        # note, in the beginning the order is recorded (c for cardinality in this case)
        batch_d = [d, [s for s in subsets if sum([fe[2] for fe in s]) == d]]
        sorted_batches.append(batch_d)
    return sorted_batches

def make_diagnosis_generator(diagnosis_generator_method):
    if diagnosis_generator_method == 'dgm_cardi_asc':
        # print('dgm_cardi_asc')
        return dgm_cardi_asc
    elif diagnosis_generator_method == 'dgm_tempo_dsc':
        # print('dgm_tempo_dsc')
        return dgm_tempo_dsc
    elif diagnosis_generator_method == 'dgm_tempo_asc':
        # print('dgm_tempo_asc')
        return dgm_tempo_asc
    elif diagnosis_generator_method == 'dgm_delay_dsc':
        # print('dgm_delay_dsc')
        return dgm_delay_dsc
    else:       # raise error
        print('error: unexected diagnosis generator method')
        raise Exception("unexected diagnosis generator method")
