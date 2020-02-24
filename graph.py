import copy


class TransitionSystem(object):

    def __init__(self, numPorts=0, portCapacity=0, acceptedRequestsPerStep=0, requestVector=None, allowedTimePerRequestVector=None):

        self.acceptedRequestsPerStep = acceptedRequestsPerStep #same as below
        self.allowedTimePerRequestVector = allowedTimePerRequestVector #keep as instance because could prove useful

        self.initRequests = self.generate_requests_from_integer_vector(requestVector)
        self.ports = self.generate_ports_from_init(numPorts, portCapacity)


        # print(self.ports)
        # print(self.initRequests)
        #print([str(r) for r in self.initRequests])
        self.traces = [[]]
        self.states = []
        self.edges = []

    def generate_requests_from_integer_vector(self, requestVector):
        tmpList = []
        counter = 0
        for reqPortNumber in requestVector:
            tmp = Request(reqPortNumber, self.allowedTimePerRequestVector[counter], 0)
            tmpList.append(tmp)
            counter+=1
        return tmpList

    def generate_ports_from_init(self, portAmt, portCap):
        tmpList = []
        for i in range(portAmt):
            # tmp = Port(0, portCap)
            # tmpList.append(tmp)
            tmp = 0
            tmpList.append(tmp)
        return tmpList

    # def generate_states(self, remainingRequests, currentTrace=[], currentPortStates=[]):
    #     if(len(remainingRequests) == 0):
    #         print("curr trace :: " + str(currentTrace))
    #         self.traces.append(currentTrace)
    #     else:
    #         for i in range(len(remainingRequests)):
    #
    #             tmp = remainingRequests[i]
    #             currentPortStates[remainingRequests[i].portNumber - 1] += 1  # iterating port number
    #             tmpState = self.State(copy.deepcopy(remainingRequests), copy.deepcopy(currentPortStates))
    #             tmpState.iterate_all_requests(i)# iterating all requests
    #             currentTrace.append(tmpState)
    #             #print(currentPortStates)
    #
    #
    #             del remainingRequests[i]
    #
    #             self.generate_states(remainingRequests, currentTrace, currentPortStates) #backtrack
    #             #print("rr:: " + str(remainingRequests))
    #             remainingRequests.insert(i, tmp)
    #             currentPortStates[remainingRequests[i].portNumber - 1] -= 1
    #             currentTrace.remove(tmpState)

    def check_if_state_is_duplicate(self, stateToCheck):
        for state in self.states:
            if stateToCheck.check_equal(state):
                return state
        return None

    def generate_states(self, previousState, remainingRequests):
        if(len(remainingRequests) == 0):
            #do nothing
            print()
        else:
            for i in range(len(remainingRequests)):
                #made the choice
                copySelectedRequest = Request(remainingRequests[i].portNumber, remainingRequests[i].stepsAllowed, remainingRequests[i].numStepsPassed)
                del remainingRequests[i]

                newState = self.State(copy.deepcopy(remainingRequests), copy.deepcopy(previousState.currPortStates))
                newState.iterate_all_requests()
                newState.update_port_states(copySelectedRequest.portNumber)
                #check for copy
                tmp = self.check_if_state_is_duplicate(newState)
                if tmp != None:
                    newEdge = self.Edge(previousState, copySelectedRequest, tmp)
                    print("I AM A COPY :: ")
                    print(tmp)
                else:
                    self.states.append(newState)
                    newEdge = self.Edge(previousState, copySelectedRequest, newState)

                self.edges.append(newEdge)

                #take choice
                self.generate_states(newState, remainingRequests)

                #undo choice
                remainingRequests.insert(i, copySelectedRequest)




    #def add_edge(self, Request, currState, nextState):


    class State(object):
        def __init__(self, currentRequests=[], currentPortStates=[]):
            self.currRequests = currentRequests
            self.currPortStates = currentPortStates
            self.adjacentStates = []

        def iterate_all_requests(self):
            for i in range(len(self.currRequests)):
                self.currRequests[i].numStepsPassed+=1

        def update_port_states(self, portToIncrease):
            self.currPortStates[portToIncrease-1] += 1

        def print_requests(self):
            for r in self.currRequests:
                print(r)

        def check_equal(self, other):
            if len(self.currRequests) != len(other.currRequests) or len(self.currPortStates) != len(other.currPortStates): #check length of lists first
                return False
            for i in range(len(self.currRequests)): #if same length of requests, check if the request states themselves are the same
                if not self.currRequests[i].check_req_equal(other.currRequests[i]):
                    return False
            for i in range(len(self.currPortStates)): #if matching requests, check if matching port states (pretty likely)
                if self.currPortStates[i] != other.currPortStates[i]:
                    return False
            return True

        def __str__(self):
            return "State currently has requests :: " + str(self.currRequests) + " And currently has port states of :: " + str(self.currPortStates) + "  \n"
        def __repr__(self):
            return self.__str__()


    class Edge(object):
        def __init__(self, prevState=None, requestTaken=None, nextState=None):
            self.prevState = prevState
            self.requestTaken = requestTaken
            self.nextState = nextState

        def __str__(self):
            return "Edge...Previous State :: " + str(self.prevState) + ", Request Taken:: " + str(
                self.requestTaken) + ", Next State:: " + str(self.nextState) + "\n"

        def __repr__(self):
            return self.__str__()

class Request(object):
    def __init__(self, portNumber, maxStepsAllowed, numStepsPassed): #allow for more freedom in defining requests (not just limited to integer vector)
        self.portNumber = portNumber
        self.stepsAllowed = maxStepsAllowed
        self.numStepsPassed = numStepsPassed

    def check_req_equal(self, other):
        return self.portNumber == other.portNumber and self.stepsAllowed == other.stepsAllowed and self.numStepsPassed == other.numStepsPassed

    def __str__(self):
        return "[P#: " + str(self.portNumber) + ", S#: " + str(self.numStepsPassed) + ", SMAX: " + str(self.stepsAllowed) + "]"
        #return "Request port :: " + str(self.portNumber) + ", Allowed time of :: " + str(self.timeAllowed) + ", Current Steps Passed:: "+ str(self.numStepsPassed) + "\n"

    def __repr__(self):
        return self.__str__()



class Port(object):
    def __init__(self, aircraftInPorts, maxAircraftInPorts=None):
        self.aircraftInPorts = aircraftInPorts
        #won't use this for now, might be redundant
        self.maxAircraftInPorts = maxAircraftInPorts

#testing values
#numPorts=0, portCapacity=0, acceptedRequestsPerStep=0, requestVector=None, allowedTimePerRequest=0 -> for init TS
graph = TransitionSystem(3, 5, 1, [1,2,3], [0,1,2])
#graph.generate_states(graph.initRequests, [], graph.ports)
emptyPortState = [0] * len(graph.initRequests) #use for generating the base state (full init request list and all zero port state list)
baseState = graph.State(graph.initRequests, emptyPortState)
graph.generate_states(baseState, graph.initRequests)
print(graph.states)

