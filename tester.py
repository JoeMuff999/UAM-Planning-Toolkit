import reworked_graph
import copy
import matplotlib
import graphviz
from IPython.display import Image

from tulip.transys import WeightedKripkeStructure as WKS
from tulip.transys.automata import WeightedFiniteStateAutomaton as WFA
from tulip.spec.prioritized_safety import PrioritizedSpecification
from tulip.transys.compositions import synchronous_parallel
from tulip.transys.mathset import PowerSet
from tulip.mvp import solve as solve_mvp

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
    ts.atomic_propositions.add("SAT")

    for s in graph.states:
        ts.states[s]["ap"] = set(s.labels)

    fa1 = WFA()
    fa1.atomic_propositions.add_from(ts.atomic_propositions)
    fa1.states.add_from({"q0"})
    fa1.states.initial.add("q0")
    fa1.states.accepting.add("q0")

    ap_with_both = copy.deepcopy(fa1.atomic_propositions)
    transition_letters = set(PowerSet(ap_with_both))
    for letter in transition_letters:
        fa1.transitions.add("q0", "q0", letter=letter)

    spec = PrioritizedSpecification()
    spec.add_rule(fa1, priority=1, level=0)

    (cost, state_path, product_path, wpa) = solve_mvp(ts, "SAT", spec)
    #wpa.plot()
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

graph = reworked_graph.ReworkedGraph(3, 5, 2, ["a", "b"], [0, 0])
#set_tests()
#state_tests(graph)
#tests()
#tulip_tests(graph)
#permutation_tests(graph)