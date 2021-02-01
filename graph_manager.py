'''
Author information:
Joey R. Muffoletto
University of Texas at Austin
Autonomous Systems Group
jrmuff@utexas.edu
'''

import reworked_graph
import copy
from tulip.transys import WeightedKripkeStructure as WKS
from tulip.transys.automata import WeightedFiniteStateAutomaton as WFA
from tulip.spec.prioritized_safety import PrioritizedSpecification
from tulip.transys.mathset import PowerSet
from tulip.mvp import solve as solve_mvp
import time

# TODO (just a note, but wanted to make it highlighted) :: you will encounter "same labeled transition warnings "from_state---[label]---> to_state"".
# TODO (note continued) :: This has to do with TuLiP encountering repeat transitions. It hasn't had an effect on logic thus far, so I wouldn't worry too much about it.
# TODO (note continued) :: If these prints are too annoying, you can comment out this line in "labeled_graphs.py" (line 1007) in the TuLiP package.
# TODO (note) :: there are many print statements in this file. This is helpful debug information.

synthesis_dictionary = dict()
worst_request_dictionary = dict()
system_timings = []
system_req_vector_size_per_tower = []

def get_optimal_trace_with_new_request(orig_trace, new_req):

    assert(type(new_req) == tuple)
    assert(type(orig_trace) == list)
    assert isinstance(orig_trace[0], reworked_graph.State)

    #give each possibility its own trace for now to simplify
    new_traces = list()
    for index in range(len(orig_trace)):
        new_traces.append(orig_trace)

    #get port with highest remaining capacity (can assume this would be the optimal state)
    final_state = new_traces[0][len(new_traces[0])-1]
    optimal_port_key = None
    highest_remaining_capacity = -999 # if anything is lower than this i lose
    for key in final_state._port_dict:
        if final_state[key] > highest_remaining_capacity:
            highest_remaining_capacity = final_state[key]
            optimal_port_key = key

    assert optimal_port_key is not None

    for index, trace in enumerate(new_traces):
        #get the copy of the state before the branch to use for the branched state
        copy_of_state_before_branch = copy.deepcopy(trace[index])

        # "take" new request
        # to all requests before index, add the new request
        for state in trace[:index+1]:
            assert isinstance(state, reworked_graph.State)
            new_req_vector = copy.copy(state.request_vector)
            new_time_vector = copy.copy(state.time_vector)
            new_req_vector.append(new_req[0])
            new_time_vector.append(new_req[1])
            #safely edit state by creating a whole new one (state should be IMMUTABLE!)
            state = reworked_graph.State(
                new_req_vector,
                new_time_vector,
                state._port_dict,
                state.previous_state,
                state.violated_port,
                state.overflowed_port
            )
        #for all requests after index, decrease time remaining decrease port capacity for new_req's chosen port
        for state in trace[index:]:
            assert isinstance(state, reworked_graph.State)
            new_time_vector = copy.copy(state.time_vector)
            new_port_dict = copy.copy(state._port_dict)

            for index_inner in range(len(new_time_vector)):
                new_time_vector[index_inner] -= 1
            #safely edit state by creating a whole new one (state should be IMMUTABLE!)
            new_port_dict[optimal_port_key] -= 1
            state = reworked_graph.State(
                state.request_vector,
                new_time_vector,
                new_port_dict,
                state.previous_state,
                state.violated_port,
                state.overflowed_port
            )

        #TODO when creating the new request at index, make sure you don't be dumb and forget to set labels
        #TODO you will need to create a method which checks for OVERFLOW!!!!!, wrong port is probably fine because its no_pref
        #TODO when creating the new node its the same as original except for the port and labels
        assert isinstance(copy_of_state_before_branch, reworked_graph.State)

        copy_of_state_before_branch._port_dict[optimal_port_key] -= 1 #this will not check for overflowed port!

        branch_state = reworked_graph.State(
            copy_of_state_before_branch.request_vector,
            copy_of_state_before_branch.time_vector,
            copy_of_state_before_branch._port_dict,
        )

