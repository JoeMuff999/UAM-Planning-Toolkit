#!/usr/bin/env python
# coding: utf-8

# In[1]:


# purpose: determine how synthesis time changes with tower # and max # requests
# for a system with n towers, determine its synthesis time for 1 through x request max
import sys
import os
# sys.path.insert(0, os.path.abspath('C:\\Users\\Joey\\PycharmProjects\\Automata-Testing'))
import copy
import optimization_functions
import graph_manager
import graph_test_methods
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
# os.environ["PATH"] += os.pathsep + 'C:/Program Files/Graphviz 2.44.1/bin'


# In[2]:


TOWER_MIN = 3
TOWER_MAX = 8
REQUEST_MIN = 1
REQUEST_MAX = 8
RUNS_PER_DATA_POINT = 5
# TOWER_MIN = 3
# TOWER_MAX = 4
# REQUEST_MIN = 4
# REQUEST_MAX = 5
# RUNS_PER_DATA_POINT = 2


# In[3]:


average_runtime_per_tower_per_request_max = list()
runtime_per_tower_per_request_max = list()
optimization_functions.set_seed(10)
system_timings = list()
cost_vecs = list()
for tower_count in range(TOWER_MIN, TOWER_MAX):
    average_runtime_per_tower_per_request_max.append([])
    runtime_per_tower_per_request_max.append([])
    system_timings.append([])
    #cost_vecs.append([])
    for request_max in range(REQUEST_MIN, REQUEST_MAX):
        average_runtime_per_tower_per_request_max[tower_count-TOWER_MIN].append(0)
        runtime_per_tower_per_request_max[tower_count-TOWER_MIN].append([])
        system_timings[tower_count-TOWER_MIN].append([])
        #cost_vecs.append([])
        for index in range(RUNS_PER_DATA_POINT):
            system = optimization_functions.get_randomized_system(
                num_towers=tower_count,
                request_min=REQUEST_MIN,
                request_max=request_max
            )
            runtime, num_rounds, minimized_cost_vec_list,sys_timing,cost_vec_per_round = graph_manager.run_minimizing_mvp(system, rollout_index=0)
            #cost_vecs[tower_count-TOWER_MIN][request_max-REQUEST_MIN].append(cost_vec_per_round)
            system_timings[tower_count-TOWER_MIN][request_max-REQUEST_MIN].append(copy.deepcopy(sys_timing))
            average_runtime_per_tower_per_request_max[tower_count-TOWER_MIN][request_max-REQUEST_MIN] += runtime/RUNS_PER_DATA_POINT
            runtime_per_tower_per_request_max[tower_count-TOWER_MIN][request_max-REQUEST_MIN].append(runtime)
            graph_manager.reset_globals()
            
# print(average_runtime_per_tower_per_request_max)
#print(system_timings)


# In[4]:


data_buffer = copy.deepcopy(average_runtime_per_tower_per_request_max)
std_buffer = copy.deepcopy(runtime_per_tower_per_request_max)
timings_buffer = copy.deepcopy(system_timings)
#cost_buffer = copy.deepcopy(cost_vecs)


# In[5]:


data = open("C:\\Users\\Joey\\PycharmProjects\\Automata-Testing\\data\\base_results_new.txt", "w")
data.write("run_index,num_towers,max_num_requests,average_runtime\n")
run_index = 0

for num_towers, tower in enumerate(data_buffer, start=TOWER_MIN):
    for index in range(len(tower)):
        data.write(str(run_index) + "," +
              str(num_towers) + "," +
              str(index + REQUEST_MIN) + "," +
              str(tower[index]) + "\n"
             )
data.close()


# In[70]:


#calculate standard deviations
std_deviation_per_tower_per_request_max = list()
for tower_num in range(TOWER_MIN, TOWER_MAX):
    std_deviation_per_tower_per_request_max.append([])
    for request_max in range(REQUEST_MIN, REQUEST_MAX):
        std_deviation_per_tower_per_request_max[tower_num- TOWER_MIN].append(np.std(std_buffer[tower_num- TOWER_MIN][request_max - REQUEST_MIN]))



x = [i for i in range(REQUEST_MIN, REQUEST_MAX)]
for i in range(len(data_buffer)):
    label = str(i + TOWER_MIN)
    plt.plot(x, data_buffer[i], label=label)
    #[test_list1[i] + test_list2[i] for i in range(len(test_list1))] 
    above_std = [std_deviation_per_tower_per_request_max[i][j] + data_buffer[i][j] for j in range(len(data_buffer[i]))]
    below_std = [data_buffer[i][j] - std_deviation_per_tower_per_request_max[i][j] for j in range(len(data_buffer[i]))]
    plt.fill_between(
        x, 
        above_std,
        below_std,
        alpha=0.2
     )


