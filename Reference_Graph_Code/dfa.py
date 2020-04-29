import graph

class Dfa(object):

    def __init__(self, states, accepting, alphabet, transitions=[]):
        self.states = states
        self.accepting = accepting
        self.alphabet = alphabet
        self.transitions = transitions

    def spec_for_TA(self):
        #source of confusion
        spec = {0: {"TA":0, "":1},
                1: {"TA":1, "":1}}; #if expired, can't de-expire




#states, accepting, alphabet, transitions=[]
test = graph.TransitionSystem(3, 5, 2, [1,2], [2,2])
emptyPortState = [0] * len(test.initRequests) #use for generating the base state (full init request list and all zero port state list)
baseState = test.State(test.initRequests, emptyPortState)
test.states.append(baseState)
test.generate_states(baseState, test.initRequests)
dfaTest = Dfa([0,1],[0], ["TA", ""], test.edges)


