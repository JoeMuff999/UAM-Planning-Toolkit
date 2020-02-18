import copy


class TransitionSystem(object):

    def __init__(self, numPorts=0, portCapacity=0, acceptedRequestsPerStep=0, requestVector=None, allowedTimePerRequest=0):

        self.acceptedRequestsPerStep = acceptedRequestsPerStep #same as below
        self.allowedTimePerRequest = allowedTimePerRequest #keep as instance because could prove useful

        self.initRequests = self.generate_requests_from_integer_vector(requestVector)
        self.ports = self.generate_ports_from_init(numPorts, portCapacity)
        # print(self.ports)
        # print(self.initRequests)
        #print([str(r) for r in self.initRequests])
        self.traces = [[]]

    def generate_requests_from_integer_vector(self, requestVector):
        tmpList = []
        for i in requestVector:
            tmp = Request(i, self.allowedTimePerRequest, 0)
            tmpList.append(tmp)
        return tmpList

    def generate_ports_from_init(self, portAmt, portCap):
        tmpList = []
        for i in range(portAmt):
            # tmp = Port(0, portCap)
            # tmpList.append(tmp)
            tmp = 0
            tmpList.append(tmp)
        return tmpList

    def generate_states(self, remainingRequests, currentTrace=[], currentPortStates=[]):
        if(len(remainingRequests) == 0):
            print("curr trace :: " + str(currentTrace))
            self.traces.append(currentTrace)
        else:
            for i in range(len(remainingRequests)):

                tmp = remainingRequests[i]
                currentPortStates[remainingRequests[i].portNumber - 1] += 1  # iterating port number
                tmpState = self.State(copy.deepcopy(remainingRequests), copy.deepcopy(currentPortStates))
                tmpState.iterate_all_requests(i)# iterating all requests
                currentTrace.append(tmpState)
                #print(currentPortStates)


                del remainingRequests[i]

                self.generate_states(remainingRequests, currentTrace, currentPortStates) #backtrack
                #print("rr:: " + str(remainingRequests))
                remainingRequests.insert(i, tmp)
                currentPortStates[remainingRequests[i].portNumber - 1] -= 1
                currentTrace.remove(tmpState)

    #def add_edge(self, Request, currState, nextState):


    class State(object):
        def __init__(self, currentRequests=[], currentPortStates=[]):
            self.currRequests = currentRequests
            self.currPortStates = currentPortStates
            self.adjacentStates = []

        def iterate_all_requests(self, ignore):
            for i in range(len(self.currRequests)):
                if(i != ignore):
                    self.currRequests[i].numStepsPassed+=1

        def print_requests(self):
            for r in self.currRequests:
                print(r)

        def __str__(self):
            return "State currently has requests :: " + str(self.currRequests) + " And currently has port states of :: " + str(self.currPortStates) + "  \n"
        def __repr__(self):
            return self.__str__()


    class Edge(object):
        def __init__(self, requestTaken=None, prevState=None, nextState=None):
            self.requestTaken = requestTaken
            self.prevState = prevState
            self.nextState = nextState


class Request(object):
    def __init__(self, portNumber, timeAllowed, numStepsPassed): #allow for more freedom in defining requests (not just limited to integer vector)
        self.portNumber = portNumber
        self.timeAllowed = timeAllowed
        self.numStepsPassed = numStepsPassed

    def __str__(self):
        return "Request port :: " + str(self.portNumber) + ", Allowed time of :: " + str(self.timeAllowed) + ", Current Steps Passed:: "+ str(self.numStepsPassed) + "\n"

    def __repr__(self):
        return self.__str__()



class Port(object):
    def __init__(self, aircraftInPorts, maxAircraftInPorts=None):
        self.aircraftInPorts = aircraftInPorts
        #won't use this for now, might be redundant
        self.maxAircraftInPorts = maxAircraftInPorts

#testing values
#numPorts=0, portCapacity=0, acceptedRequestsPerStep=0, requestVector=None, allowedTimePerRequest=0 -> for init TS
graph = TransitionSystem(3, 5, 1, [1,2,3], 2)
graph.generate_states(graph.initRequests, [], graph.ports)
print(graph.traces)