plt.xlabel('Max Number of Requests')
plt.xticks(x)
plt.ylabel('Runtime (s)')
plt.legend(title='Number of towers:')
plt.savefig('data\\runtime_vs_size.png',dpi=216)


# In[81]:


# reversed_data = std_buffer
# print(len(reversed_data))
# print(len(reversed_data[0][0]))

# reversed_data = np.transpose(std_buffer)
# print(len(reversed_data))
# print(len(reversed_data[0]))

reversed_data = np.transpose(np.asarray(std_buffer), axes=(1,0,2))
plt.figure(dpi=100)
plt.style.use('seaborn')
separation = 1/(REQUEST_MAX-REQUEST_MIN)
counter = 0
bp_per_tower = [[] for i in range(REQUEST_MAX-REQUEST_MIN)]
for i in range(len(reversed_data)):
    counter = 0
    for j in range(len(reversed_data[0])):
        bp = plt.boxplot(
            reversed_data[i][j],
            positions = [i+counter],
            vert=True,
            patch_artist=True,
            notch=False,
            widths=separation
        )
        counter += separation
        bp_per_tower[j].append(bp)
        
import matplotlib.patches as mpatches        
colors = ['lightyellow', 'lightsalmon','lightblue','pink','lightgreen']
patches = []
for num, color in enumerate(colors, start=TOWER_MIN):
    patches.append(mpatches.Patch(color=color, label=str(num)+" Towers"))
plt.legend(handles=patches)
color_index = 0
for tower_count in range(len(bp_per_tower)):
    for bp in bp_per_tower[tower_count]:        
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(colors[color_index])
    color_index+=1
        
plt.xlabel('Max Number of Requests')
x = [i for i in range(REQUEST_MIN, REQUEST_MAX)]
x_positions = [(i+.5) for i in range(REQUEST_MAX - REQUEST_MIN)]

ax = plt.axes()
ax.set_xticklabels(x)
ax.set_xticks(x_positions)
plt.ylabel('Runtime (s)')
plt.savefig('data\\runtime_vs_size_boxplot.png',dpi=216)


# In[243]:


#generate time for x requests for min through max towers
REQUESTS_TO_TEST = 5
REQUEST_INDEX = REQUESTS_TO_TEST - 1

RUNS_TO_DO = 15
graph_manager.reset_globals()
optimization_functions.set_seed(10)

timings_for_x_requests_per_tower = list()
for tower_count in range(TOWER_MIN, 11):
    timings_for_x_requests_per_tower.append([])
    for run in range(RUNS_TO_DO):   
        system = optimization_functions.get_randomized_system(
                num_towers=tower_count,
                request_min=REQUEST_MIN,
                request_max=REQUESTS_TO_TEST
            )
        runtime, num_rounds, minimized_cost_vec_list,sys_timing,cost_vec_per_round = graph_manager.run_minimizing_mvp(system, rollout_index=0)
        timings_for_x_requests_per_tower[tower_count - TOWER_MIN].append(copy.deepcopy(sys_timing))
        graph_manager.reset_globals()


# In[ ]:


graph_manager.reset_globals()
optimization_functions.set_seed(50)

for tower_count in range(TOWER_MIN, 11):
    timings_for_x_requests_per_tower.append([])
    for run in range(RUNS_TO_DO):   
        system = optimization_functions.get_randomized_system(
                num_towers=tower_count,
                request_min=REQUEST_MIN,
                request_max=REQUESTS_TO_TEST
            )
        runtime, num_rounds, minimized_cost_vec_list,sys_timing,cost_vec_per_round = graph_manager.run_minimizing_mvp(system, rollout_index=0)
        timings_for_x_requests_per_tower[tower_count - TOWER_MIN].append(copy.deepcopy(sys_timing))
        graph_manager.reset_globals()


# In[244]:


timings_for_x_requests_buffer = copy.deepcopy(timings_for_x_requests_per_tower)


# In[252]:


