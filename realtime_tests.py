import graph_manager as gm
import realtime_manager as rm

def test_realtime():
    tower1 = gm.return_tower(2, 2, [1,1], [0,1,0])
    tower2 = gm.return_tower(2, 1, [3,3], [2])

    system = [tower1, tower2]
    # towerC3 = gm.return_tower(3, 3, [3,3,3], [1,1,2])
    # towerC4 = gm.return_tower(3, 3, [4,4,4], [2, 2, 2])
    # towerC5 = gm.return_tower(3, 3, [2,2,2],[3,3,3])
    # systemC = [towerC1, towerC2, towerC3, towerC4, towerC5]

    rm.configure_realtime(tau=0)
    sample_request  = ('0', 3) # port name, time to land
    sample_request_dict = {0: [sample_request, sample_request]} # tower index maps to a list of (port_name, expiration_time) tuples.
    rm.main_loop(system, [[] for i in range(10)])
    gm.reset_globals()
    print("\n\nEnd of test 1\n\n")

def test_additional_requests():
    tower1 = gm.return_tower(2, 2, [1,1], [0,1,0])
    tower2 = gm.return_tower(2, 1, [3,3], [2])

    system = [tower1, tower2]
    # towerC3 = gm.return_tower(3, 3, [3,3,3], [1,1,2])
    # towerC4 = gm.return_tower(3, 3, [4,4,4], [2, 2, 2])
    # towerC5 = gm.return_tower(3, 3, [2,2,2],[3,3,3])
    # systemC = [towerC1, towerC2, towerC3, towerC4, towerC5]

    rm.configure_realtime(tau=0)
    sample_request  = ('no_pref', 3) # port name, time to land
    sample_request_dict = {0: [(sample_request)], 1: [(sample_request)]} # tower index maps to a list of (port_name, expiration_time) tuples.
    rm.main_loop(system, [[sample_request_dict] for i in range(2)])
    gm.reset_globals()
    print("\n\nEnd of test 2\n\n")


def test_additional_requests_with_tau():
    tower1 = gm.return_tower(2, 3, [5, 10], [2, 2, 2])
    tower2 = gm.return_tower(2, 3, [5, 10], [2, 2, 2])

    system = [tower1, tower2]
    # towerC3 = gm.return_tower(3, 3, [3,3,3], [1,1,2])
    # towerC4 = gm.return_tower(3, 3, [4,4,4], [2, 2, 2])
    # towerC5 = gm.return_tower(3, 3, [2,2,2],[3,3,3])
    # systemC = [towerC1, towerC2, towerC3, towerC4, towerC5]

    rm.configure_realtime(tau=1)
    sample_request  = ('no_pref', 99) # port name, time to land
    sample_request_dict = {0: [(sample_request)], 1: [(sample_request)]} # tower index maps to a list of (port_name, expiration_time) tuples.
    rm.main_loop(system, [[sample_request_dict]])# for i in range(2)])
    gm.reset_globals()
    print("\n\nEnd of test 3\n\n")

def test_additional_requests_with_tau_single_tower():
    tower1 = gm.return_tower(5, 5, [5 for i in range(5)], [2 for i in range(5)])
    # trace = gm.generate_trace(tower1)[1]
    system = [tower1]
    # towerC3 = gm.return_tower(3, 3, [3,3,3], [1,1,2])
    # towerC4 = gm.return_tower(3, 3, [4,4,4], [2, 2, 2])
    # towerC5 = gm.return_tower(3, 3, [2,2,2],[3,3,3])
    # systemC = [towerC1, towerC2, towerC3, towerC4, towerC5]

    rm.configure_realtime(tau=10)
    sample_request  = ('no_pref', 8) # port name, time to land
    sample_request_dict = {0: [(sample_request)]} # tower index maps to a list of (port_name, expiration_time) tuples.
    rm.main_loop(system, [[sample_request_dict] for i in range(7)])# for i in range(2)])
    gm.reset_globals()
    print("\n\nEnd of test 4\n\n")

def test_additional_requests_with_empty_state_gap():
    tower1 = gm.return_tower(0, 2, [], [3 for i in range(2)])
    system = [tower1]
    sample_request  = ('no_pref', 8) # port name, time to land
    sample_request_dict = {0: [(sample_request)]} # tower index maps to a list of (port_name, expiration_time) tuples.
    
    rm.configure_realtime(tau=10)
    
    additional_requests_input = [[] for i in range(7)]
    to_append = [[sample_request_dict] for i in range(7)]
    additional_requests_input = additional_requests_input + to_append
    print(additional_requests_input)
    rm.main_loop(system, additional_requests_input)# for i in range(2)])
    gm.reset_globals()

    print("\n\nEnd of test 5\n\n")

def debug_discrepancy():
    tower1 = gm.return_tower(2, 2, [20,20], [3 for i in range(2)])
    system = [tower1]
    sample_request  = ('no_pref', 8) # port name, time to land
    sample_request_dict = {0: [sample_request,sample_request]} # tower index maps to a list of (port_name, expiration_time) tuples.
    
    rm.configure_realtime(tau=2)
    to_append = [[sample_request_dict] for i in range(3)]
    (completed_traces, timings) = rm.main_loop(system, to_append)# for i in range(2)])
    mvp_output_per_tower = rm.get_mvp_output(completed_traces)
    print(gm.print_formatted_trace_path(mvp_output_per_tower[0][1]))
    gm.reset_globals()

# test_realtime()
# test_additional_requests()
# test_additional_requests_with_tau()
# test_additional_requests_with_empty_state_gap()
# test_additional_requests_with_tau_single_tower()