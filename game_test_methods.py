import game

from tulip.transys import WeightedKripkeStructure as WKS
from tulip.transys.automata import WeightedFiniteStateAutomaton as WFA
from tulip.spec.prioritized_safety import PrioritizedSpecification
from tulip.transys.mathset import PowerSet
from tulip.mvp import solve as solve_mvp
import graph_manager as gm
def sample_graph():
    tower = gm.return_tower(2, 1, [1,1], [1,1])

    trace = gm.generate_trace(tower)[1]
    gm.generate_trace(tower)[3].plot()
    # print(trace)
    # req_to_add = ('REALTIME REQUEST', 4)
    # resultant_graph = gm.rollout_monte_carlo(trace, 1, req_to_add=req_to_add)
    # cheaper_graph = gm.rollout_monte_carlo(trace, 2, req_to_add=req_to_add)
    # outrageous_graph = gm.rollout_monte_carlo(trace, 0, req_to_add=req_to_add)
    #
    # gm.generate_trace(resultant_graph)[3].plot()
    # gm.generate_trace(cheaper_graph)[3].plot()
    # gm.generate_trace(outrageous_graph)[3].plot()
    # resultant_graph.plot()

def test_game_loop():
    towerC1 = gm.return_tower(3, 3, [1,1,1], [0,1,0])
    towerC2 = gm.return_tower(3, 1, [3,3,3], [2])
    towerC3 = gm.return_tower(3, 3, [3,3,3], [1,1,2])
    towerC4 = gm.return_tower(3, 3, [4,4,4], [2, 2, 2])
    towerC5 = gm.return_tower(3, 3, [2,2,2],[3,3,3])
    systemC = [towerC1, towerC2, towerC3, towerC4, towerC5]

    game.main_loop(systemC, rollout_index=1)

def test_minimized_traces():

    towerC1 = gm.return_tower(3, 3, [1,1,1], [0,1,0])
    towerC2 = gm.return_tower(3, 1, [3,3,3], [2])
    towerC3 = gm.return_tower(3, 3, [3,3,3], [1,1,2])
    towerC4 = gm.return_tower(3, 3, [4,4,4], [2, 2, 2])
    towerC5 = gm.return_tower(3, 3, [2,2,2],[3,3,3])
    systemC = [towerC1, towerC2, towerC3, towerC4, towerC5]

    game.get_minimized_traces_from_system(systemC)
# test_minimized_traces()
test_game_loop()