#time per round per tower vs. number of towers for 5 requests
#timings buffer, per number_towers per request_max per system per round per tower per type of timing 
#show average round runtime vs time number of towers for 5 request
TOWER_MAX = 11
# print(timings_for_x_requests_buffer)
round_times_per_tower_count = [[] for i in range(TOWER_MIN, TOWER_MAX)]
max_round_times_per_tower_count = [[] for i in range(TOWER_MIN, TOWER_MAX)]
round_count_per_tower_count =[[] for i in range(TOWER_MIN, TOWER_MAX)]
for tower_count in range(len(timings_for_x_requests_buffer)):
    for system_index in range(len(timings_for_x_requests_buffer[tower_count])):
        max_round_time = 0
        for round_index in range(len(timings_for_x_requests_buffer[tower_count][system_index])):
            for tower_index in range(len(timings_for_x_requests_buffer[tower_count][system_index][round_index])):
                    total_round_time = 0
                    total_round_time += timings_for_x_requests_buffer[tower_count][system_index][round_index][tower_index][0]
                    total_round_time += timings_for_x_requests_buffer[tower_count][system_index][round_index][tower_index][1]
                    round_times_per_tower_count[tower_count].append(total_round_time)
                    if total_round_time > max_round_time:
                        max_round_time = total_round_time
        max_round_times_per_tower_count[tower_count].append(max_round_time)
        round_count_per_tower_count[tower_count].append(len(timings_for_x_requests_buffer[tower_count][system_index]))
plt.figure(dpi=100)
plt.style.use('default')

for i in range(len(round_times_per_tower_count)):
        bp = plt.boxplot(
            round_times_per_tower_count[i],
            positions = [i],
            vert=True,
            patch_artist=True,
            notch=False,
            widths=separation
        )
        for box in bp['boxes']:
            box.set(color='lightgreen')

# data = np.transpose(std_buffer,axes=(1,0,2))
# for i in range(len(data[4])):
#         bp = plt.boxplot(
#             reversed_data[i][j],
#             positions = [i],
#             vert=True,
#             patch_artist=True,
#             notch=False,
#             widths=separation
#         )
#         for box in bp['boxes']:
#             box.set(color='lightgreen')


xlabels = [i for i in range(TOWER_MIN, TOWER_MAX)]
x_positions = [i for i in range(TOWER_MAX-TOWER_MIN)]
ax = plt.axes()
ax.set_xticklabels(xlabels)
ax.set_xticks(x_positions)
plt.ylabel('Runtime Per Iteration (s)')
plt.xlabel('Number of Vertihubs')
plt.savefig('data\\runtime_vs_size_boxplot_requests_static.png',dpi=1024)


# In[249]:


plt.figure(dpi=100)
plt.style.use('default')

plt.rcParams['xtick.labelsize']=18
plt.rcParams['ytick.labelsize']=18
for i in range(len(max_round_times_per_tower_count)):
        bp = plt.boxplot(
            max_round_times_per_tower_count[i],
            positions = [i],
            vert=True,
            patch_artist=True,
            notch=False,
            widths=separation,
             showfliers=False
        )
        for box in bp['boxes']:
            box.set(color='lightgreen')

# data = np.transpose(std_buffer,axes=(1,0,2))
# for i in range(len(data[4])):
#         bp = plt.boxplot(
#             reversed_data[i][j],
#             positions = [i],
#             vert=True,
#             patch_artist=True,
#             notch=False,
#             widths=separation
#         )
#         for box in bp['boxes']:
#             box.set(color='lightgreen')


xlabels = [i for i in range(TOWER_MIN, 11)]
x_positions = [i for i in range(TOWER_MAX-TOWER_MIN)]
ax = plt.axes()

ax.set_xticklabels(xlabels)
ax.set_xticks(x_positions)
plt.gcf().subplots_adjust(bottom=0.15)
plt.ylabel('Max Runtime Per Iteration (s)', fontsize=18)
plt.xlabel('Number of Vertihubs', fontsize=18)
plt.savefig('data\\max_runtime_vs_size_boxplot_requests_static.png',dpi=1024)


# In[284]:


#overlay iterations on the above plot
plt.figure(dpi=100)
plt.style.use('default')

plt.rcParams['xtick.labelsize']=18
plt.rcParams['ytick.labelsize']=18
average_iteration_per_tower = []
fig,ax1 = plt.subplots()
ax2 = ax1.twinx()
for i in range(len(max_round_times_per_tower_count)):
        bp = ax1.boxplot(
            max_round_times_per_tower_count[i],
            positions = [i-.1],
            vert=True,
            patch_artist=True,
            notch=False,
            widths=separation,
             showfliers=False
        )
        for box in bp['boxes']:
            box.set(color='lightgreen')
        bx = ax2.boxplot(
            round_count_per_tower_count[i],
            positions = [i+.15],
            vert=True,
            patch_artist=True,
            notch=False,
            widths=separation,
             showfliers=False
        )
        for box in bx['boxes']:
            box.set(color='lightblue')