#TODO YOU WILL NEED TO GO THROUGH AND CHANGE THE PREVIOUS_STATE FOR EACH NODE THAT WAS DISRUPTED BY THE CHANGE

#TODO remove this please :)
# def bandaid_check_overflow(state):
#     assert isinstance(state, reworked_graph.State)
#     for key in state._port_dict.keys():
#         if state.previous_state is None:
#             state.previous_state =
#         elif state._port_dict[key] < state.previous_state._port_dict[key]:
#             if state._port_dict[key] < 0:
#                 return True


def rollout_monte_carlo(trace, index, req_to_add=None, return_subtrace=False):
    # add the new request to the state from which we will build the new graph
    if(index >= len(trace)):
        return  reworked_graph.ReworkedGraph(
            trace[0]._port_dict,
            1,
            list(trace[0].request_vector),
            list(trace[0].time_vector)
        ), []
    state_at_index = copy.deepcopy(trace[index])

    assert isinstance(state_at_index, reworked_graph.State)

    updated_request_vector = list(copy.copy(state_at_index.request_vector))
    updated_time_vector = list(copy.copy(state_at_index.time_vector))

    if req_to_add is not None:
        updated_request_vector.append(req_to_add[0])
        updated_time_vector.append(req_to_add[1]-index)

    state_at_index = reworked_graph.State(
        tuple(updated_request_vector),
        tuple(updated_time_vector),
        state_at_index._port_dict,
        state_at_index.previous_state,
        state_at_index.violated_port,
        state_at_index.overflowed_port
    )
    subtrace_before_index = copy.deepcopy(trace[:index]) # cut out part of trace before index

    resultant_graph = reworked_graph.ReworkedGraph(
        state_at_index._port_dict,
        1,
        list(state_at_index.request_vector),
        list(state_at_index.time_vector)
    )

    for index, state in enumerate(subtrace_before_index):
        if index+1 < len(subtrace_before_index):
            resultant_graph.transitions.add((state, "SEE_GRAPH_MANAGER", subtrace_before_index[index+1]))
        else: #last request in subtrace, hook it up with the base_state of the second part
            resultant_graph.transitions.add((state, "SEE_GRAPH_MANAGER", resultant_graph.base_state))
        resultant_graph.states.add(state)
    if index > 0:
        resultant_graph.base_state = copy.deepcopy(subtrace_before_index[0])

    return resultant_graph


def run_minimizing_mvp(system, rollout_index=0):
    num_rounds = 0
    violation_minimized = False
    total_time = 0
    cost_vec_per_round = list()
    trace_per_tower = None
    while not violation_minimized:
        for tower in system:  #debugging
            print(str(tower))
            system_req_vector_size_per_tower.append(len(tower.request_vector))
        time_start = time.perf_counter()
        system_timings.append([])
        for tower in system:
            system_timings[num_rounds].append([])
        system, violation_minimized, minimized_cost_vec = do_round(system, num_rounds, rollout_index)
        cost_vec_per_round.append(minimized_cost_vec)
        time_end = time.perf_counter()
        total_time += time_end - time_start
        print("\n new round - completed in time " + str(time_end - time_start))
        print("\tround " + str(num_rounds) + " breakdown :: ") #(tower number) | (time to find most expensive request in tower) | (time to synthesize with published request)")
        for tower_index in range(len(system_timings[0])):
            if system_timings[num_rounds][tower_index][1] == 0:
                print("\t tower " + str(tower_index) + " took " + str(system_timings[num_rounds][tower_index][0]) + " to find most expensive request and took " + str(system_timings[num_rounds][tower_index][1]) + " to synthesize with published request <--- publishing tower")
            else:
                print("\t tower " + str(tower_index) + " took " + str(system_timings[num_rounds][tower_index][0]) + " to find most expensive request and took " + str(system_timings[num_rounds][tower_index][1]) + " to synthesize with published request")
        print("")
        num_rounds += 1


    assert(minimized_cost_vec is not None)

    print("violation minimized")
    print("round breakdown average")
    cumulative_ERFind_time = [0 for i in range(len(system_timings[0]))]
    cumulative_PRTest_time = [0 for i in range(len(system_timings[0]))]
    for round_index in range(len(system_timings)):
        for tower_index in range(len(system_timings[0])):
            cumulative_ERFind_time[tower_index] += system_timings[round_index][tower_index][0]
            cumulative_PRTest_time[tower_index] += system_timings[round_index][tower_index][1]
    for tower_index in range(len(system_timings[0])):
        print("tower " + str(tower_index) + " expensive request cumulative : " + str(cumulative_ERFind_time[tower_index]) + " ,published request synthesis cumulative : " + str(cumulative_PRTest_time[tower_index]))

    print("end of system\n---")


    return total_time, num_rounds, minimized_cost_vec, system_timings, cost_vec_per_round

