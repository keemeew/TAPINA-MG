import heapq
import random
import time
from itertools import permutations
from unittest import result
import random
import numpy as np
import math
import heapq
import copy
from collections import deque

def generate_apps(num,Hosts):
    Apps = []
    worker_list = []
    while len(Apps) < num:
        random.shuffle(Hosts)
        worker_num = np.random.randint(3,7)
        model_size = np.random.randint(1,20)
        worker_list.append(Hosts[0:worker_num])
        # worker_list.append(list(np.random.choice(Hosts, worker_num)))
        worker_list.append(model_size)
        if worker_list not in Apps:
            Apps.append(worker_list)
        worker_list = []
#    print(Apps)
    return Apps

def generate_apps_zipf(num,Hosts,zipf):
    Apps = []
    worker_list = []
    while len(Apps) < num:
        random.shuffle(Hosts)
        worker_num = np.random.randint(3,7)
        model_size = np.random.zipf(a=zipf,size=1)[0]
        worker_list.append(Hosts[0:worker_num])
        worker_list.append(model_size)
        if worker_list not in Apps:
            Apps.append(worker_list)
        worker_list = []
    return Apps

def dijkstra(graph,start,end):
    distances = {node: float('inf') for node in graph}
    distances[start] = 0 
    queue = []
    heapq.heappush(queue, [distances[start], start]) 
    while queue:  
        current_distance, current_destination = heapq.heappop(queue)  
        if distances[current_destination] < current_distance:
            continue
        for new_destination, new_distance in graph[current_destination].items():
            distance = current_distance + new_distance 
            if distance < distances[new_destination]:  
                distances[new_destination] = distance
                heapq.heappush(queue, [distance, new_destination])  
    return distances[end]

def avg_distance(graph,application,switch):
    sum = 0
    for node in application[0]:
        sum += dijkstra(graph, node, switch)
    return sum/len(application[0])

def max_distance(graph,application,switch):
    maxdist = 0
    for node in application[0]:
        current_distance = dijkstra(graph, node, switch)
        if maxdist < current_distance:
            maxdist = current_distance
    return maxdist

def inflight(graph,application,switch):
    return avg_distance(graph, application, switch)*len(application[0])*application[1]


def Divide(a, b, start):
    r_lst = [] 
    if b != 1: 
        for s in range(start, int(a / b) + 1):
            div_lst = Divide(a - s, b - 1, s)
            for lst in div_lst: 
                r_lst.append([s] + lst)
    else:
        r_lst.append([a])
    return r_lst

def find_best_switch(graph,App,Switches):
    best_val = float("inf")
    best_switch = ''
    for i in range (0,len(Switches)):
        intermediate = 0
        intermediate = inflight(graph, App, Switches[i])
        if intermediate < best_val:
            best_val = intermediate
            best_switch = Switches[i]
    return best_switch

def find_worst_switch(graph,switch_list):
    best_val = float("inf")
    worst_sw = ''
    for i in range (0,len(switch_list)):
        intermediate = 0
        for k in range (1,len(switch_list[i])):
            # intermediate += switch_list[i][k][-1]*(len(switch_list[i][k][0]))
            intermediate += (inflight(graph,switch_list[i][k],'PS')-inflight(graph,switch_list[i][k],switch_list[i][0]))
        if intermediate < best_val:
            best_val = intermediate
            worst_sw = switch_list[i]
    return worst_sw

def find_best_app(Apps):
    best_val = 0
    best_App = ''
    for i in range (0,len(Apps)):
        intermediate = 0
        intermediate = Apps[i][-1]*(len(Apps[i][0]))
        if intermediate > best_val:
            best_val = intermediate
            best_App = Apps[i]
    return best_App

def find_worst_app(Apps):
    best_val = float("inf")
    best_App = ''
    for i in range (0,len(Apps)):
        intermediate = 0
        intermediate = Apps[i][-1]*(len(Apps[i][0]))
        if intermediate < best_val:
            best_val = intermediate
            best_App = Apps[i]
    return best_App

