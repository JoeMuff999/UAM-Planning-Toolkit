import graph_manager as gm 
import reworked_graph as rg
import copy

TAU = 0
TIME_STEP = 0
configured = False

DEFAULT_EMPTY_STATE = rg.State((),(),{"0" : 3, "1" : 3}) # causes port states to "reset", empties out all previously landed aircraft

def configure_realtime(tau=0):
    global TAU
    global configured
    TAU = tau
    configured = True
    assert("VALID" in DEFAULT_EMPTY_STATE.labels)
    

"""
Inputs:
    -system of n towers

Outputs:

"""
def main_loop(initial_system, additional_requests):
    assert(configured) # force user to configure globals before running
    global TIME_STEP
    global TAU

    # minimizing the initial system using the request swapping algorithm
    minimized_system = copy.deepcopy(initial_system)
    gm.run_minimizing_mvp(minimized_system)

    #obtain minimized traces
    minimized_traces = get_minimized_traces(minimized_system) # the initial plan for our agents. 
    print("minimized_traces" + str(minimized_traces))
    completed_traces = [[] for i in range(len(minimized_traces))]
    while not are_traces_empty(minimized_traces) or TIME_STEP < len(additional_requests):        
        if TIME_STEP < len(additional_requests) and additional_requests[TIME_STEP] != []: # if there is an incoming request at this time step
            # print('additional requests = ' + str(additional_requests[TIME_STEP]))
            #add to the preferred tower at the TAU state. 
            for request_dict in additional_requests[TIME_STEP]:
                for requested_tower_index in request_dict:
                    requested_tower = minimized_traces[requested_tower_index]
                    # check if requested tower has an existing TAU state, else its an empty state
                    if len(requested_tower) > TAU:
                        TAU_state = copy.deepcopy(requested_tower[TAU]) 
                    else:
                        fill_with_empty_states(requested_tower) 
                        TAU_state = copy.deepcopy(DEFAULT_EMPTY_STATE)
                    print("additional requests for this tower = " + str(request_dict[requested_tower_index]))
                    for request in request_dict[requested_tower_index]:
                        requested_port = request[0]
                        adjusted_expiration_time = request[1] - TAU 
                        TAU_state.request_vector = list(TAU_state.request_vector)
                        TAU_state.time_vector = list(TAU_state.time_vector)
                        TAU_state.request_vector.append(requested_port)
                        TAU_state.time_vector.append(adjusted_expiration_time) 

                    TAU_graph = rg.ReworkedGraph(
                        TAU_state._port_dict, 
                        1, 
                        TAU_state.request_vector, 
                        TAU_state.time_vector
                    )

                    TAU_trace = gm.generate_trace(TAU_graph)[1]
                    print("Tau trace = " + str(TAU_trace))
                    minimized_traces[requested_tower_index] = requested_tower[:TAU] + TAU_trace
                    print("Full trace including new requests = " + str(minimized_traces[requested_tower_index]))

        record_completed_state(minimized_traces, completed_traces)

        TIME_STEP += 1
        print("completed traces = " + str(completed_traces))

    for trace in minimized_traces:
        assert(len(trace) == 0)
    # for index in range(len(minimized_traces)):
    #     for state_index, state in enumerate(minimized_traces[index]):
    #         assert(completed_traces[index][state_index] == state)

# for any trace that does not have a valid state at index trace, fill up with empty states
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
            completed_traces[index].append(minimized_traces[index][0])
            del minimized_traces[index][0]
    
#     #lock the next TAU actions 
#     locked_traces = []
#     for trace in minimized_traces:
#         # if TAU is greater than the trace, copy the whole thing, create empty states for it
#         # if we have TAU=3, need 4 corresponding states, therefore, len(trace) must be greater than TAU
#         trace_length = len(trace)
#         if trace_length <= TAU:
#             assert(trace_length != 1)
#             #setup the "empty state" which we will use to fill the remainder of the trace until TAU
#             empty_state = None
            
#             if trace_length == 0: # means no port dict to copy over
#                 empty_state = copy.deepcopy(DEFAULT_EMPTY_STATE)
#             else:
#                 final_state_port_dict = copy.deepcopy(trace[trace_length-1]._port_dict)
#                 empty_state = rg.State((),(),final_state_port_dict)
# `           #we need TAU+1 states, or TAU +1 - len(trace) states extra
#             for i in range(TAU + 1 - trace_length): 
#                 trace.append(empty_state)
#         #now that our traces are properly sized, lets "lock" them
#         locked_traces.append(copy.deepcopy(trace[:(TAU+1)])) # copies from 0 to stop - 1, so from 0 to TAU

        
    
            




# def stringify_system()

"""
Inputs:
    -a list of n towers
Outputs:
    -a list of n traces
"""
def get_minimized_traces(system):
    traces = []
    for tower in system:
        traces.append(gm.generate_trace(tower)[1]) # 1 is the index for the state path (trace)
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

