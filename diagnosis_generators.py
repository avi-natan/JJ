def dgm_cardi_asc_tempo_rnd(subsets):
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

def make_diagnosis_generator(diagnosis_generator_method):
    dgm_splitted = diagnosis_generator_method.split('_')
    if dgm_splitted[1] == 'cardi' and dgm_splitted[4] == 'dsc':
        print('dgm_cardi_asc_tempo_dsc')
        return None
    elif dgm_splitted[1] == 'cardi' and dgm_splitted[4] == 'asc':
        # todo implement
        print('dgm_cardi_asc_tempo_asc')
        return None
    elif dgm_splitted[1] == 'tempo' and dgm_splitted[2] == 'dsc':
        # todo implement
        print('dgm_tempo_dsc_cardi_asc')
        return None
    elif dgm_splitted[1] == 'tempo' and dgm_splitted[2] == 'asc':
        # todo implement
        print('cost_sum_at_location')
        return None
    else:   # diagnosis_generator_method == 'dgm_cardi_asc_tempo_rnd':
        print('dgm_cardi_asc_tempo_rnd')
        return dgm_cardi_asc_tempo_rnd