def heuristic(graph,Apps,Switches,k,memory_cons,dist_thresh):
    for i in range (0,len(Apps)):
        Apps[i][1] = Apps[i][1]*len(Apps[i][0])
    Apps.sort(key=lambda x: (-x[1], x[0]))
    # random.shuffle(Apps)
    # Apps.sort(key=lambda x: (x[1], x[0]))
    for i in range (0,len(Apps)):
        Apps[i][1] = int(Apps[i][1]/len(Apps[i][0]))
    #print(Apps)
    dist_thresh = dist_thresh
    sel_sw = ''
    Selected_SW = []
    all_switches = []
    Switch_list = []
    App_rejected = []
    result = 0
    start_time = time.time()
    for i in range (0,len(Switches)):
        all_switches.append(Switches[i])
    #Switches.append('PS')
    node_cnt = 0
    for i in range (0,len(Apps)): 
        # print(Apps[i])
        if node_cnt == 0:
            # print(all_switches)
            Selected_SW.append([find_best_switch(graph,Apps[i],all_switches)])
            Selected_SW[-1].append(Apps[i])
            # if find_best_switch(graph,Apps[i],Switches) != 'PS':
            Switch_list.append(find_best_switch(graph,Apps[i],all_switches))
            node_cnt += 1
            sel_sw = find_best_switch(graph,Apps[i],all_switches)
        else:
            if len(Switch_list) != 0:
                if avg_distance(graph,Apps[i],find_best_switch(graph,Apps[i],Switch_list)) <= dist_thresh:
                    for t in range (0, len(Selected_SW)):
                        if Selected_SW[t][0] == find_best_switch(graph,Apps[i],Switch_list):
                            Selected_SW[t].append(Apps[i])
                    sel_sw = find_best_switch(graph,Apps[i],Switch_list)
                else:
                    if node_cnt < k:
                        # print(find_best_switch(graph,Apps[i],all_switches))
                        if find_best_switch(graph,Apps[i],all_switches) not in Switch_list:
                            Selected_SW.append([find_best_switch(graph,Apps[i],all_switches)])
                            Selected_SW[-1].append(Apps[i])
                            Switch_list.append(find_best_switch(graph,Apps[i],all_switches))
                            node_cnt += 1
                            sel_sw = find_best_switch(graph,Apps[i],Switches)
                        else:
                            for t in range (0, len(Selected_SW)):
                                if Selected_SW[t][0] == find_best_switch(graph,Apps[i],all_switches):
                                    Selected_SW[t].append(Apps[i])
                            sel_sw = find_best_switch(graph,Apps[i],all_switches)                            
                    else:
                        for t in range (0, len(Selected_SW)):
                            if Selected_SW[t][0] == find_best_switch(graph,Apps[i],Switch_list):
                                Selected_SW[t].append(Apps[i])
                        sel_sw = find_best_switch(graph,Apps[i],Switch_list)
            else:
                if node_cnt < k:
                    Selected_SW.append([find_best_switch(graph,Apps[i],all_switches)])
                    Selected_SW[-1].append(Apps[i])
                    Switch_list.append(find_best_switch(graph,Apps[i],all_switches))
                    node_cnt += 1
                    sel_sw = find_best_switch(graph,Apps[i],Switches)
                else:
                    App_rejected.append(Apps[i])
        for j in range(0,len(Selected_SW)):
            if sel_sw != '' and Selected_SW[j][0] == sel_sw:
                if len(Selected_SW[j])-1 >= memory_cons and Selected_SW[j][0] in Switch_list:
                    # print(print(Selected_SW[j][0]))
                    all_switches.remove(Selected_SW[j][0])
                    Switch_list.remove(Selected_SW[j][0])
        sel_sw = ''
    for i in range (0,len(Selected_SW)):
        for p in range (1,len(Selected_SW[i])):
            result += inflight(graph, Selected_SW[i][p], Selected_SW[i][0])
    for i in range (0,len(App_rejected)):
        result += inflight(graph,App_rejected[i],'PS')
    end_time = time.time()
    time_diff = end_time - start_time
    print('Case: heuristic')
    for i in range (0,len(Selected_SW)):    
        print('Selected switch:',Selected_SW[i][0])       
        print('App allocation:',Selected_SW[i][1:])        
    print('PS Apps:',App_rejected)  
    print('Inflight:',result)
    print('TAPINA time:', time_diff)
    # print('-'*50)
    App_arr = [i for i in range(len(Apps))]
    for i in range (0,len(Apps)):
        App_arr[i] = Apps[i] 
    # for i in range (0,len(Apps)):
    #     App_arr[i][1] = App_arr[i][1]*len(App_arr[i][0])
    return int(result)

def preference_lists_for_tenants(graph,Apps,Switches):
    
    switch_list = []
    prefer_list = []
    for i in range (0,len(Apps)):
        prefer_list.append([Apps[i]])
    
    for i in range (0,len(Apps)):
        for k in range (0,len(Switches)):
            switch_list.append(Switches[k])
        while switch_list != []:
            nowswitch = find_best_switch(graph,Apps[i],switch_list)
            prefer_list[i].append(nowswitch)
            switch_list.remove(nowswitch)
    
    # print(prefer_list)
    return prefer_list

def preference_lists_for_switches(Apps):
    
    app_list = []
    prefer_list = []
    
    for k in range (0,len(Apps)):
        app_list.append(Apps[k])
    while app_list != []:
        nowapp = find_best_app(app_list)
        prefer_list.append(nowapp)
        app_list.remove(nowapp)

    # print(prefer_list)
    return prefer_list

