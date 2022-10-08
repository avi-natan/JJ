import diagnoser
import diagnoser2
import visualizer

if __name__ == '__main__':
    plan = \
        [[[0, 5], [1, 5], [2, 5], [2, 4], [2, 3], [2, 2], [2, 1], [2, 0]],
         [[0, 3], [1, 3], [2, 3], [3, 3], [4, 3], [4, 2], [4, 1]],
         [[0, 0], [1, 0], [2, 0], [3, 0], [3, 1], [3, 2], [3, 3], [3, 4], [3, 5]]]
    visualizer.visualize(5, 6, plan)

    # spdchgtab = \
    #     [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #      [-1, 0, 0, 2, 0],
    #      [-2, -1j, 0, 0, -1, -2, -1j, -1, -1, 2, 2]]
    #
    # execution = \
    #     [[[0, 5], [1, 5], [2, 5], [2, 4], [2, 4], [2, 3], [2, 2], [2, 1], [2, 1], [2, 1], [2, 1], [2, 0]],
    #      [[0, 3], [0, 3], [1, 3], [2, 3], [4, 2], [4, 1]],
    #      [[0, 0], [0, 0], [0, 0], [1, 0], [2, 0], [2, 0], [2, 0], [2, 0], [2, 0], [2, 0], [3, 2], [3, 5]]]

    # # old version of observation, works with diagnoser file
    # spdchgtab = \
    #     [[2, 2, 0, 2],
    #      [0, 0, 0, 0, 0, 0, 0, 0],
    #      [0, 0, 2, 1, -2, -1j, 0]]

    # execution = \
    #     [[[0,5], [2,4], [2,1], [2,1], [2,0]],
    #      [[0,3], [1,3], [1,3], [2,3], [2,3], [3,3], [4,3], [4,2], [4,1]],
    #      [[0,0], [1,0], [2,0], [3,2], [3,4], [3,4], [3,4], [3,5]]]
    # diagnoser.diagnose(plan, execution, [5, 6], 1)

    """
    the general form of the observation is as follows:
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
    # new version of observation, works with diagnoser2 file
    spdchgtab = \
        [[0, 2, 2, 0, 2],
         [0, 0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 2, 1, -2, -1j, 0]]

    observation = \
        [[[0,[0,5],0,0], [1,[2,4],3,-2], [2,[2,1],6,-4], [3,[2,1],6,-3], [4,[2,0],7,-3]],
         [[0,[0,3],0,0], [1,[1,3],1,0],  [2,[1,3],1,1],  [3,[2,3],2,1],  [4,[2,3],2,2],  [5,[3,3],3,2],  [6,[4,3],4,2],  [7,[4,2],5,2], [8,[4,1],6,2]],
         [[0,[0,0],0,0], [1,[1,0],1,0],  [2,[2,0],2,0],  [3,[3,2],5,-2], [4,[3,4],7,-3], [5,[3,4],7,-2], [6,[3,4],7,-1], [7,[3,5],8,-1]]]

    diagnoser2.diagnose([5, 6], plan, observation, [], 'cost_function', 'fd_stuck')