#returns the new system based on the round algorithm. Also, if violation is minimized (ie: system not altered), return True. else, return False
def do_round(system, round_index, rollout_index):
    # get most expensive requests in system

    worst_request_indices_list = []
    accompanying_step_list = []
    worst_cost_list = []
    publishing_tower_index_list = []

    tower_cost_list = [] #keep track of the tower, without removed request, cost

    for index, tower in enumerate(system):
        # does worst_request_dictionary already contain the most expensive/worst request for this tower
        time_start = time.perf_counter()
        if tower.base_state in worst_request_dictionary.keys():
            curr_request_index, curr_time, curr_cost, full_tower_cost = worst_request_dictionary[tower.base_state]
            # print("used old values")
            # time_start = time.perf_counter()
            # curr_request_index, curr_time, curr_cost = get_worst_request_index(tower)
            # time_end = time.perf_counter()
            # print("saved this many seconds " + str(time_end - time_start))
        else:
            curr_request_index, curr_time, curr_cost, full_tower_cost = get_worst_request_index(tower)
            worst_request_dictionary[tower.base_state] = (curr_request_index, curr_time, curr_cost, full_tower_cost)
        time_end = time.perf_counter()
        system_timings[round_index][index].append(time_end-time_start)
        tower_cost_list.append(full_tower_cost)
        print("Tower's current cost = " + str(full_tower_cost))
        worst_request_indices_list.append(curr_request_index)
        accompanying_step_list.append(curr_time)

        worst_cost_list.append(curr_cost)

        publishing_tower_index_list.append(index) #used to keep track of what tower each index is aligned to

    cost_vec = copy.deepcopy(tower_cost_list) #copy to return so that we can have the data on the final costs
    for i in worst_cost_list: #debugging
        print_formatted_cost(i)
    for index in range(len(system)): #prep system timing list
        system_timings[round_index][index].append(0)

    while len(worst_request_indices_list) is not 0:
        # "publish" worst request
        publishing_tower_index = 0
        list_index = 0
        published_request_index = 0
        cost_of_published_request = [-1, -1, -1]
        published_request_time = 0
        for index, cost in enumerate(worst_cost_list):
            if compare_levels(cost_of_published_request, cost):
                cost_of_published_request = copy.copy(cost)
                publishing_tower_index = publishing_tower_index_list[index]
                published_request_index = worst_request_indices_list[index]
                published_request_time = accompanying_step_list[index]
                list_index = index

        #remove worst request and counterparts from list
        #all subsequent prints are very helpful
        # print("pub_tower_index_list " + str(publishing_tower_index_list))
        # print("worst_request_list_index " + str(worst_request_indices_list))
        # print("publishing tower index " + str(publishing_tower_index))
        del worst_request_indices_list[list_index]
        del accompanying_step_list[list_index]
        del worst_cost_list[list_index]
        del publishing_tower_index_list[list_index]

        accepting_system = None # this is the system which will accept the new request
        
        # find which tower will accept
        cost_of_accepting_request_list = []
        accepting_tower_index = -1
        min_new_cost = cost_of_published_request
        for index, tower in enumerate(system):
            if index != publishing_tower_index:
                time_start = time.perf_counter()
                cost_of_tower_without_published_request, trace, empty, empty1 = generate_trace(tower)
                save_system = None # used to save the system, fixes the issue with building the tower from scratch ISSUE_ID=0
                final_trace = None # used to save the trace, fixes the issue with not having the correct trace for each tower be returned
                if rollout_index >= len(trace):
                    save_system = add_req_to_tower(tower, published_request_time)
                    cost_with_published_request = generate_trace(save_system)[0]
                    cost_of_accepting_request = vector_difference(cost_with_published_request, cost_of_tower_without_published_request) #param_1 - param_2
                else:
                    cost_of_accepting_request = vector_difference(generate_trace(rollout_monte_carlo(trace, rollout_index, ('wrong_tower', published_request_time)), True)[0], cost_of_tower_without_published_request) #param_1 - param_2
                #prevent infinite runs. cost_of_accepting_request won't have transition cost so we need to add a penalty so it won't swap if equal
                cost_of_accepting_request[len(cost_of_accepting_request)-1] += 1
                # cost_of_accepting_request[1] += 1 # level 1 cost of request landing at not preferred port (different tower than original)
                time_end = time.perf_counter()
                system_timings[round_index][index][1] += (time_end - time_start)
                cost_of_accepting_request_list.append(cost_of_accepting_request)
                if compare_levels(cost_of_accepting_request, min_new_cost):
                    min_new_cost = cost_of_accepting_request
                    accepting_tower_index = index
                    accepting_system = save_system
                # else: # only need trace if the system is minimized, therefore we can safely save "trace" because it is the trace without the published request (and thus is the original state)
                #     trace_per_tower[index] = trace
        print("accepting tower index " + str(accepting_tower_index))
        print("lowest_new_cost " + str(min_new_cost))
        print("cost of accepting request list :: " + str(cost_of_accepting_request_list))
        if accepting_tower_index != -1: #found a tower that will accept the request
            system[accepting_tower_index] = add_req_to_tower(system[accepting_tower_index], published_request_time)
            assert(published_request_index <= system_req_vector_size_per_tower[publishing_tower_index]-1) # ensure that the removed request was originally a part of this tower
            system[publishing_tower_index] = del_req_from_tower(system[publishing_tower_index], published_request_index)
            system_req_vector_size_per_tower[publishing_tower_index]-=1
            return system, False, cost_vec

    return system, True, cost_vec

