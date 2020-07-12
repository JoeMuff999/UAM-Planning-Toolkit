import reworked_graph
import copy
import time

from tulip.transys import WeightedKripkeStructure as WKS
from tulip.transys.automata import WeightedFiniteStateAutomaton as WFA
from tulip.spec.prioritized_safety import PrioritizedSpecification
from tulip.transys.mathset import PowerSet
from tulip.mvp import solve as solve_mvp
import graph_manager as gm

State = reworked_graph.State

def state_tests(graph):
    print(graph.transitions)
    print(graph.states)

def iterate_all_requests_tests():
    test = (["a", "b", "c"], [2, 2, 2])
    graph.iterate_all_requests(test, [0, 2])
    print(test)

def set_tests():
    state1 = State((1,2,3,4,1,2,1), (1,1,1,2,2,2,2))
    state2 = State((1,2,3,4,1,2,1), (1,1,1,2,2,2,2))
    state3 = State((1,2), (2,3))
    state4 = State((), ())
    state5 = State((), ())
    #state1._port_dict[1] = 99
    transition1 = (state1, None, state3)
    transition2 = (state2, None, state3)
    # test = set()
    # test.add(state1)
    # test.add(state2)
    # test.add(state3)
    # test.add(state4)
    # test.add(state5)
    trans_set = set()
    trans_set.add(transition1)
    trans_set.add(transition2)
    # print(test)
    #print(trans_set)

def port_tests():
    state = State(('a','b','a'), (2,3,2))
    copied_requests = []
    tup1 = ('b', 3)
    tup2 = ('a', 1)
    tup3 = ('a', 1)
    copied_requests.append(tup1)
    copied_requests.append(tup2)
    copied_requests.append(tup3)
    state.update_port_states(copied_requests)
    print(state)

def tulip_tests(graph):
    ts = WKS()
    ts.states.add_from(graph.states)
    ts.states.initial.add(graph.base_state)

    for transition in graph.transitions:
        ts.transitions.add(transition[0], transition[2], {"cost": 1})

    ts.atomic_propositions.add("VALID")
    ts.atomic_propositions.add("WRONG_PORT")
    ts.atomic_propositions.add("OVERFLOWED_PORT")
    ts.atomic_propositions.add("FINISH")

    for s in graph.states:
        ts.states[s]["ap"] = set(s.labels)

    fa0 = WFA()
    fa0.atomic_propositions.add_from(ts.atomic_propositions)
    fa0.states.add_from({"q0"})
    fa0.states.initial.add("q0")
    fa0.states.accepting.add("q0")

    ap_without_valid = copy.deepcopy(fa0.atomic_propositions)
    ap_without_valid.remove("VALID")
    valid = {"VALID"}

    for letter in PowerSet(ap_without_valid):  # union of everything with valid
        fa0.transitions.add("q0", "q0", letter=set(letter) | valid)

    fa1 = WFA()
    fa1.atomic_propositions.add_from(ts.atomic_propositions)
    fa1.states.add_from({"q0"})
    fa1.states.initial.add("q0")
    fa1.states.accepting.add("q0")

    ap_without_wrong_port = copy.deepcopy(fa1.atomic_propositions)
    ap_without_wrong_port.remove("WRONG_PORT")
    wrong_port = {"WRONG_PORT"}

    for letter in PowerSet(ap_without_wrong_port):
        fa1.transitions.add("q0", "q0", letter=letter)

    fa2 = WFA()
    fa2.atomic_propositions.add_from(ts.atomic_propositions)
    fa2.states.add_from({"q0"})
    fa2.states.initial.add("q0")
    fa2.states.accepting.add("q0")

    ap_without_port_overflow = copy.deepcopy(fa2.atomic_propositions)
    ap_without_port_overflow.remove("OVERFLOWED_PORT")

    for letter in PowerSet(ap_without_port_overflow):
        fa2.transitions.add("q0", "q0", letter=letter)

    spec = PrioritizedSpecification()
    spec.add_rule(fa0, priority=1, level=0)
    spec.add_rule(fa1, priority=1, level=1)
    spec.add_rule(fa2, priority=2, level=1)

    (cost, state_path, product_path, wpa) = solve_mvp(ts, "FINISH", spec)

    print("Optimal cost: {}".format(cost))
    print("State path: {}".format(state_path))
    print("Product path: {}".format(product_path))

def permutation_tests(graph):
    tmp_dict = {"A" : 1, "B": 2, "C" : 3, "D" : 4}
    s = list(graph.generate_cartesian_product(list(tmp_dict.keys()), 1))
    print(tmp_dict.keys())
    counter = 0
    print(list(s))
    for i in s:
        counter+=1
    print(list(s))
    print(counter)

