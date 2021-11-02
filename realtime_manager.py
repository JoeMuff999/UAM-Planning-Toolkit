import graph_manager as gm 
import reworked_graph as rg
import copy
import time

TAU = 0
TIME_STEP = 0
configured = False

DEFAULT_EMPTY_STATE = rg.State((),(),{"0" : 3, "1" : 3}) # causes port states to "reset", empties out all previously landed aircraft

def configure_realtime(tau=0, override_default_empty_state=None):
    global TAU
    global configured
    global DEFAULT_EMPTY_STATE
    global TIME_STEP
    TAU = tau
    TIME_STEP = 0

    if(override_default_empty_state is None):
        override_default_empty_state = rg.State((),(),{"0" : 3, "1" : 3})
    DEFAULT_EMPTY_STATE = copy.deepcopy(override_default_empty_state)
    configured = True
    assert("VALID" in DEFAULT_EMPTY_STATE.labels)
    

"""
Inputs:
    -system of n towers
    -a list of incoming request dictionaries

Outputs:
    -timing information
    -cummulative system cost

To note:
    -currently not processing the total cost
    -default state is overriden in configuration

"""
def main_loop(initial_system, additional_requests, MAX_ALLOWED_REQUESTS=8, Purdue_Data_Output = None): #the MAX_ALLOWED_REQUESTS will cause problems for your non-purdue data set stuff, but we can cross that bridge later
    assert(configured) # force user to configure globals before running
    
    
    global TIME_STEP
    global TAU
    TIME_STEP = 0
    timing_info = []
    # minimizing the initial system using the request swapping algorithm
    minimized_system = copy.deepcopy(initial_system)
    # gm.run_minimizing_mvp(minimized_system) # removed request swapping algorithm
    # add it to the first state that is empty
    #obtain minimized traces
    minimized_traces = get_minimized_traces(minimized_system) # the initial plan for our agents. 
    # print("minimized_traces" + str(minimized_traces))
    completed_traces = [[] for i in range(len(minimized_traces))]
    sum_of_requests = 0
    TAU_graphs = [None for i in minimized_traces]
    additional_requests_culled = copy.deepcopy(additional_requests)
    #TODO: make it so that a vertihub does not have more than 8 requests inside of it at any point
    while not are_traces_empty(minimized_traces) or TIME_STEP < len(additional_requests): 
        start_time = time.perf_counter()   
        # NOTE: the "[{}]" check is needed because the purdue data input has a dictionary even if there are no additional requests
        if TIME_STEP < len(additional_requests) and additional_requests[TIME_STEP] != [] and additional_requests[TIME_STEP] != [{}]: # if there is an incoming request at this time step
            print('Current time step : ' + str(TIME_STEP) + '/' + str(len(additional_requests)))
            print('additional requests = ' + str(additional_requests[TIME_STEP]))
            #add to the preferred tower at the TAU state. 
            # print(additional_requests[TIME_STEP])
            assert(len(additional_requests[TIME_STEP]) <= 1)
            #NOTE: this will likely only ever iterate once, but thats okay. just don't confuse yourself
            #there is only ONE request_dict per additional_requests[TIME_STEP]
            # iterate over all of the towers
            for requested_tower_index in range(len(TAU_graphs)):
                requested_tower = minimized_traces[requested_tower_index]

                # check if requested tower has an existing TAU state, else its an empty state
                was_big_enough = False
                TAU_state = None
                if len(requested_tower) > TAU:
                    TAU_state = copy.deepcopy(requested_tower[TAU]) 
                    TAU_state.labels = TAU_state.generate_labels()
                    was_big_enough = True
                else:
                    # fill_with_empty_states(requested_tower) 
                    TAU_state = copy.deepcopy(DEFAULT_EMPTY_STATE)
                
                if additional_requests[TIME_STEP][0].get(requested_tower_index,None) != None:   # the None is what get will return if it does not find the first parameter in its list of keys (requested_tower_index)         
                    # print("additional requests for tower " + str(requested_tower_index) + " = " + str(additional_requests[TIME_STEP][0][requested_tower_index]))
                    # make a separate method for this code
                    if was_big_enough:
                        for index, request in enumerate(additional_requests[TIME_STEP][0][requested_tower_index]):
                            # print (additional_requests[TIME_STEP][0][requested_tower_index])
                            requested_port = request[0]
                            adjusted_expiration_time = request[1] - TAU 
                            TAU_state.request_vector = list(TAU_state.request_vector)
                            TAU_state.time_vector = list(TAU_state.time_vector)
                            #NOTE: This is where we cap the number of requests in a tower state
                            if len(TAU_state.request_vector) < MAX_ALLOWED_REQUESTS:
                                TAU_state.request_vector.append(requested_port)
                                TAU_state.time_vector.append(adjusted_expiration_time)
                                if Purdue_Data_Output != None:
                                    Purdue_Data_Output.max_requests = max(Purdue_Data_Output.max_requests, len(TAU_state.request_vector))

                            else:
                                additional_requests_culled[TIME_STEP][0][requested_tower_index].remove(request) # NOTE: an issue here is that two requests may be the exact same (same port, same expiration), so if we had requests = [(0,0), (1,1), (0,0)], and we were rejecting number 3, this would actually make the list [(1,1), (0,0)] instead of [(0,0), (1,1)]. This could definitely have an effect, although I'm not sure how serious the impact will be
                                if Purdue_Data_Output != None:
                                    Purdue_Data_Output.num_denied_requests += 1
                                print("DENIED REQUEST") 
                    else:
                        for index, request in enumerate(additional_requests[TIME_STEP][0][requested_tower_index]):
                            requested_port = request[0]
                            # add the requests to the first empty state 
                            # for this case, lets say there is a tower that has an empty last state in the sense that it its last state
                            # is a "finish" state. this check here will build off of that state. the other case if its an empty tower, which
                            # then of course we just use the empty state.
                            #NOTE: The +1 is because the requested_tower will always have an empty state, which means that the len(requested_tower) will always be at least one, even if its empty
                            if TAU == 0:
                                adjusted_expiration_time = request[1] - len(requested_tower)
                            else:
                                adjusted_expiration_time = request[1] - len(requested_tower) +1

                            # print("last request_vector = " + str(len(requested_tower[len(requested_tower)-1].request_vector)))
                            # only check the final state because it is the only one that can actually be empty, we also check if index == 0 b/c we only want to do this for the first request at this time step. if we do it for all of them, we continally reset our TAU state
                            # if index == 0 and len(requested_tower[len(requested_tower)-1].request_vector) == 0:
                            #     TAU_state = copy.deepcopy(requested_tower[len(requested_tower)-1])
                                # adjusted_expiration_time = request[1] - len(requested_tower) + 2 #NOTE: figure out what this "+2" was for...
                            TAU_state.request_vector = list(TAU_state.request_vector)
                            TAU_state.time_vector = list(TAU_state.time_vector)
                            #NOTE: This is where we cap the number of requests in a tower state
                            if len(TAU_state.request_vector) < MAX_ALLOWED_REQUESTS:
                                TAU_state.request_vector.append(requested_port)
                                TAU_state.time_vector.append(adjusted_expiration_time)
                                if Purdue_Data_Output != None:
                                    Purdue_Data_Output.max_requests = max(Purdue_Data_Output.max_requests, len(TAU_state.request_vector))
                            else:
                                if Purdue_Data_Output != None:
                                    Purdue_Data_Output.num_denied_requests += 1

                                additional_requests_culled[TIME_STEP][0][requested_tower_index].remove(request)
                                print("DENIED REQUEST")
                
                # so if we add to the first empty state, then we need to pad it with empty states.
                # yes, for record keeping. if there isn't and additional request, our tower will have no states!
                # NOTE: graph construction happens here
                TAU_graph = rg.ReworkedGraph(
                    TAU_state._port_dict, 
                    1, 
                    TAU_state.request_vector, 
                    TAU_state.time_vector
                )
                TAU_graphs[requested_tower_index] = TAU_graph #NOTE: heuristic graphs are set here
            #NOTE: at this point, all towers should have a corresponding TAU_graph. Now, we just need to do the passing heuristic for TAU states, and then record the pre-TAU states
            gm.run_minimizing_mvp(TAU_graphs) # Request passing heuristic, modifies TAU_graphs by reference
            gm.reset_globals()
            #TODO: now, we need to set the minimized traces for each tower:
            for requested_tower_index in range(len(TAU_graphs)):
                # NOTE: mvp happens here
                requested_tower = minimized_traces[requested_tower_index]
                TAU_trace = gm.generate_trace(TAU_graphs[requested_tower_index], override=True)[1]
                if len(requested_tower) > TAU:
                    minimized_traces[requested_tower_index] = requested_tower[:TAU] + TAU_trace
                else:
                    minimized_traces[requested_tower_index] = requested_tower[:-1] + TAU_trace

            #TODO: at the moment, one clear issue is that the expiration bug still exists.

            


                    # if was_big_enough:
                    #     # assert(len(requested_tower[0].request_vector) != 0 or TAU == 0)
                    #     for time_index, state in enumerate(requested_tower[:TAU]):
                    #         for index, request in enumerate(request_dict[requested_tower_index]):
                    #             requested_port = request[0]
                    #             adjusted_expiration_time = request[1] - time_index
                    #             state.request_vector = list(state.request_vector)
                    #             state.time_vector = list(state.time_vector)
                    #             state.request_vector.append(requested_port)
                    #             state.time_vector.append(adjusted_expiration_time) 
                    #             state.request_vector = tuple(state.request_vector)
                    #             state.time_vector = tuple(state.time_vector)
                    #             state.labels = state.generate_labels()

                    #     minimized_traces[requested_tower_index] = requested_tower[:TAU] + TAU_trace
                    # else:
                    #     # if(len(requested_tower) > 0):
                    #         # print(TAU)
                    #         # assert(len(requested_tower[0].request_vector) != 0 )
                    #     for time_index, state in enumerate(requested_tower[:-1]):
                    #         for index, request in enumerate(request_dict[requested_tower_index]):
                    #             requested_port = request[0]
                    #             adjusted_expiration_time = request[1] - time_index
                    #             state.request_vector = list(state.request_vector)
                    #             state.time_vector = list(state.time_vector)
                    #             state.request_vector.append(requested_port)
                    #             state.time_vector.append(adjusted_expiration_time) 
                    #             state.request_vector = tuple(state.request_vector)
                    #             state.time_vector = tuple(state.time_vector)
                    #             state.labels = state.generate_labels()
                    #     minimized_traces[requested_tower_index] = requested_tower[:-1] + TAU_trace

                # print("Full trace including new requests = " + str(minimized_traces[requested_tower_index]))
            # current_num_requests = 0
            # for trace in minimized_traces:
            #     if(len(trace) > 0):
            #         current_num_requests += len(trace[0].request_vector)
            # num_reqs = 0
            # for key in additional_requests[TIME_STEP][0]:
            #     print(additional_requests[TIME_STEP][0][key])
            #     num_reqs += len(additional_requests[TIME_STEP][0][key])

            # print (current_num_requests)
            # print (sum_of_requests)
            # print (num_reqs)
            # print (TIME_STEP)
            # if sum_of_requests == 0:

            #     assert(current_num_requests == sum_of_requests + num_reqs)
            # else:

            #     assert(current_num_requests == sum_of_requests + num_reqs -1)
            # sum_of_requests = current_num_requests
            end_time = time.perf_counter()
        else:
            end_time = start_time


        # what about the case when there are no more incoming requests for a while. then, we clearly won't have enough empty states
        # in fact, when will this even be called again? this is fine actually
        # what about the case of padding after the tau state? do we need padding if it adds the empty state anyways.
        record_completed_state(minimized_traces, completed_traces)


        # record the time it took to replan around this round of incoming requests
        time_per_time_step = end_time - start_time
        timing_info.append(time_per_time_step)

        TIME_STEP += 1
        # print("completed traces = " + str(completed_traces) + "  time_step = " + str(TIME_STEP))
    
    for trace in minimized_traces:
        assert(len(trace) == 0)
        
    if Purdue_Data_Output != None:
        Purdue_Data_Output.additional_requests_culled = additional_requests_culled
    return completed_traces, timing_info
    # for index in range(len(minimized_traces)):
    #     for state_index, state in enumerate(minimized_traces[index]):
    #         assert(completed_traces[index][state_index] == state)

