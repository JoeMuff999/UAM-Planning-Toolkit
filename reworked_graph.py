import copy
from itertools import combinations
REQUESTS = 0
TIMES = 1
class ReworkedGraph(object):
    def __init__(self, num_ports=0, port_capacity=0, max_accepted_requests=0, request_vector=None,
                 max_time_per_req_vector=None):
        self.num_ports = num_ports
        self.port_capacity = port_capacity
        self.max_accepted_requests = max_accepted_requests
        self.request_vector = request_vector
        self.max_time_per_req_vector = max_time_per_req_vector

        assert len(max_time_per_req_vector) == len(request_vector)

        self.base_state = State(tuple(copy.deepcopy(request_vector)), tuple(copy.deepcopy(max_time_per_req_vector)))

        self.states = set()
        self.transitions = set()

        self.states.add(self.base_state)
        self.generate_states(self.base_state, (copy.deepcopy(self.request_vector), copy.deepcopy(self.max_time_per_req_vector)))

    def generate_states(self, previous_state=None, remaining_requests=([], [])):
        if (len(remaining_requests[0]) == 0) or (not all(i >= 0 for i in remaining_requests[TIMES])):
            return
        else:
            choices = self.generate_choices(len(remaining_requests[0]))
            for choice in choices:
                copied_requests = []
                self.iterate_all_requests(remaining_requests, choice)
                if len(choice) != 0:
                    copied_requests = [None] * choice[len(choice)-1]
                    offset = 0
                    for i in choice:
                        index_for_RR = i - offset
                        copy_of_selected_request = (remaining_requests[REQUESTS][index_for_RR], remaining_requests[TIMES][index_for_RR])
                        assert type(copy_of_selected_request) is tuple
                        copied_requests.insert(i, copy_of_selected_request) #copied_requests = list of tuples, tuple = (reqName,time)
                        del remaining_requests[REQUESTS][index_for_RR]
                        del remaining_requests[TIMES][index_for_RR]
                        offset += 1

                new_state = State(tuple(copy.deepcopy(remaining_requests[REQUESTS])), tuple(copy.deepcopy(remaining_requests[TIMES])))
                new_state._port_dict = copy.deepcopy(previous_state._port_dict)
                new_state.update_port_states(copied_requests)

                self.states.add(new_state)
                tmp = [i for i in copied_requests if i] #remove none
                transition = (previous_state, tuple(tmp), new_state)
                self.transitions.add(transition)

                self.generate_states(new_state, remaining_requests)

                for i in range(len(copied_requests)):
                    req = copied_requests[i]
                    if req is not None:
                        remaining_requests[REQUESTS].insert(i, req[REQUESTS])
                        remaining_requests[TIMES].insert(i, req[TIMES])
                self.undo_iteration_of_requests(remaining_requests, choice)


    def generate_choices(self, num_requests):
        base_list = [i for i in range(num_requests)]
        list_to_return = []
        for i in range(self.max_accepted_requests+1): #range(1, self.max_accepted_requests+1) -> don't include empty case
            tmp = combinations(base_list, i)
            list_to_return.extend(tmp)
        return list_to_return

    def iterate_all_requests(self, req_vec, ignore_vec):
        #req_vev = tuple(list('a','b'), list(2,2)) set(requests, times)
        for i in range(len(req_vec[1])):
            if i not in ignore_vec:
                req_vec[1][i] -= 1

    def undo_iteration_of_requests(self, req_vec, ignore_vec):
        for i in range(len(req_vec[1])):
            if i not in ignore_vec:
                req_vec[1][i] += 1



class State(object):
    def __init__(self, request_vector=tuple, time_vector=tuple):

        assert type(request_vector) is tuple
        assert type(time_vector) is tuple
        assert len(request_vector) == len(time_vector)

        self.request_vector = request_vector
        self.time_vector = time_vector
        self._port_dict = self._generate_ports()

    def update_port_states(self, copied_requests):
        for req in copied_requests:
            if req is not None:
                key = req[0]
                self._port_dict[key] += 1

    def _generate_ports(self):
        dict_to_return = dict()
        tmp_set = set() #using this to prevent creating multiple keys for one request
        for req in self.request_vector:
            tmp_tuple = (req, 0)
            assert type(tmp_tuple) is tuple
            tmp_set.add(tmp_tuple)

        for tup in tmp_set:
            dict_to_return.update({tup[0]: tup[1]})
        return dict_to_return


    def __key(self):
        return (self.request_vector, self.time_vector)

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        if isinstance(other, State):
            return self.__key() == other.__key()
        return NotImplemented

    def __str__(self):
        return "State currently has requests :: " + str(self.request_vector) + " Time states of :: " + str(
            self.time_vector) + " Port states of :: " + str(self._port_dict) + " \n"  # + " Labels :: " + str(self.labels) + "  \n" #+ " Possible Paths's:: " + str(self.actionsLeadingToState) + "  \n"

    def __repr__(self):
        return self.__str__()

