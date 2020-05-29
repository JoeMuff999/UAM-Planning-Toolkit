import reworked_graph
import copy
from tulip.transys import WeightedKripkeStructure as WKS
from tulip.transys.automata import WeightedFiniteStateAutomaton as WFA
from tulip.spec.prioritized_safety import PrioritizedSpecification
from tulip.transys.mathset import PowerSet
from tulip.mvp import solve as solve_mvp
import time
import numpy as np
import matplotlib.pyplot as plt

YES = "y"
NO = "n"


# def generate_system():
# use_input_file = input("Use previously existing system? y/n \n")
# if use_input_file == YES:
# tower1 = reworked_graph.ReworkedGraph({"a": 1, "b" : 1, "c" : 1}, 2, ["a", "b","c"], [0, 4, 1])
# trace_tuple1 = generate_trace(tower1)
# tower2 = reworked_graph.ReworkedGraph({"a": 1, "b" : 1}, 1, ["a", "b","b"], [0, 2, 1])
# trace_tuple2 = generate_trace(tower2)
# tower3 = reworked_graph.ReworkedGraph({"a": 1, "b" : 3}, 2, ["a", "a", "b","b"], [0, 0, 1, 1])
# trace_tuple3 = generate_trace(tower3)
# req4 = []
#
# for i in range(10):
#     if i < 50:
#         req4.append("a")
#     else:
#         req4.append("a")
# time4 = [5 for i in req4]
#
#
#
#
# start_time = time.time()
# tower4 = reworked_graph.ReworkedGraph({"a" : 1, "b" : 2, "c" :1}, 1, req4, time4)
# end_time = time.time()
# print(end_time-start_time)
# start_time = time.time()
# trace_tuple4 = generate_trace(tower4)
# end_time = time.time()
# print(end_time - start_time)
# x = [trace_tuple1, trace_tuple2,trace_tuple3]
# for i in x:
#     print("Optimal cost: {}".format(i[0]))
#     print("State path: {}".format(i[1]))
#     print("Product path: {}".format(i[2])

# hi = [[2,3,4],[5,6,7],[8,9,10]]
# for row in range(len(hi)):
#     x = ['%f' % i for i in hi[row]]
#     print(x)
# trace_tuple1 = generate_trace(tower1)
# req_max = 3;
# port_max = 3;
# x = [0 for i in range(req_max)]
# times = [x for i in range(req_max)]
# for i in range(1, req_max):
#     for j in range(1, port_max):
#         if i < 5 or j < 5:
#             tower = return_tower(i, j)
#             start_time = time.time()
#             generate_trace(tower)
#             end_time = time.time()
#             times[i][j] = end_time-start_time
#             print("TIMES = " + str(i) + " : "+ str(j) + " time = "+ str(times[i][j]))
# rows = ['%d requests' % i for i in range(req_max)]
# columns = ['%d ports' % i for i in range(port_max)]
#
# cell_text = []
# for row in range(req_max):
#     cell_text.append(['%f' % i for i in times[row]])
#
# the_table = plt.table(cellText = cell_text, rowLabels=rows, colLabels=columns, loc='center')
# plt.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)
# plt.tick_params(axis='y', which='both', right=False, left=False, labelleft=False)
# for pos in ['right', 'top', 'bottom', 'left']:
#     plt.gca().spines[pos].set_visible(False)
# plt.show()

# 1 request remove
# 1 request added directly reduce cost

# TODO :: make return tower s.t. you can easily send a list of request max times. needs to be deterministic
def runner():
    # return_tower :: num_requests, num_ports, time_steps, port_max
    tower1 = return_tower(2, 2, 2, [1,1])
    tower2 = return_tower(2, 1, 2, [3])
    tower3 = return_tower(2, 2, 2, [0,1])

    system = [tower1, tower2, tower3]
    violation_minimized = False
    while not violation_minimized:
        for i in system:
            print(str(i))

        system, violation_minimized = do_round(system)

        print("\n new round \n")


    # worst_request1, req_list1, trace_list1 = get_worst_request(tower1)
    # worst_request2, req_list2, trace_list2 = get_worst_request(tower2)
    #
    # cost_reduction1 = trace_list1[int(worst_request1)][0]
    # cost_reduction2 = trace_list2[int(worst_request2)][0]
    #
    # calculate_cost_benefit(tower2, worst_request1, 3, cost_reduction1, trace_list2[0][0])
    # for trace in trace_list1:
    #     print("Optimal cost: {}".format(trace[0]))
    #     print("State path: {}".format(trace[1]))
    #
    # for trace in trace_list2:
    #     print("Optimal cost: {}".format(trace[0]))
    #     print("State path: {}".format(trace[1]))

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
        #print(worst_cost_list)
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
                list_index = index
        

        #remove worst request and counterparts from list
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
        max_new_cost = cost_of_published_request #supposed to be int max but this will never happen
        for index, tower in enumerate(system):
            if index != publishing_tower_index:
                cost_of_tower_without_published_request = generate_trace(tower)[0]
                cost_of_accepting_request = vector_difference(cost_with_new_vec(tower, published_request_time), cost_of_tower_without_published_request) #param_1 - param_2
                cost_of_accepting_request_list.append(cost_of_accepting_request)
                if compare_levels(cost_of_accepting_request, max_new_cost):
                    max_new_cost = cost_of_accepting_request
                    accepting_tower_index = index
        print("accepting tower index " + str(accepting_tower_index))
        print("max_new_cost " + str(max_new_cost))
        if accepting_tower_index != -1: #found a tower that will accept the request
            system[accepting_tower_index] = add_req_to_tower(system[accepting_tower_index], published_request_time)
            system[publishing_tower_index] = del_req_from_tower(system[publishing_tower_index], published_request_index)
            return system, False

    return system, True


    #TODO


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