#TODO: make each helper method take in a list of traces
def add_req_to_tower(old_tower, new_request_time):
    #copy over old tower parameters then add the new request
    req_copy = copy.deepcopy(old_tower.request_vector)
    time_copy = copy.deepcopy(old_tower.max_time_per_req_vector)
    port_dict = copy.deepcopy(old_tower.port_limits)
    req_per_step = old_tower.max_accepted_requests
    req_copy.append('wrong_tower')
    time_copy.append(new_request_time)

    # generate new tower
    new_tower = return_tower_specific(port_dict, req_per_step, req_copy, time_copy)
    return new_tower

def del_req_from_tower(old_tower, index_of_request_to_remove):
    req_copy = copy.deepcopy(old_tower.request_vector)
    time_copy = copy.deepcopy(old_tower.max_time_per_req_vector)
    port_dict = copy.deepcopy(old_tower.port_limits)
    req_per_step = old_tower.max_accepted_requests

    del req_copy[index_of_request_to_remove]
    del time_copy[index_of_request_to_remove]

    new_tower = return_tower_specific(port_dict, req_per_step, req_copy, time_copy)
    return new_tower

def cost_with_new_vec(input_graph, new_request_time):
    # create new tower parameters
    req_copy = copy.deepcopy(input_graph.request_vector)
    time_copy = copy.deepcopy(input_graph.max_time_per_req_vector)
    port_dict = copy.deepcopy(input_graph.port_limits)
    req_per_step = input_graph.max_accepted_requests
    req_copy.append('wrong_tower')
    time_copy.append(new_request_time)

    # generate new tower
    new_tower = return_tower_specific(port_dict, req_per_step, req_copy, time_copy)
    new_cost = generate_trace(new_tower)[0]
    return new_cost

