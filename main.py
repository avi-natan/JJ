# Press the green button in the gutter to run the script.
import ast
import random
from datetime import datetime

import diagnoser2
import helper
import planner_simple
import simulator
import simulator2
import visualizer
import diagnoser


def read_experiment_bundle(filename):
    with open('Experiment_Bundles/' + filename) as f:
        lines = f.readlines()
    lines = list(filter(lambda l: l[:2] != ';;', lines))
    board_sizes = ast.literal_eval(lines[0][:-1].split(sep=':')[1])
    plan_lengths = ast.literal_eval(lines[1][:-1].split(sep=':')[1])
    agent_nums = ast.literal_eval(lines[2][:-1].split(sep=':')[1])
    faulty_agents_nums = ast.literal_eval(lines[3][:-1].split(sep=':')[1])
    fault_probabilities = ast.literal_eval(lines[4][:-1].split(sep=':')[1])
    fault_speed_ranges = ast.literal_eval(lines[5][:-1].split(sep=':')[1])
    fault_types = ast.literal_eval(lines[6][:-1].split(sep=':')[1])
    failure_detectors = ast.literal_eval(lines[7][:-1].split(sep=':')[1])
    cost_functions = ast.literal_eval(lines[8][:-1].split(sep=':')[1])
    diagnosis_generation_methods = ast.literal_eval(lines[9][:-1].split(sep=':')[1])
    repeats_number = int(lines[10][:-1].split(sep=':')[1])
    return board_sizes, plan_lengths, agent_nums, faulty_agents_nums, fault_probabilities, fault_speed_ranges, \
        fault_types, failure_detectors, cost_functions, diagnosis_generation_methods, repeats_number


def runPaperExperiment():
    pass


def runExperimentBundle(filename):
    # read parameters from file
    board_sizes, plan_lengths, agent_nums, faulty_agents_nums, fault_probabilities, fault_speed_ranges, \
        fault_types, failure_detectors, cost_functions, diagnosis_generation_methods, repeats_number = \
        read_experiment_bundle(filename)

    # calculate the total number of instances and initiate instance number
    total_instances = len(board_sizes) * len(plan_lengths) * len(agent_nums) * len(faulty_agents_nums) \
        * len(fault_probabilities) * len(fault_speed_ranges) * len(fault_types) \
        * len(failure_detectors) * len(cost_functions) * len(diagnosis_generation_methods) * repeats_number
    instance_number = 1

    # create instances
    for bs in board_sizes:
        for pl in plan_lengths:
            for an in agent_nums:
                # create a plan
                """
                A is a set of agents. an is the size of a (|A|).
                T is a set of timesteps.
                V is a set of possible location an agent may occupy.
                plan
                pi: A x T -> V is a mapping of (a,t) to the location v that agent a is planned to occupy at time t.
                    note, that the legth of the plans of different agents may vary.
                """
                plan, plan_remake = planner_simple.create_naiive_plan(bs, pl, an)
                while plan_remake:
                    print('plan remake')
                    plan, plan_remake = planner_simple.create_naiive_plan(bs, pl, an)
                # visualizer.animate(bs[0], bs[1], plan, orientation='console')
                visualizer.visualize(bs[0], bs[1], plan, orientation='console')
                for fan in faulty_agents_nums:
                    #  choose the faulty agents
                    F = list(range(an))
                    random.shuffle(F)
                    F = F[:fan]
                    F.sort()
                    for fp in fault_probabilities:
                        for fsr in fault_speed_ranges:
                            for ft in fault_types:
                                for fd in failure_detectors:
                                    for rn in range(repeats_number):
                                        # execute the plans to get annotated observation
                                        """
                                        observation
                                        o: A x T -> V is a mapping of agent a at time t to the location a occupied at time t.
                                        
                                        plan step
                                        tao: A x T -> T is a mapping between the wall clock time and the plan
                                             step for agent a.
                                             
                                        plan offset
                                        D_tao: A x T -> Z is defined as: t - tao(a,t).
                                        
                                        if no faults occur then:
                                        1. tao(a,t) = t
                                        2. o(a,t) = pi(a,t)
                                        3. D_tao(a,t) = 0
                                        
                                        An annotated observation looks as follows:
                                        obs = [agent obs]
                                        agent obs = [temporal units]
                                        temporal unit = [wall clock, position, plan step, plan offset]
                                        position = [x coordinate, y coordinate]
                                    
                                        according to the document, it follows that:
                                        t(a,t) = observation[a][t][0]
                                        o(a,t) = observation[a][t][1]
                                        tao(a,t) = observation[a][t][2]
                                        D_tao(a,t) = observation[a][t][3]
                                        """
                                        annotated_observation, spdchgtab, simulation_remake = \
                                            simulator2.simulate_instance(bs, plan, F, fp, fsr, ft, fd, rn + 1,
                                                                         instance_number, total_instances)
                                        while simulation_remake:
                                            print('simulation remake')
                                            annotated_observation, spdchgtab, simulation_remake = \
                                                simulator2.simulate_instance(bs, plan, F, fp, fsr, ft, fd, rn + 1,
                                                                             instance_number, total_instances)
                                        helper.print_matrix(annotated_observation)
                                        # advance instance number by 1
                                        instance_number += 1

                                        for cf in cost_functions:
                                            # diagnose
                                            res = diagnoser2.diagnose(bs, plan, annotated_observation, cf,
                                                                      diagnosis_generation_methods, fd)
                                            print(9)



if __name__ == '__main__':
    print('Hi, JonJon pipeline!')
    start_time = datetime.now()

    runPaperExperiment()
    runExperimentBundle("developement.expbundle")

    end_time = datetime.now()
    delta = end_time - start_time
    print(f'time to finish: {delta}')

    print(f'Bye JonJon pipeline!')
