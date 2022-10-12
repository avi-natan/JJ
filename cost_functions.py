def cost_max_offset(cf):
    return max(0, max([pl[-1][3] for pl in cf]))

def make_cost_function(cost_function):
    if cost_function[:11] == 'cost_max_of':
        # print('cost_max_offset')
        return cost_max_offset
    elif cost_function[:11] == 'cost_sum_of':
        # todo implement
        print('cost_sum_offset')
        return None
    elif cost_function[:11] == 'cost_max_at':
        # todo implement
        print('cost_max_at_location')
        return None
    elif cost_function[:11] == 'cost_sum_at':
        # todo implement
        print('cost_sum_at_location')
        return None
    else:   # cost_function == 'cost_stuck':
        # todo implement
        print('cost_stuck')
        return None