patches = []
colors = ['lightgreen', 'lightblue']
patches.append(mpatches.Patch(color='lightgreen', label='Iterations vs Verithubs'))
patches.append(mpatches.Patch(color='lightblue', label='Runtime per Iteration vs Vertihubs', hatch='//'))

plt.legend(handles=patches)
#         average_iteration_per_tower.append(np.average(round_count_per_tower_count))
#         ax2.plot(i, np.average(round_count_per_tower_count[i]), 'b.', markersize=18)
# x_axis = [i for i in range(TOWER_MIN, TOWER_MAX)]
# plt.plot(x_axis, average_iteration_per_tower)
# plt.plot(max_round_times_per_tower_count[i])
# data = np.transpose(std_buffer,axes=(1,0,2))
# for i in range(len(data[4])):
#         bp = plt.boxplot(
#             reversed_data[i][j],
#             positions = [i],
#             vert=True,
#             patch_artist=True,
#             notch=False,
#             widths=separation
#         )
#         for box in bp['boxes']:
#             box.set(color='lightgreen')


xlabels = [i for i in range(TOWER_MIN, 11)]
x_positions = [i for i in range(TOWER_MAX-TOWER_MIN)]

ax1.set_xticklabels(xlabels)
ax1.set_xticks(x_positions)
plt.gcf().subplots_adjust(bottom=0.15)
ax1.set_ylabel('Max Runtime Per Iteration (s)', fontsize=18)
ax1.set_xlabel('Number of Vertihubs', fontsize=18)
ax2.set_ylabel('Average Iterations Per Round',fontsize=18)
plt.savefig('data\\max_runtime_vs_size_boxplot_requests_static_with_iterations.png',dpi=1024)


# In[253]:


for i in range(len(max_round_times_per_tower_count)):
        bp = plt.boxplot(
            round_count_per_tower_count[i],
            positions = [i],
            vert=True,
            patch_artist=True,
            notch=False,
            widths=separation,
             showfliers=False
        )
        for box in bp['boxes']:
            box.set(color='lightgreen')

# data = np.transpose(std_buffer,axes=(1,0,2))
# for i in range(len(data[4])):
#         bp = plt.boxplot(
#             reversed_data[i][j],
#             positions = [i],
#             vert=True,
#             patch_artist=True,
#             notch=False,
#             widths=separation
#         )
#         for box in bp['boxes']:
#             box.set(color='lightgreen')


xlabels = [i for i in range(TOWER_MIN, 11)]
x_positions = [i for i in range(TOWER_MAX-TOWER_MIN)]
ax = plt.axes()

ax.set_xticklabels(xlabels)
ax.set_xticks(x_positions)
plt.gcf().subplots_adjust(bottom=0.15)
plt.ylabel('Number of Iterations (s)', fontsize=18)
plt.xlabel('Number of Vertihubs', fontsize=18)
plt.savefig('data\\iteration_count_vs_size_boxplot_requests_static.png',dpi=1024)


# In[136]:


#cost per round graph -> show effectiveness of minimization
optimization_functions.set_seed(35)
graph_manager.reset_globals()
hand_system = optimization_functions.get_randomized_system(
    num_towers=6,
    request_min=1,
    request_max=5
)
runtime, num_rounds, minimized_cost_vec_list,sys_timing,cost_vec_per_round = graph_manager.run_minimizing_mvp(hand_system, rollout_index=0)


# In[137]:


specific_buffer = copy.deepcopy(cost_vec_per_round)
print(specific_buffer)


# In[151]:


level_0_cost_per_round = list()
level_1_cost_per_round = list()
for round_index in range(len(specific_buffer)):
    level_0_cost_per_round.append(0)
    level_1_cost_per_round.append(0)    
    for vec in specific_buffer[round_index]:
        level_0_cost_per_round[round_index] += vec[0]
        level_1_cost_per_round[round_index] += vec[1]
# plt.figure(dpi=40)
# x_axis = [i for i in range(num_rounds)]
# plt.step(x_axis, level_0_cost_per_round, label="level 0", where="post")
# plt.step(x_axis, level_1_cost_per_round, label="level 1",where="post")
# plt.xticks(x_axis)
# plt.xlabel("Iteration")
# plt.ylabel("Cost")
# plt.legend(title="Spec/Cost level")
# plt.savefig('data\\cost_vs_iteration.png',dpi=216)


# In[238]:


level_0_cost_per_tower_per_round = list()
level_1_cost_per_tower_per_round = list()


