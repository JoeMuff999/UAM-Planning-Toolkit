# class for the main loop of the "simulation"
import reworked_graph
import graph_manager

ROLLOUT_INDEX = 2 #how far back to go when doing rollout. an index of 0 is the least level of optimization. if index >= len(trace), will default to 0

def main_loop(system, rollout_index=ROLLOUT_INDEX):
    #initialization stuff:
    initialize_globals(rollout_index=ROLLOUT_INDEX)
    system = get_minimized_traces_from_system(system)

    while(True):
        graph_manager.do_round()

# takes in a list of reworkedgraphs
# should return a minimized list of traces
def get_minimized_traces_from_system(system):
    #TODO one issue: I am getting a system from run_minimizing_mvp and then getting the trace for each tower. What would be better is to just get the traces outright
    minimized_system = graph_manager.run_minimizing_mvp(system, ROLLOUT_INDEX)[5]



def initialize_globals(rollout_index):
    ROLLOUT_INDEX = rollout_index