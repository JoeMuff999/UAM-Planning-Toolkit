import random
import graph_test_methods
import graph_manager
import reworked_graph

def get_randomized_system():
    # System Parameters
    NUM_TOWERS = 5  # number of towers in the system
    ROLLOUT_INDEX = 1  # index of start node when performing rollout heuristic
    TIME_STEPS = 4  # number of time steps alloted for each request
    NUM_PORTS = 3  # number of ports each tower will have
    PORT_MAX = 4

    GRAPH_INDEX = 0

    random.seed(10)

    num_requests_per_tower = []
    time_vector_per_tower = []
    port_vector_per_tower = []
    num_ports_adjusted = NUM_PORTS
    system_storage = []
    system = []
    # randomizing the number of requests
    for i in range(NUM_TOWERS):
        num_requests_random = random.randint(1, 6)

        if NUM_PORTS > num_requests_random:
            NUM_PORTS = num_requests_random

        num_requests_per_tower.append(num_requests_random)
        time_vector_per_tower.append([TIME_STEPS for i in range(num_requests_random)])
        port_vector_per_tower.append([PORT_MAX for i in range(num_requests_random)])
        tower = graph_manager.return_tower(num_requests_random, NUM_PORTS, time_vector_per_tower[i], port_vector_per_tower[i])
        #do something with this data
        system_storage = (tower, num_requests_random, NUM_PORTS, time_vector_per_tower[i], PORT_MAX)

        system.append(tower)

        #print("tower " + str(i) + " : " + str(tower_tuple))
    return system



