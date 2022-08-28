# Press the green button in the gutter to run the script.
import ast
from datetime import datetime

import planners
import visualizer


def read_experiment_bundle(filename):
    with open('Experiment_Bundles/' + filename) as f:
        lines = f.readlines()
    lines = list(filter(lambda l: l[:2] != ';;', lines))
    board_sizes = ast.literal_eval(lines[0][:-1].split(sep=':')[1])
    plan_lengths = ast.literal_eval(lines[1][:-1].split(sep=':')[1])
    agent_nums = ast.literal_eval(lines[2][:-1].split(sep=':')[1])
    faulty_agents_nums = ast.literal_eval(lines[3][:-1].split(sep=':')[1])
    speed_variations = ast.literal_eval(lines[4][:-1].split(sep=':')[1])
    speed_variation_types = ast.literal_eval(lines[5][:-1].split(sep=':')[1])
    conflict_delay_times = ast.literal_eval(lines[6][:-1].split(sep=':')[1])
    repeats_number = int(lines[7][:-1].split(sep=':')[1])
    return board_sizes, plan_lengths, agent_nums, faulty_agents_nums, speed_variations, speed_variation_types,\
        conflict_delay_times, repeats_number

def runPaperExperiment():
    pass

def runExperimentBundle(filename):
    board_sizes, plan_lengths, agent_nums, faulty_agents_nums, speed_variations, speed_variation_types, \
        conflict_delay_times, repeats_number = read_experiment_bundle(filename)
    for bs in board_sizes:
        for pl in plan_lengths:
            for an in agent_nums:
                plan = planners.create_naiive_plan(bs, pl, an)
                visualizer.visualize(bs[0], bs[1], plan, orientation='console')
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