transposed_buffer = np.transpose(specific_buffer,axes=(1,0,2))
for tower_index in range(len(transposed_buffer)):
    level_0_cost_per_tower_per_round.append([])
    level_1_cost_per_tower_per_round.append([])
    for round_index in range(len(transposed_buffer[tower_index])):
        level_0_cost_per_tower_per_round[tower_index].append(transposed_buffer[tower_index][round_index][0])
        level_1_cost_per_tower_per_round[tower_index].append(transposed_buffer[tower_index][round_index][1])

plt.style.use('default')

plt.rcParams['xtick.labelsize']=18
plt.rcParams['ytick.labelsize']=18        

# subpltfig, ax = plt.subplots(3,2, sharex='row', sharey='col')
x_ticks = np.arange(0,5,1)
y_ticks = np.arange(0,4,1)
for i in range(len(level_0_cost_per_tower_per_round)):
    dummy_fig,dummy_ax = plt.subplots()
    dummy_ax.plot(x_axis, level_0_cost_per_tower_per_round[i], label="level 0")
    dummy_ax.plot(x_axis, level_1_cost_per_tower_per_round[i], label="level 1",linestyle='--')
    dummy_ax.legend(title="Level of Cost",fontsize=12)
    dummy_ax.set_xlabel("Iteration",fontsize=18)
    dummy_ax.set_ylabel("Cost",fontsize=18)
    dummy_ax.set_xticks(x_ticks)
    dummy_ax.set_yticks(y_ticks)

#     dummy_ax.set_xticklabels(x_axis)
#     dummy_ax.set_yticklabels([i for i in range(0,3)])


    plt.savefig('data\\cost_vs_iteration\\cost_vs_iteration_' + str(i) + '.png',dpi=1024,Transparent=True)

dummy_fig,dummy_ax = plt.subplots()
dummy_ax.plot(x_axis, level_0_cost_per_round, label="level 0")
dummy_ax.plot(x_axis, level_1_cost_per_round, label="level 1",linestyle='--')
dummy_ax.legend(title="Level of Cost",fontsize=12)
dummy_ax.set_xlabel("Iteration",fontsize=18)
dummy_ax.set_ylabel("Cost",fontsize=18)
# x_ticks_big = np.arange(0)
y_ticks_big = np.arange(0,13,2)
dummy_ax.set_yticks(y_ticks_big)
dummy_ax.set_xticks(x_ticks)
plt.savefig('data\\cost_vs_iteration\\cost_vs_iteration_big_fig.png',dpi=1024,Transparent=True)

# dummy_ax.set_xticklabels(x_axis)
# dummy_ax.set_yticklabels([i for i in range(0,12)])


# In[241]:



plt.rcParams['xtick.labelsize']=15
plt.rcParams['ytick.labelsize']=15
main_figure = plt.figure(dpi=216, constrained_layout=True)
gs = main_figure.add_gridspec(3,3)

rows = 1
cols = 0
for i in range(len(level_0_cost_per_tower_per_round)):
    ax = main_figure.add_subplot(gs[rows,cols])
    ax.plot(x_axis, level_0_cost_per_tower_per_round[i], label="level 0 cost for tower " + str(i))
    ax.plot(x_axis, level_1_cost_per_tower_per_round[i], label="level 1 cost for tower " + str(i),linestyle='--')
    rows = rows = 1 if rows >=2 else rows+1
    cols = cols = 0 if cols >=2 else cols+1
    ax.set_xticks(x_ticks)
    ax.set_yticks(y_ticks)

    #ax[rows][cols].set_yticklabels([i for i in range(0, 4)])

big_ax = main_figure.add_subplot(gs[0, :])
big_ax.plot(x_axis, level_0_cost_per_round, label="Level 0")
big_ax.plot(x_axis, level_1_cost_per_round, label="Level 1", linestyle='--')

big_ax.legend(title="Level of Cost")
big_ax.set_xlabel("Iteration",fontsize=18)
big_ax.set_ylabel("Cost",fontsize=18)
big_ax.set_xticks(x_ticks)
y_ticks_big = np.arange(0,13,3)
big_ax.set_yticks(y_ticks_big)
plt.savefig('data\\cost_vs_iteration\\cost_vs_iteration_compiled.png',dpi=1024)
# plt.step(x_axis, level_0_cost_per_round, label="level 0", where="post")
# plt.step(x_axis, level_1_cost_per_round, label="level 1",where="post")
# plt.xticks(x_axis)
# plt.xlabel("Iteration")
# plt.ylabel("Cost")
# plt.legend(title="Spec/Cost level")


# In[ ]:


#large centralized system
import time

time_start = time.perf_counter()

