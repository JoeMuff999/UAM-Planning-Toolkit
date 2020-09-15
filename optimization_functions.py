import random
import graph_test_methods
import graph_manager
import reworked_graph

def set_seed(seed):
    random.seed(seed)

def get_randomized_system(num_towers=5, request_min=1, request_max=5):
    # System Parameters
    NUM_TOWERS = num_towers  # number of towers in the system
    ROLLOUT_INDEX = 1  # index of start node when performing rollout heuristic
    #TIME_STEPS = 3  # number of time steps alloted for each request
    NUM_PORTS = 3  # number of ports each tower will have

    PORT_CAPACITY_MIN = 1
    PORT_CAPACITY_MAX = 3

    TIME_STEP_MIN = 1
    TIME_STEP_MAX = 3
    GRAPH_INDEX = 0

    REQUEST_MIN = request_min
    REQUEST_MAX = request_max

    num_requests_per_tower = []
    time_vector_per_tower = []
    port_vector_per_tower = []
    num_ports_adjusted = NUM_PORTS
    system_storage = []
    system = []
    # randomizing the number of requests
    for i in range(NUM_TOWERS):
        num_requests_random = random.randint(request_min, request_max)

        num_ports_adjusted = NUM_PORTS
        if num_ports_adjusted >= num_requests_random:
            num_ports_adjusted = num_requests_random

        num_requests_per_tower.append(num_requests_random)
        time_vector_per_tower.append([])
        # get random time for each request
        for j in range(num_requests_random):
            time_vector_per_tower[i].append(random.randint(TIME_STEP_MIN, TIME_STEP_MAX))
        #time_vector_per_tower.append([TIME_STEPS for i in range(num_requests_random)])
        port_vector_per_tower.append([])
        for j in range(num_ports_adjusted):
            port_vector_per_tower[i].append(random.randint(PORT_CAPACITY_MIN, PORT_CAPACITY_MAX))
        #port_vector_per_tower.append([PORT_MAX for i in range(num_requests_random)])
        tower = graph_manager.return_tower(num_requests_random, num_ports_adjusted, time_vector_per_tower[i], port_vector_per_tower[i])
        #do something with this data
        system_storage = (tower, num_requests_random, num_ports_adjusted, time_vector_per_tower[i], port_vector_per_tower[i])

        system.append(tower)

        #print("tower " + str(i) + " : " + str(tower_tuple))
    return system



