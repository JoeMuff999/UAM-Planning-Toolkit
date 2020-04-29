import graph
import copy
from tulip.transys import WeightedKripkeStructure as WKS
from tulip.transys.automata import WeightedFiniteStateAutomaton as WFA
from tulip.spec.prioritized_safety import PrioritizedSpecification
from tulip.transys.compositions import synchronous_parallel
from tulip.transys.mathset import PowerSet
from tulip.mvp import solve as solve_mvp


test = graph.TransitionSystem(3, 5, 2, [1,2], [2,2])
emptyPortState = [0] * len(test.initRequests) #use for generating the base state (full init request list and all zero port state list)
baseState = test.State(copy.deepcopy(test.initRequests), emptyPortState)
test.states.add(baseState)
test.generate_states(baseState, copy.deepcopy(test.initRequests))
setOfStates = set(test.states)
setOfTransitions = set(test.edges)
ts = WKS()
ts.states.add_from(setOfStates)
ts.states.initial.add(baseState)

for transition in setOfTransitions:
    ts.transitions.add(
        transition.prevState, transition.nextState, 1
    )
ts.atomic_propositions.add("VALID")
ts.atomic_propositions.add("SAT")

for s in setOfStates:
    ts.states[s]["ap"] = set(s.labels)

# ts = synchronous_parallel([ts])

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
print("Optimal cost: {}".format(cost))
print("State path: {}".format(state_path))
print("Product path: {}".format(product_path))
#wpa.plot()