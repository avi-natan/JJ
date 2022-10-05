import helper

def simulate_instance(board_size, plan, faulty_agents, fault_probability, fault_speed_range,
                      fault_type, failure_detector, repeat_number, instance_number, total_instances_count):

    # logging
    print(f'######################## simulating instance {instance_number}/{total_instances_count} ########################')
    print(f'board_size: {board_size}')
    print(f'plan:')
    helper.print_matrix(plan)
    print(f'faulty_agents: {faulty_agents}')
    print(f'fault_probability: {fault_probability}')
    print(f'fault_speed_range: {fault_speed_range}')
    print(f'fault_type: {fault_type}')
    print(f'failure_detector: {failure_detector}')
    print(f'repeat_number: {repeat_number}')
    print(f'instance_number: {instance_number}')
    print(f'total_instances_count: {total_instances_count}')



    return [], []