def cost_with_removed_vec(input_graph, index_of_request_to_remove):
    req_copy = copy.deepcopy(input_graph.request_vector)
    time_copy = copy.deepcopy(input_graph.max_time_per_req_vector)
    port_dict = copy.deepcopy(input_graph.port_limits)
    req_per_step = input_graph.max_accepted_requests

    del req_copy[index_of_request_to_remove]
    del time_copy[index_of_request_to_remove]

    new_tower = return_tower_specific(port_dict, req_per_step, req_copy, time_copy)
    return generate_trace(new_tower)[0]


def get_worst_request_index(input_graph):
    worst_request_index = -1

    og = generate_trace(input_graph)
    original_cost = og[0]

    # request_list = [input_graph]

    highest_cost_vec = [-1, -1, -1]
    worst_request_time = -1

    for i in range(len(input_graph.request_vector)):
        start_time = time.time()

        curr_req = input_graph.request_vector[i]
        curr_time = input_graph.max_time_per_req_vector[i]

        # request_list.append(curr_req)
        new_cost = cost_with_removed_vec(input_graph, i)

        diff = vector_difference(original_cost, new_cost)

        if compare_levels(highest_cost_vec, diff):
            worst_request_index = i
            worst_request_time = curr_time
            highest_cost_vec = diff

        end_time = time.time()
        #print("finished req :: " + str(i) + " in time " + str(end_time - start_time))

    return worst_request_index, worst_request_time, highest_cost_vec, original_cost  # request_list, trace_list,


def compare_levels(orig_vec, new_vec): # if new - orig > 0 (priority based on index)
    for i in range(len(orig_vec)):
        if orig_vec[i] < new_vec[i]:
            return True
        elif orig_vec[i] == new_vec[i]:
            continue
        else:
            return False


def vector_part_sum(l1):
    x = 0
    for i in l1:
        x += i
    return x

def reset_globals():
    synthesis_dictionary.clear()
    worst_request_dictionary.clear()
    system_timings.clear()
    system_req_vector_size_per_tower.clear()

def vector_difference(l1, l2):
    diff = []
    for i in range(len(l1)):
        diff.append(l1[i] - l2[i])
    return diff

def print_formatted_cost(cost_to_print):
    print("Most expensive request cost: {}".format(cost_to_print))

def print_formatted_trace_path(trace_to_print):
    print("State path: {}".format(trace_to_print))

def return_tower_specific(port_dict, req_per_step, request_vec, time_req):
    return reworked_graph.ReworkedGraph(port_dict, req_per_step, request_vec, time_req)


def return_tower(num_requests, num_ports, time_vector, port_max):
    req = []
    port_dict = {}
    choices = ['%d' % i for i in range(num_ports)]
    length_choices = len(choices)
    index = 0
    for i in range(num_requests):
        if index >= length_choices:
            index = 0
        req.append(choices[index])
        index += 1
    for i in range(num_ports):
        key = '' + str(i)
        port_dict[key] = port_max[i]
    time = time_vector
    return reworked_graph.ReworkedGraph(port_dict, 1, req, time)

#TODO -> make it so that generate_trace doesn't need a "graph" class as parameter. (ie: just give it a set of states, trans, and labels)
def generate_trace(graph, override=False):
    # check if synthesis results already exist for the input graph. if so, return stored value
    if not override:
        if graph.base_state in synthesis_dictionary.keys():
            return synthesis_dictionary[graph.base_state]

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
    for req in graph.request_vector:
        if req == "wrong_tower":
            cost._value[1] += 1
    synthesis_dictionary[graph.base_state] = (cost, state_path, product_path, wpa)
    # print("Optimal cost: {}".format(cost))
    # print("State path: {}".format(state_path))
    # print("Product path: {}".format(product_path))
    
    return (cost, state_path, product_path, wpa)
