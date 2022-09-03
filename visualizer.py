import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors

const_colors = {
    0: [0, 1, 0],
    1: [0, 0, 1],
    2: [0.5, 0, 0],
    3: [0, 0.5, 0],
    4: [0, 0, 0.5],
    5: [0.1, 0.8, 0.8],
    6: [1, 0.1, 1],
    7: [1, 1, 0.1],
    8: [1, 0.7, 0],
    9: [0.6, 0, 0.6],
    10: [1, 0, 0.4],
    11: [0.3, 0.3, 0.3]
}

def get_pick_color(color_id):
    return const_colors[color_id % 12]

def visualize(height, width, plans, mode='grid', orientation='console'):
    a_matrix = plans
    board = np.zeros((width, height))
    # plt.figure()
    plt.figure(dpi=300)
    cmap = colors.ListedColormap(['white', 'black'])
    plt.imshow(board, interpolation='none', vmin=0, vmax=2, aspect='equal', cmap=cmap)

    ax = plt.gca()

    # Major ticks
    ax.set_xticks(np.arange(0, height, 1))
    ax.set_yticks(np.arange(0, width, 1))

    # Labels for major ticks
    ax.set_xticklabels(np.arange(0, height, 1))
    ax.set_yticklabels(np.arange(0, width, 1))

    # Minor ticks
    ax.set_xticks(np.arange(-.5, height, 1), minor=True)
    ax.set_yticks(np.arange(-.5, width, 1), minor=True)

    # We change the fontsize of minor ticks label
    ax.tick_params(axis='both', which='major', labelsize=6)
    ax.tick_params(axis='both', which='minor', labelsize=1)

    # Gridlines based on minor ticks
    if mode == 'net':
        ax.grid(which='major', color='black', linestyle='-', linewidth=2, zorder=0)
    elif mode == 'grid':
        ax.grid(which='minor', color='black', linestyle='-', linewidth=2, zorder=0)
    else:
        raise Exception("mode needs to be either 'grid' or 'net'")

    ax.xaxis.tick_top()
    if orientation == 'console':
        x = 1
        y = 0
    else:
        x = 0
        y = 1
    for ai, _ in enumerate(a_matrix):
        for i in range(len(a_matrix[ai][:-2])):
            plt.arrow(a_matrix[ai][i][x], a_matrix[ai][i][y],
                      a_matrix[ai][i + 1][x] - a_matrix[ai][i][x],
                      a_matrix[ai][i + 1][y] - a_matrix[ai][i][y],
                      width=0.5 - (0.5 / len(a_matrix)) * (ai % len(a_matrix)), color=get_pick_color(ai),
                      head_length=0, head_width=0, zorder=3 + ai % len(a_matrix))
        plt.arrow(a_matrix[ai][-2][x], a_matrix[ai][-2][y],
                  a_matrix[ai][-1][x] - a_matrix[ai][-2][x],
                  a_matrix[ai][-1][y] - a_matrix[ai][-2][y],
                  width=0.5 - (0.5 / len(a_matrix)) * (ai % len(a_matrix)), color=get_pick_color(ai),
                  head_width=0.5, head_length=0.5, zorder=3 + ai % len(a_matrix))

    plt.show()