def tests():
    ls = []
    print(all(i >= 0 for i in ls))

def tower_runtime_analysis():
    #reset dictionaries because global
    run_towerA()
    clear_gm_dicts()
    run_towerB()
    clear_gm_dicts()
    run_towerC()
    clear_gm_dicts()
    run_towerD()

def clear_gm_dicts():
    gm.synthesis_dictionary.clear()
    gm.worst_request_dictionary.clear()

def run_towerD():

    towerD1 = gm.return_tower(3, 3, [1,1,1], [0,1,0])
    towerD2 = gm.return_tower(3, 1, [3,3,3], [2])
    towerD3 = gm.return_tower(3, 3, [3,3,3], [1,1,2])
    towerD4 = gm.return_tower(3, 3, [4,4,4], [2, 2, 2])
    towerD5 = gm.return_tower(3, 3, [2,2,2],[3,3,3])
    towerD6 = gm.return_tower(3, 3, [0,3,2],[1,1,1])

    systemD = [towerD1, towerD2, towerD3, towerD4, towerD5, towerD6]

    time_start = time.perf_counter()
    total_timeD, total_roundsD = gm.run_minimizing_mvp(systemD)
    time_end = time.perf_counter()
    average_round_timeD = total_timeD / total_roundsD

    print("\nsystemD with six towers completed in time " + str(time_end - time_start) + "\n"
          + "With a total runtime of " + str(total_timeD) + ", total round count of " + str(total_roundsD)
          + " and an average round time of " + str(average_round_timeD))

def run_towerC():

    towerC1 = gm.return_tower(3, 3, [1,1,1], [0,1,0])
    towerC2 = gm.return_tower(3, 1, [3,3,3], [2])
    towerC3 = gm.return_tower(3, 3, [3,3,3], [1,1,2])
    towerC4 = gm.return_tower(3, 3, [4,4,4], [2, 2, 2])
    towerC5 = gm.return_tower(3, 3, [2,2,2],[3,3,3])
    systemC = [towerC1, towerC2, towerC3, towerC4, towerC5]

    time_start = time.perf_counter()
    total_timeC, total_roundsC = gm.run_minimizing_mvp(systemC)
    time_end = time.perf_counter()
    average_round_timeC = total_timeC/total_roundsC
    print("\nsystemC with five towers completed in time " + str(time_end - time_start) + "\n"
          + "With a total runtime of " + str(total_timeC) + ", total round count of " + str(total_roundsC)
          + " and an average round time of " + str(average_round_timeC))

def run_towerA():

    towerA1 = gm.return_tower(3, 3, [1,1,1], [0,1,0])
    towerA2 = gm.return_tower(3, 1, [3,3,3], [2])
    towerA3 = gm.return_tower(3, 3, [4,4,4], [2, 2, 2])#gm.return_tower(3, 3, [3,3,3], [1,1,2])
    systemA = [towerA1, towerA2, towerA3]

    time_start = time.perf_counter()
    total_timeA, total_roundsA = gm.run_minimizing_mvp(systemA)
    time_end = time.perf_counter()
    average_round_timeA = total_timeA / total_roundsA
    print("\nsystemA with three towers completed in time " + str(time_end - time_start) + "\n"
          + "With a total runtime of " + str(total_timeA) + ", total round count of " + str(total_roundsA)
          + "and an average round time of " + str(average_round_timeA) + "\n")
def run_towerB():

    towerB1 = gm.return_tower(3, 3, [1,1,1], [0,1,0])
    towerB2 = gm.return_tower(3, 1, [3,3,3], [2])
    towerB3 = gm.return_tower(3, 3, [3,3,3], [1,1,2])
    towerB4 = gm.return_tower(3, 3, [4,4,4], [2, 2, 2])
    systemB = [towerB1, towerB2, towerB3, towerB4]

    time_start = time.perf_counter()
    total_timeB, total_roundsB = gm.run_minimizing_mvp(systemB)
    time_end = time.perf_counter()
    average_round_timeB = total_timeB/total_roundsB
    print("\nsystemB with four towers completed in time " + str(time_end - time_start) + "\n"
          + "With a total runtime of " + str(total_timeB) + ", total round count of " + str(total_roundsB)
          + " and an average round time of " + str(average_round_timeB))

tower_runtime_analysis()
#   def __init__(self, requests_per_port_per_step={}, max_accepted_requests=0, request_vector=[],
               #  max_time_per_req_vector=[]):

