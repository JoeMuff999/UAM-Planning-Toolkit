# class for the main loop of the "simulation"
import reworked_graph
import graph_manager as gm

ROLLOUT_INDEX = 1 #how far back to go when doing rollout. an index of 0 is the least level of optimization. if index >= len(trace), will default to 0

def main_loop(system, rollout_index=ROLLOUT_INDEX):
    #initialization stuff:
    initialize_globals(rollout_index=ROLLOUT_INDEX)
    final_traces = [[] for tower in system]
    while(True):
        #receive minimized system
        minimized_traces = get_minimized_traces_from_system(system)
        #gm.run_minimizing_mvp(system, rollout_index=ROLLOUT_INDEX, return_traces=True)[5]
        #rollout from index (ie: string it until rollout state)

        if check_if_finished(minimized_traces):
            break;
        minimized_rolled_system = list()
        subtraces = list()
        for trace in minimized_traces:
            resultant_graph, subtrace = gm.rollout_monte_carlo(trace, rollout_index+1, return_subtrace=True)
            minimized_rolled_system.append(resultant_graph)
            subtraces.append(subtrace)
            # print(resultant_graph)
        #record transition (ie: which request was accepted)

    #or, record the state that got cut off and then at the end we run mvp
    #TODO: understand that you can only test with 1 rollout index because if you remove a subtrace with more than 1 you will end up skipping forward in time
        for index, tower in enumerate(minimized_rolled_system):
            # build the final trace by adding the timestepped
            final_traces[index].append(subtraces[index])
            if len(subtraces[index]) == 0:
                continue
            state = subtraces[index][0]
            tower.states.remove(state)
            if len(subtraces[index]) > 1:
                for transition in tower.transitions:
                    if transition[0] == state and transition[2] == subtraces[index][1]:
                        tower.transitions.remove(transition)
                        break
            else:
                tower.transitions.remove((state, "SEE_GRAPH_MANAGER", tower.base_state))

                # assert(counter == 1)
        system = minimized_rolled_system
        print("FINISHED LOOP")
        gm.reset_globals()
    # for tower in system:
    for index, tower in enumerate(final_traces):
        print("index " + str(index) + "\n" + str(tower))
    #chop off timestamp node
    #send it back through
    # while(True):
    #     graph_manager.do_round()

# takes in a list of reworkedgraphs
# should return a minimized list of traces

def check_if_finished(traces):
    for trace in traces:
        if len(trace[0].request_vector) > 0:
            return False
    return True

# TODO one issue: I am getting a system from run_minimizing_mvp and then getting the trace for each tower. What would be better is to just get the traces outright
def get_minimized_traces_from_system(system):
    minimized_traces = gm.run_minimizing_mvp(system, rollout_index=ROLLOUT_INDEX, return_traces=True)[5]
        #debugging trace_per_tower
    for trace in minimized_traces:
        gm.print_formatted_trace_path(trace)
    #build it out from current timestep
    return minimized_traces


def initialize_globals(rollout_index):
    ROLLOUT_INDEX = rollout_index
