import copy
from itertools import chain, combinations
import itertools

class TransitionSystem(object):

    def __init__(self, numPorts=0, portCapacity=0, acceptedRequestsPerStep=0, requestVector=None, allowedTimePerRequestVector=None):

        self.acceptedRequestsPerStep = acceptedRequestsPerStep #same as below
        self.allowedTimePerRequestVector = allowedTimePerRequestVector #keep as instance because could prove useful

        self.initRequests = self.generate_requests_from_integer_vector(requestVector)
        self.ports = self.generate_ports_from_init(numPorts, portCapacity)

        self.recursiveOptionList = [i for i in range(acceptedRequestsPerStep)]
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
            tmp = Request(reqPortNumber, self.allowedTimePerRequestVector[counter])
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




            #old singular version
            # for i in range(len(remainingRequests)):
            #     #made the choice
            #     self.iterate_all_requests(remainingRequests, i)
            #     copySelectedRequest = Request(remainingRequests[i].portNumber, remainingRequests[i].initSteps, remainingRequests[i].numStepsLeft)
            #     del remainingRequests[i]
            #
            #     newState = self.State(copy.deepcopy(remainingRequests), copy.deepcopy(previousState.currPortStates))
            #     #newState.iterate_all_requests() --> replaced by iterating the remainingRequests. change made because could only decrement at max once since deep copying the remainingRequests and prevState.currRequests
            #     newState.update_port_states(copySelectedRequest.portNumber)
            #     #check for copy
            #     tmp = self.check_if_state_is_duplicate(newState)
            #     if tmp != None:
            #         newEdge = self.Edge(previousState, copySelectedRequest, tmp)
            #     else:
            #         self.states.append(newState)
            #         newEdge = self.Edge(previousState, copySelectedRequest, newState)
            #
            #     self.edges.append(newEdge)
            #
            #     #take choice
            #     self.generate_states(newState, remainingRequests)
            #
            #     #undo choice
            #     remainingRequests.insert(i, copySelectedRequest)
            #     self.undo_iteration_of_requests(remainingRequests, i)

    def generate_states(self, previousState, remainingRequests):
        if(len(remainingRequests) == 0 or self.request_expired(remainingRequests)):
            return
        else:
            choices = self.generate_choices(len(remainingRequests)) #power set
            for choice in choices: #choices = [[]], choice = [] (ex: [1,2])
                copiedRequests = []
                copySelectedRequest = None
                self.iterate_all_requests(remainingRequests, choice)
                if len(choice) != 0:
                    copiedRequests = [None] * choice[len(choice)-1] #access largest element, use this element as the size of indexing. (ex: if choice : [0,2], then copiedRequests should be [0, None, 2] to keep aligned
                    offset = 0
                    for i in choice: #works with none?
                        indexForRR = i - offset
                        copySelectedRequest = Request(remainingRequests[indexForRR].portNumber, remainingRequests[indexForRR].initSteps, remainingRequests[indexForRR].numStepsLeft)
                        copiedRequests.insert(i, copySelectedRequest)
                        del remainingRequests[indexForRR]
                        offset += 1 #use this offset because since we are using indexes, we need to shift
                #meat
                newState = self.State(copy.deepcopy(remainingRequests), copy.deepcopy(previousState.currPortStates), copy.deepcopy(previousState.actionsLeadingToState))
                actionsLeadingToState = self.generate_port_list(copiedRequests)
                newState.actionsLeadingToState[0].append(actionsLeadingToState)
                #newState.iterate_all_requests() --> replaced by iterating the remainingRequests. change made because could only decrement at max once since deep copying the remainingRequests and prevState.currRequests
                newState.update_port_states(copiedRequests)
                #check for copy
                tmp = self.check_if_state_is_duplicate(newState)
                if tmp != None:
                    tmp.add_action_list(newState.actionsLeadingToState[0])
                    newEdge = self.Edge(previousState, copySelectedRequest, tmp)
                else:
                    self.states.append(newState)
                    newEdge = self.Edge(previousState, copySelectedRequest, newState)

                self.edges.append(newEdge)

                #take choice
                self.generate_states(newState, remainingRequests)

                # undo choice
                for i in range(len(copiedRequests)):
                    req = copiedRequests[i]
                    if req is not None:
                        remainingRequests.insert(i, req)
                self.undo_iteration_of_requests(remainingRequests, choice)

    #generates choices for the recursive backtracking
    def generate_choices(self, numRequests): #combinations up to length acceptedRequestPerStep
        baseList = [i for i in range(numRequests)]
        listToReturn = []
        for i in range(1, self.acceptedRequestsPerStep+1): #TODO remove the 1 to include case where you dont choose a request
            tmp = combinations(baseList, i)
            listToReturn.extend(tmp)
        return listToReturn

    #generates the list of ports used per the given actions (just for printing purposes) its the A's:: part when printing states
    def generate_port_list(self, listOfRequests):
        listToReturn = []
        for req in listOfRequests:
            if req is not None:
                listToReturn.append(req.portNumber)
        return listToReturn
    #checks if a request in the given list has a request with numStepsLeft < 0
    def request_expired(self, listOfRequests):
        for req in listOfRequests:
            if req.is_expired():
                return True
        return False
    #decreases the numStepsLeft for all requests in 1st param except for those that are being removed which are in 2nd param
    def iterate_all_requests(self, listOfRequests, reqListIndexToIgnore):
        for i in range(len(listOfRequests)):
            if i not in reqListIndexToIgnore:
                listOfRequests[i].numStepsLeft -= 1
    #undos what the above function does
    def undo_iteration_of_requests(self, listOfRequests, reqListIndexToIgnore):
        for i in range(len(listOfRequests)):
            if i not in reqListIndexToIgnore:
                listOfRequests[i].numStepsLeft += 1
    #runs through multiple sub level checks to see if a state is exactly the same as another
    def check_if_state_is_duplicate(self, stateToCheck):
        for state in self.states:
            if stateToCheck.check_equal(state):
                return state
        return None

    #class for representing States (nodes of graph)
    class State(object):
        def __init__(self, currentRequests=[], currentPortStates=[], actionsLeadingToState=[[]]):
            self.currRequests = currentRequests
            self.currPortStates = currentPortStates
            self.actionsLeadingToState = actionsLeadingToState

        #action list = actions that led to the current state, this adds another path/trace that was taken to this state to its internal list
        def add_action_list(self, listOfActions):
            self.actionsLeadingToState.append(listOfActions)

         #FIXME remove this in future, likely redundant
        def iterate_all_requests(self):
            for req in self.currRequests:
                req.numStepsLeft -= 1
                if(req.portNumber == 3):
                    print("AHHHH" + str(req.numStepsLeft))
                    print(self.currPortStates)

        #given the list of accepted/taken requests/actions, update this state's port states (ie: add 1 to a helipad being used)
        def update_port_states(self, listOfRequests):
            for req in listOfRequests:
                if req is not None:
                    self.currPortStates[req.portNumber-1] += 1
        #FIXME checks if any requests in this state are expired, likely useless
        def contains_expired_request(self):
            for req in self.currRequests:
                if req.numStepsLeft < 0:
                    return True
            return False
        #FIXME likely useless
        def print_requests(self):
            for r in self.currRequests:
                print(r)
        #large function that checks if this and other (states) are completely equal. Requires that their portStates and requestStates (including current time states for requests) to be 100% equal
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
            return "State currently has requests :: " + str(self.currRequests) + " And currently has port states of :: " + str(self.currPortStates) + " Possible Paths's:: " + str(self.actionsLeadingToState) + "  \n"
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
    def __init__(self, portNumber, maxStepsAllowed, numStepsLeft=None): #allow for more freedom in defining requests (not just limited to integer vector)
        self.portNumber = portNumber
        self.initSteps = maxStepsAllowed

        if numStepsLeft is None: #if numStepsLeft not provided
            self.numStepsLeft = maxStepsAllowed
        else:
            self.numStepsLeft = numStepsLeft

    def is_expired(self):
        return self.numStepsLeft < 0

    def check_req_equal(self, other):
        return self.portNumber == other.portNumber and self.initSteps == other.initSteps and self.numStepsLeft == other.numStepsLeft

    def __str__(self):
        return "[P#: " + str(self.portNumber) + ", SLEFT#: " + str(self.numStepsLeft) + ", SINIT: " + str(self.initSteps) + "]"
        #return "Request port :: " + str(self.portNumber) + ", Allowed time of :: " + str(self.timeAllowed) + ", Current Steps Passed:: "+ str(self.numStepsLeft) + "\n"

    def __repr__(self):
        return self.__str__()



class Port(object):
    def __init__(self, aircraftInPorts, maxAircraftInPorts=None):
        self.aircraftInPorts = aircraftInPorts
        #won't use this for now, might be redundant
        self.maxAircraftInPorts = maxAircraftInPorts

#testing values
#numPorts=0, portCapacity=0, acceptedRequestsPerStep=0, requestVector=None, allowedTimePerRequest=0 -> for init TS
graph = TransitionSystem(3, 5, 2, [1,2,1], [3,2,2])
#graph.generate_states(graph.initRequests, [], graph.ports)
emptyPortState = [0] * len(graph.initRequests) #use for generating the base state (full init request list and all zero port state list)
baseState = graph.State(graph.initRequests, emptyPortState)
graph.states.append(baseState)
graph.generate_states(baseState, graph.initRequests)
print(graph.states)

