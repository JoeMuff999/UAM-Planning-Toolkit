import game

from tulip.transys import WeightedKripkeStructure as WKS
from tulip.transys.automata import WeightedFiniteStateAutomaton as WFA
from tulip.spec.prioritized_safety import PrioritizedSpecification
from tulip.transys.mathset import PowerSet
from tulip.mvp import solve as solve_mvp
import graph_manager as gm


def test_minimized_traces():

    towerC1 = gm.return_tower(3, 3, [1,1,1], [0,1,0])
    towerC2 = gm.return_tower(3, 1, [3,3,3], [2])
    towerC3 = gm.return_tower(3, 3, [3,3,3], [1,1,2])
    towerC4 = gm.return_tower(3, 3, [4,4,4], [2, 2, 2])
    towerC5 = gm.return_tower(3, 3, [2,2,2],[3,3,3])
    systemC = [towerC1, towerC2, towerC3, towerC4, towerC5]

    game.get_minimized_traces_from_system(systemC)
test_minimized_traces()