def get_mvp_output(completed_traces):
    finish_label = "REALTIME_FINISH"
    # apply label to final state of all towers in the trace
    for tower in completed_traces:
        state = tower[len(tower)-1]
        prev_labels = list(copy.copy(state.labels))
        prev_labels.append("REALTIME_FINISH")
        tower[len(tower)-1].labels = tuple(prev_labels)
    
    mvp_output_per_tower = []    
    for tower in completed_traces:
        # append cummulative cost to array
        mvp_output_per_tower.append(copy.deepcopy(get_realtime_cost(tower, finish_label=finish_label)))
        # print()
        
    return mvp_output_per_tower



# for any trace that does not have a valid state at index TAU, fill up with empty states
def fill_with_empty_states(trace_to_fill):
    global TAU
    for i in range(TAU + 1 - len(trace_to_fill)): 
        trace_to_fill.append(DEFAULT_EMPTY_STATE)
    assert(trace_to_fill[TAU] == DEFAULT_EMPTY_STATE)

#checks if all towers are empty
def are_traces_empty(minimized_traces):
    for trace in minimized_traces:
        if len(trace) > 0:
            return False
    return True

def record_completed_state(minimized_traces, completed_traces):
    # complete step at front of trace
    for index, trace in enumerate(minimized_traces):
        if len(trace) == 0: # ie: no more states, is empty system/goal state
            completed_traces[index].append(copy.deepcopy(DEFAULT_EMPTY_STATE))
        else:
            # print("recorded state " + str(minimized_traces[index][0]) + " for tower " + str(index))
            completed_traces[index].append(minimized_traces[index][0])
            del minimized_traces[index][0]


