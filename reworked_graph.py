'''
Author information:
Joey R. Muffoletto
University of Texas at Austin
Autonomous Systems Group
jrmuff@utexas.edu
'''

import copy
from itertools import combinations
from itertools import product

REQUESTS = 0
TIMES = 1

NO_PREF = "no_pref"
#TODO :: IMPLEMENT A WAY TO HAVE NO PORT PREFERENCE FOR A REQUEST FOR REALLOCATION PURPOSES -> believe this is already done
#TODO :: fix bug that overflowed gets counted more than once

class ReworkedGraph(object):
    def __init__(self, requests_per_port_per_step={}, max_accepted_requests=0, request_vector=[],
                 max_time_per_req_vector=[]):

        self.max_accepted_requests = max_accepted_requests
        self.request_vector = request_vector
        self.max_time_per_req_vector = max_time_per_req_vector

        assert len(max_time_per_req_vector) == len(request_vector)

        self.base_state = State(tuple(copy.deepcopy(request_vector)), tuple(copy.deepcopy(max_time_per_req_vector)), port_dict=requests_per_port_per_step)

        self.states = set()
        self.transitions = set()

        self.port_limits = requests_per_port_per_step
        self.states.add(self.base_state)
        self.generate_states(self.base_state,
                             (copy.deepcopy(self.request_vector), copy.deepcopy(self.max_time_per_req_vector)), copy.deepcopy(self.base_state._port_dict))


    def generate_states(self, previous_state=None, remaining_requests=([], []), port_dict=None):
        if (len(remaining_requests[0]) == 0):  # or (not all(i >= 0 for i in remaining_requests[TIMES])):
            return
        elif all(i == -1 for i in remaining_requests[TIMES]) and not previous_state.scratch:
            tmp = tuple()  # empty choice
            transition = (previous_state, tmp, previous_state)
            if transition in self.transitions:
                return
            else:
                self.transitions.add(transition)
                previous_state.scratch = True  # use so that doesn't infinitely self loop, but does allow it to recurse if first time
                self.generate_states(previous_state, remaining_requests, port_dict)
        else:
            choices = self.generate_choices(len(remaining_requests[0])) # TODO make this not be returned
            for choice in choices:
                port_permutations = self.generate_cartesian_product(previous_state._port_dict.keys(), len(choice))
                for port_choice in port_permutations:

                    copied_requests = []
                    indices_of_negatives = self.generate_ignore_list(remaining_requests)
                    self.iterate_all_requests(remaining_requests, choice, indices_of_negatives)
                    if len(choice) != 0:
                        copied_requests = [None] * choice[len(choice) - 1]
                        offset = 0
                        for i in choice:
                            index_for_RR = i - offset
                            copy_of_selected_request = (remaining_requests[REQUESTS][index_for_RR], remaining_requests[TIMES][index_for_RR])
                            assert type(copy_of_selected_request) is tuple
                            copied_requests.insert(i, copy_of_selected_request)  # copied_requests = list of tuples, tuple = (reqName,time)
                            del remaining_requests[REQUESTS][index_for_RR]
                            del remaining_requests[TIMES][index_for_RR]
                            offset += 1

                    tmp = [i for i in copied_requests if i]  # remove none
                    # decrease remaining capacity of ports
                    self.update_port_states(port_dict, port_choice)
                    # check if a request was landed at a different port than asked for
                    port_violation = False
                    #check if a port is overflowed
                    port_overflowed = False

                    if len(choice) > 0:
                        port_violation = self.landed_different_port(copy.deepcopy(port_choice), copy.deepcopy(tmp))
                        port_overflowed = self.overflowed_port(port_choice, port_dict, previous_state._port_dict)



                    new_state = State(tuple(copy.deepcopy(remaining_requests[REQUESTS])), tuple(copy.deepcopy(remaining_requests[TIMES])), port_dict=copy.deepcopy(port_dict), previous_state=previous_state, violated_port=port_violation, overflowed_port=port_overflowed)

                    self.states.add(new_state)

                    transition = (previous_state, tuple(tmp), new_state)
                    self.transitions.add(transition)

                    self.generate_states(new_state, remaining_requests, port_dict)

                    for i in range(len(copied_requests)):
                        req = copied_requests[i]
                        if req is not None:
                            remaining_requests[REQUESTS].insert(i, req[REQUESTS])
                            remaining_requests[TIMES].insert(i, req[TIMES])
                    self.undo_iteration_of_requests(remaining_requests, choice, indices_of_negatives)
                    self.reset_port_states(port_dict, port_choice)

    def generate_choices(self, num_requests):
        base_list = [i for i in range(num_requests)]
        list_to_return = []
        for i in range(
            self.max_accepted_requests + 1):  # range(1, self.max_accepted_requests+1) -> don't include empty case
            tmp = combinations(base_list, i)
            list_to_return.extend(tmp)
        return list_to_return

    def generate_cartesian_product(self, keys, length_of_choice):
        tmp = list(product(keys, repeat=length_of_choice))
        return tmp

    def generate_ignore_list(self, req_vec):
        tmp_list = []
        for i in range(len(req_vec[TIMES])):
            if req_vec[TIMES][i] == -1:
                tmp_list.append(i)
        return tmp_list

    def landed_different_port(self, port_choice, copied_requests):
        port_choice_list = list(port_choice)
        for request_tuple in copied_requests:
            if request_tuple is not None:
                if request_tuple[0] in port_choice_list:
                    port_choice_list.remove(request_tuple[0])
                elif request_tuple[0] != NO_PREF:
                    return True
        return False

    def overflowed_port(self, port_choice, port_dict, previous_port_dict):
        port_choice_list = list(port_choice)
        for port in port_choice_list:
            key = str(port)
            if port == NO_PREF:
                continue
            elif port_dict[key] <= -1 and previous_port_dict[key] > port_dict[key]: #logic : if landed another at this port, and the previous state did not have this many, must be overflow
                return True
        return False

    def update_port_states(self, port_dict, keys_to_deiterate):
        for key in keys_to_deiterate:
            port_dict[key] -= 1

    def reset_port_states(self, port_dict, keys_to_iterate):
        for key in keys_to_iterate:
            port_dict[key] += 1

    def iterate_all_requests(self, req_vec, ignore_vec, negative_vec):
        # req_vev = tuple(list('a','b'), list(2,2)) set(requests, times)
        for i in range(len(req_vec[1])):
            if i not in ignore_vec and i not in negative_vec:
                req_vec[1][i] -= 1

    def undo_iteration_of_requests(self, req_vec, ignore_vec, negative_vec):
        for i in range(len(req_vec[1])):
            if i not in ignore_vec and i not in negative_vec:
                req_vec[1][i] += 1


