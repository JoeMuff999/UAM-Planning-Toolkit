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

# TODO :: ALGORITHM IS NOT FULLY TESTED, MAY NOT BE WORKING COMPLETELY. WORKS FOR SIMPLE EXAMPLES AT THE VERY LEAST
# TODO (just a note, but wanted to make it highlighted) :: you will encounter "same labeled transition warnings "from_state---[label]---> to_state"".
# TODO (note continued) :: This has to do with TuLiP encountering repeat transitions. It hasn't had an effect on logic thus far, so I wouldn't worry too much about it.
# TODO (note) :: there are many print statements in this file. This is helpful debug information.
def runner():
    # return_tower :: num_requests, num_ports, time_steps, port_max <- parameter information
    tower1 = return_tower(3, 3, 1, [0,1,0])
    tower2 = return_tower(3, 1, 3, [4])
    tower3 = return_tower(3, 3, 3, [1,1,2])

    system = [tower1, tower2, tower3]
    violation_minimized = False
    while not violation_minimized:
        for i in system:
            print(str(i)) #debugging

        system, violation_minimized = do_round(system)

        print("\n new round \n")
    print("violation minimized")

#returns the new system based on the round algorithm. If violation is minimized (ie: system not altered), return True. else, return False
def do_round(system):
    # get most expensive requests in system

    worst_request_indices_list = []
    accompanying_step_list = []
    worst_cost_list = []
    publishing_tower_index_list = []

    for index,tower in enumerate(system):
        curr_request_index, curr_time, curr_cost = get_worst_request_index(tower)

        worst_request_indices_list.append(curr_request_index)
        accompanying_step_list.append(curr_time)
        worst_cost_list.append(curr_cost)
        publishing_tower_index_list.append(index) #used to keep track of what tower each index is aligned to

    for i in worst_cost_list:
        print_formatted_cost(i)
    while len(worst_request_indices_list) is not 0:
        # "publish" worst request
        publishing_tower_index = 0
        list_index = 0
        published_request_index = 0
        cost_of_published_request = [-1, -1, -1]
        published_request_time = 0
        for index, cost in enumerate(worst_cost_list):
            if compare_levels(cost_of_published_request, cost):
                cost_of_published_request = cost
                publishing_tower_index = publishing_tower_index_list[index]
                published_request_index = worst_request_indices_list[index]
                published_request_time = accompanying_step_list[index]
                list_index = index
        

        #remove worst request and counterparts from list
        #all subsequent prints are very helpful
        print("pub_tower_index_list " + str(publishing_tower_index_list))
        print("worst_request_list_index " + str(worst_request_indices_list))
        print("publishing tower index " + str(publishing_tower_index))
        del worst_request_indices_list[list_index]
        del accompanying_step_list[list_index]
        del worst_cost_list[list_index]
        del publishing_tower_index_list[list_index]



        # find which tower will accept
        cost_of_accepting_request_list = []
        accepting_tower_index = -1
        min_new_cost = cost_of_published_request
        for index, tower in enumerate(system):
            if index != publishing_tower_index:
                cost_of_tower_without_published_request = generate_trace(tower)[0]
                cost_of_accepting_request = vector_difference(cost_with_new_vec(tower, published_request_time), cost_of_tower_without_published_request) #param_1 - param_2
                cost_of_accepting_request_list.append(cost_of_accepting_request)
                if compare_levels(cost_of_accepting_request, min_new_cost):
                    min_new_cost = cost_of_accepting_request
                    accepting_tower_index = index
        print("accepting tower index " + str(accepting_tower_index))
        print("lowest_new_cost " + str(min_new_cost))
        print("cost of accepting request list :: " + str(cost_of_accepting_request_list))
        if accepting_tower_index != -1: #found a tower that will accept the request
            system[accepting_tower_index] = add_req_to_tower(system[accepting_tower_index], published_request_time)
            system[publishing_tower_index] = del_req_from_tower(system[publishing_tower_index], published_request_index)
            return system, False

    return system, True

def add_req_to_tower(old_tower, new_request_time):
    #copy over old tower parameters then add the new request
    req_copy = copy.deepcopy(old_tower.request_vector)
    time_copy = copy.deepcopy(old_tower.max_time_per_req_vector)
    port_dict = copy.deepcopy(old_tower.port_limits)
    req_per_step = old_tower.max_accepted_requests
    req_copy.append('no_pref')
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
    req_copy.append('no_pref')
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

    request_list = [input_graph]

    highest_cost_vec = [-1, -1, -1]
    worst_request_time = -1

    for i in range(len(input_graph.request_vector)):
        start_time = time.time()

        curr_req = input_graph.request_vector[i]
        curr_time = input_graph.max_time_per_req_vector[i]

        request_list.append(curr_req)
        new_cost = cost_with_removed_vec(input_graph, i)

        diff = vector_difference(original_cost, new_cost)

        if compare_levels(highest_cost_vec, diff):
            worst_request_index = i
            worst_request_time = curr_time
            highest_cost_vec = diff

        end_time = time.time()
        #print("finished req :: " + str(i) + " in time " + str(end_time - start_time))

    return worst_request_index, worst_request_time, highest_cost_vec  # request_list, trace_list,


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


def vector_difference(l1, l2):
    diff = []
    for i in range(len(l1)):
        diff.append(l1[i] - l2[i])
    return diff

def print_formatted_cost(cost_to_print):
    print("Optimal cost: {}".format(cost_to_print))

def return_tower_specific(port_dict, req_per_step, request_vec, time_req):
    return reworked_graph.ReworkedGraph(port_dict, req_per_step, request_vec, time_req)

# TODO :: change param "time_steps" to be a vector with len = len(num_requests) (ie: max time steps for each request)
def return_tower(num_requests, num_ports, time_steps, port_max):
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
    time = [time_steps for i in req]
    return reworked_graph.ReworkedGraph(port_dict, 1, req, time)


def generate_trace(graph):
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

    # print("Optimal cost: {}".format(cost))
    # print("State path: {}".format(state_path))
    # print("Product path: {}".format(product_path))
    return (cost, state_path, product_path, wpa)

runner()