def deferred_acceptance(graph,Apps,Switches,memory_const):
    
    app_list = []
    switch_list = []
    rejected_list = []
    
    preference_tenants = preference_lists_for_tenants(graph,Apps,Switches)
    for k in range (0,len(Apps)):
        app_list.append(Apps[k])
        
    for k in range (0,len(Switches)):
        switch_list.append([Switches[k]])
    
    while app_list != []:
        current_app = app_list[0]
        app_idx = Apps.index(current_app)
        if len(preference_tenants[app_idx])-1 != 0:
            switch_choice = preference_tenants[app_idx][1]
            switch_idx = Switches.index(switch_choice)
        else: 
            rejected_list.append(current_app)
            app_list.remove(current_app)
            continue
        
        if len(switch_list[switch_idx])-1 < memory_const:
            switch_list[switch_idx].append(preference_tenants[app_idx][0])
            app_list.remove(current_app)
        else:
            remove_list = []
            for i in range (0,len(switch_list[switch_idx])-1):
                if int(switch_list[switch_idx][i+1][-1]*len(switch_list[switch_idx][i+1][0])) < int(preference_tenants[app_idx][0][-1]*len(preference_tenants[app_idx][0][0])):
                    remove_list.append(switch_list[switch_idx][i+1])
            if remove_list != []:
                remove_app = find_worst_app(remove_list)
                preference_tenants[Apps.index(remove_app)].remove(switch_list[switch_idx][0])
                switch_list[switch_idx].remove(remove_app)
                app_list.append(remove_app)
            if len(switch_list[switch_idx])-1 < memory_const:
                switch_list[switch_idx].append(preference_tenants[app_idx][0])
                app_list.remove(current_app)
            else:
                preference_tenants[Apps.index(current_app)].remove(switch_list[switch_idx][0])
    
    result = 0
    for i in range (0,len(switch_list)):
        for p in range (1,len(switch_list[i])):
            result += inflight(graph, switch_list[i][p], switch_list[i][0])
    for i in range (0,len(rejected_list)):
        result += inflight(graph,rejected_list[i],'PS')
    
    # print(switch_list)
    # print(rejected_list)
    # print(result)
    
    return switch_list, rejected_list

def matching_with_second_round(graph,Apps,Switches,k,memory_const):
    start_time = time.time()
    switch_list, rejected_list = deferred_acceptance(graph,Apps,Switches,memory_const)
    
    selected_switches = []
    selected_switch_list = []
    
    for i in range (0,len(switch_list)):
        if len(switch_list[i])-1 > 0:
            selected_switches.append(switch_list[i])
    
    while len(selected_switches) > k:
        remove_switch = find_worst_switch(graph,selected_switches)
        selected_switches.remove(remove_switch)
        for i in range (1,len(remove_switch)):
            rejected_list.append(remove_switch[i])
    
    for i in range (0, len(selected_switches)):
        selected_switch_list.append(selected_switches[i][0])
    
    switch_list_final, rejected_list_final = deferred_acceptance(graph,Apps,selected_switch_list,memory_const)
    
    result = 0
    for i in range (0,len(switch_list_final)):
        for p in range (1,len(switch_list_final[i])):
            result += inflight(graph, switch_list_final[i][p], switch_list_final[i][0])
    for i in range (0,len(rejected_list_final)):
        result += inflight(graph,rejected_list_final[i],'PS')
    
    end_time = time.time()
    print('Case: Matching')
    for i in range (0,len(switch_list_final)):    
        print('Selected switch:',switch_list_final[i][0])       
        print('App allocation:',switch_list_final[i][1:])        
    print('PS Apps:',rejected_list_final)  
    print('Inflight:',result)
    print("TAPINA-MG time:",end_time-start_time)
    
    return int(result)
    
def matching_with_second_round_w_time(graph,Apps,Switches,k,memory_const):
    start_time = time.time()
    switch_list, rejected_list = deferred_acceptance(graph,Apps,Switches,memory_const)
    
    selected_switches = []
    selected_switch_list = []
    
    for i in range (0,len(switch_list)):
        if len(switch_list[i])-1 > 0:
            selected_switches.append(switch_list[i])
    
    while len(selected_switches) > k:
        remove_switch = find_worst_switch(graph,selected_switches)
        selected_switches.remove(remove_switch)
        for i in range (1,len(remove_switch)):
            rejected_list.append(remove_switch[i])
    
    for i in range (0, len(selected_switches)):
        selected_switch_list.append(selected_switches[i][0])
    
    switch_list_final, rejected_list_final = deferred_acceptance(graph,Apps,selected_switch_list,memory_const)
    
    result = 0
    for i in range (0,len(switch_list_final)):
        for p in range (1,len(switch_list_final[i])):
            result += inflight(graph, switch_list_final[i][p], switch_list_final[i][0])
    for i in range (0,len(rejected_list_final)):
        result += inflight(graph,rejected_list_final[i],'PS')
    
    end_time = time.time()
    time_diff = end_time-start_time
    print('Case: Matching')
    for i in range (0,len(switch_list_final)):    
        print('Selected switch:',switch_list_final[i][0])       
        print('App allocation:',switch_list_final[i][1:])        
    print('PS Apps:',rejected_list_final)  
    print('Inflight:',result)
    print("TAPINA-MG time:",time_diff)
    
    return int(result), time_diff
    
def ep_value(app):
    return app[1] * len(app[0])

def solution_set_traffic(graph, solution_set, rejected_apps=None):
    result = 0
    for group in solution_set:
        sw = group[0]
        for app in group[1:]:
            result += inflight(graph, app, sw)

    if rejected_apps is not None:
        for app in rejected_apps:
            result += inflight(graph, app, 'PS')

    return int(result)