class State(object):

    def __init__(self, request_vector=tuple, time_vector=tuple, port_dict=dict, previous_state=None, violated_port=False, overflowed_port=False):

        assert type(request_vector) is tuple
        assert type(time_vector) is tuple
        assert len(request_vector) == len(time_vector)


        self.violated_port = violated_port
        self.overflowed_port = overflowed_port

        self.previous_state = previous_state

        self.request_vector = request_vector
        self.time_vector = time_vector
        self._port_dict = port_dict
        self.labels = self._generate_labels()

        self.scratch = False

    def _generate_labels(self):
        label_tmp = []
        if not self._contains_expired_request():
            if self.previous_state is not None: #add this extra check so that states with no requests in them aren't automatically valid
                if "VALID" in self.previous_state.labels:
                    label_tmp.append("VALID")
            else:
                label_tmp.append("VALID")
        if len(self.request_vector) is 0:
            label_tmp.append("FINISH")
        if self.violated_port:
            label_tmp.append("WRONG_PORT")
        if self.overflowed_port:
            label_tmp.append("OVERFLOWED_PORT")
        return label_tmp
    # valid label
    def _contains_expired_request(self):
        return not all(i >= 0 for i in self.time_vector)
    # use hashing s.t. when I generate states, duplicates are very easily found. extremely helpful.
    def __key(self):
        port_list = []
        for key in self._port_dict:
            port_list.append(self._port_dict[key])
        port_tuple = tuple(port_list)
        label_tuple = tuple(self.labels)
        return (self.request_vector, self.time_vector, port_tuple, label_tuple)

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        if isinstance(other, State):
            return self.__key() == other.__key()
        return NotImplemented

    def __str__(self):
        return "State currently has requests :: " + str(self.request_vector) + " Time states of :: " + str(
            self.time_vector) + " Port states of :: " + str(
            self._port_dict) + " Labels :: " + str(self.labels) + "  \n"  # + " Possible Paths's:: " + str(self.actionsLeadingToState) + "  \n"

    def __repr__(self):
        return self.__str__()