"""
Inputs:
    -a list of n towers
Outputs:
    -a list of n traces
"""
def get_minimized_traces(system):
    traces = []
    for tower in system:
        traces.append(gm.generate_trace(tower, override=True)[1]) # 1 is the index for the state path (trace)
    return traces
    

"""
Takes in:
    -a system of N towers that is not minimized
Process:
    -minimizes the system using graph_managers request passing heuristic
Outputs:
    -the minimized system
"""
def initialize_system(initial_system):
    gm.run_minimizing_mvp(initial_system)



'''
rewriting trace generation function with realtime spec
'''
from tulip.transys import WeightedKripkeStructure as WKS
from tulip.transys.automata import WeightedFiniteStateAutomaton as WFA
from tulip.spec.prioritized_safety import PrioritizedSpecification
from tulip.mvp import solve as solve_mvp
from tulip.transys.mathset import PowerSet


def get_realtime_cost(trace, finish_label="FINISH"):

    # NOTE: crazy thing.. so you have repeat states, and then tulip will treat them as the same state, even if they are not... (such as empty state). thus, you need to give each state a unique id
    for index,s in enumerate(trace):
        prev_labels = list(s.labels)
        prev_labels.append(str(index))        
        s.labels = tuple(prev_labels)

    ts = WKS()
    ts.states.add_from(trace)
    ts.states.initial.add(trace[0])

    for index in range(1, len(trace)):
        ts.transitions.add(trace[index-1], trace[index], {"cost" : 1})

    ts.atomic_propositions.add("VALID")
    ts.atomic_propositions.add("WRONG_PORT")
    ts.atomic_propositions.add("OVERFLOWED_PORT")
    ts.atomic_propositions.add("FINISH")
    ts.atomic_propositions.add(finish_label)
    # NOTE: SEE ABOVE :)

    for s in trace:
        prev_labels = list(s.labels)
        del prev_labels[len(s.labels)-1]      
        ts.states[s]["ap"] = set(prev_labels)

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

    (cost, state_path, product_path, wpa) = solve_mvp(ts, finish_label, spec) 
    #NOTE: manually tagging on extra cost if a request was originally intended for a different tower. 
    #trust me, this works b/c the swapping algorithm is the one who checks the costs 
    #(if you are wondering why you don't add these costs before synthesis)
    cost._value[1] = 0 #ignore the port costs, replace it with the wrong_tower costs
    for req in trace[0].request_vector:
        if req == "wrong_tower":
            cost._value[1] += 1
    return (cost, state_path, product_path, wpa)