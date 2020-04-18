import numpy as np
import csv
import threading
import time
import queue

def shortest_path(graph, v1, v2, t):

    INF = float("inf")
    row_num = len(graph)
    col_num = len(graph[0])

    l_d_1 = v1[0] + v1[1] * col_num
    l_u_1 = v1[0] + col_num * row_num - (v1[1] - 1) * (col_num)
    r_d_1 = (col_num - v1[0]) + v1[1] * col_num
    r_u_1 = col_num * row_num - (v1[1] - 1) * (col_num) + (col_num - v1[0])

    l_d_2 = v2[0] + v2[1] * col_num
    l_u_2 = v2[0] + col_num * row_num - (v2[1] - 1) * (col_num)
    r_d_2 = (col_num - v2[0]) + v2[1] * col_num
    r_u_2 = col_num * row_num - (v2[1] - 1) * (col_num) + (col_num - v2[0])
        

    dist_arr = np.full((row_num, col_num), INF)

    method_list = [l_d_1, l_u_1, r_d_1, r_u_1, l_d_2, l_u_2, r_d_2, r_u_2]

    min_method = 0

    for i in range(len(method_list)):
        if method_list[i] < method_list[min_method]:
            min_method = i

        
    if min_method <= 3: # 1 is start
        dist_arr[v1] = 0
        current_v = v2
        min_v = v2
        target_v = v1
    else: # 2 is start
        dist_arr[v2] = 0
        current_v = v1
        min_v = v1
        target_v = v2
    
    while True:
        Flag = False
        for i in range(row_num):
            if min_method in [2, 3, 6, 7]:
                i = row_num - i - 1
            for j in range(col_num):
                if min_method in [1, 3, 5, 7]:
                    j = col_num - j - 1
                if i != 0:
                    if dist_arr[i - 1, j] + graph[i, j] < dist_arr[i, j]:
                        dist_arr[i, j] = dist_arr[i - 1, j] + graph[i, j]
                        Flag = True
                if i != row_num - 1:
                    if dist_arr[i + 1, j] + graph[i, j] < dist_arr[i, j]:
                        dist_arr[i, j] = dist_arr[i + 1, j] + graph[i, j]
                        Flag = True
                if j != 0:
                    if dist_arr[i, j - 1] + graph[i, j] < dist_arr[i, j]:
                        dist_arr[i, j] = dist_arr[i, j - 1] + graph[i, j]
                        Flag = True
                if j != col_num - 1:
                    if dist_arr[i, j + 1] + graph[i, j] < dist_arr[i, j]:
                        dist_arr[i, j] = dist_arr[i, j + 1] + graph[i, j]
                        Flag = True
        if Flag == False:
            break

    path = []

    while True:
        # print(current_v)
        if current_v == target_v:
            break
        if current_v[0] != 0:
            if dist_arr[current_v[0] - 1, current_v[1]] < dist_arr[min_v]:
                min_v = (current_v[0] - 1, current_v[1])
        if current_v[0] != row_num - 1:
            if dist_arr[current_v[0] + 1, current_v[1]] < dist_arr[min_v]:
                min_v = (current_v[0] + 1, current_v[1])
        if current_v[1] != 0:
            if dist_arr[current_v[0], current_v[1] - 1] < dist_arr[min_v]:
                min_v = (current_v[0], current_v[1] - 1)
        if current_v[1] != col_num - 1:
            if dist_arr[current_v[0], current_v[1] + 1] < dist_arr[min_v]:
                min_v = (current_v[0], current_v[1] + 1)
        current_v = min_v
        path.append(current_v)
    
    if min_method <= 3:
        path.reverse()
    # print("path:", path)
    return path

    '''
    total_t = 0
    if min_method <= 3:
        for i in range(len(path)):
            if total_t >= t:
                return path[-1 - i]
            total_t += graph[path[-1 - i]]
        return path[0]
    else:
        for i in range(len(path)):
            if total_t >= t:
                return path[i]
            total_t += graph[path[i]]
        return path[-1]
    '''


class Graph:
    def __init__(self, fp):
        f = open(fp, "r")
        reader = csv.reader(f)
        self.s_graph = []
        for row in reader:
            self.s_graph.append(row)
        f.close()
        self.s_graph = np.array(self.s_graph)
        
        self.row_num = len(self.s_graph)
        self.col_num = len(self.s_graph[0])

        self.t_graph = np.zeros((self.row_num, self.col_num))
        
        for i in range(self.row_num):
            for j in range(self.col_num):
                if self.s_graph[i, j] == "0":
                    self.t_graph[i, j] = self._t_p(0)
                else:
                    self.t_graph[i, j] = 9999999
        self.p_graph = np.zeros((self.row_num, self.col_num))

    def update(self, loc_before, loc_after):
        if loc_before == None:
            pass
        else:
            self.p_graph[loc_before] -= 1
            self.t_graph[loc_before] = self._t_p(self.p_graph[loc_before])
        if loc_after == None:
            pass
        else:
            self.p_graph[loc_after] += 1
            self.t_graph[loc_after] = self._t_p(self.p_graph[loc_after])
    
    def save(self, fp):
        np.save(fp, self.p_graph)

    def _t_p(self, p_num):
        return p_num + 1

class Person(threading.Thread):
    def __init__(self, target_vs, my_v, qArray, lockArray): # target_vs: [{sid: xx, loc: (xx,xx)}]
        super(Person, self).__init__()
        self.target_vs = target_vs
        self.my_v = my_v
        self.qArray = qArray
        self.lockArray = lockArray

    def run(self, t = 1):
        # print(self.my_v)
        #print(threading.current_thread().name,  " -- self.target_vs = ", self.target_vs, "\n")
        while True:
            global G, sname_quan
            if self.target_vs != []:
                loc_before = self.my_v
                vertex_list = shortest_path(G.t_graph, self.my_v, (self.target_vs[0]["loc"][0], self.target_vs[0]["loc"][1]), t)
                for i in range(len(vertex_list)):
                    self.my_v = vertex_list[i]                    
                    self.lockArray[0].acquire()
                    self.qArray[0].put(
                        str({"name": threading.current_thread().name, "mode": "loc", "forward": "go", "loc_before": loc_before, "loc_after": self.my_v})
                    )

                    # print(G.s_graph[self.my_v], self.target_vs[0]["sid"])
                    if G.s_graph[self.my_v] == self.target_vs[0]["sid"]:
                        if sname_quan[self.target_vs[0]["sname"]] == 0:
                            self.qArray[0].put(
                                str({"name": threading.current_thread().name, "mode": "dispute"})
                            )
                        else:
                            self.qArray[0].put(
                                str({"name": threading.current_thread().name, "mode":"buy", "prod": self.target_vs[0]["sname"]})
                            )
                        self.lockArray[0].release()
                        self.target_vs.pop(0)
                        break
                    self.lockArray[0].release()
                    if i < len(vertex_list) - 1 and G.t_graph[vertex_list[i + 1 ]] >= 3 and G.t_graph[vertex_list[i + 1 ]] < 100:
                        break
                    loc_before = self.my_v
                    
            else:
                Flag = False
                loc_before = self.my_v
                vertex_list = shortest_path(G.t_graph, self.my_v, (78, 38), t)
                for i in range(len(vertex_list)):
                    self.my_v = vertex_list[i]
                    self.lockArray[0].acquire()
                    self.qArray[0].put(
                        str({"name": threading.current_thread().name, "mode": "loc", "forward": "come", "loc_before": loc_before, "loc_after": self.my_v})
                    )

                    if self.my_v == (78, 38):
                        self.qArray[0].put(
                            str({"name": threading.current_thread().name, "mode": "done"})
                        )
                        Flag = True
                        self.lockArray[0].release()                    
                        break
                    self.lockArray[0].release()
                    if i < len(vertex_list) - 1 and G.t_graph[vertex_list[i + 1 ]] >= 3 and G.t_graph[vertex_list[i + 1 ]] < 100:
                        break
                    loc_before = self.my_v
                    
                if Flag == True:
                    break

if __name__ == "__main__":
    
    qArray = []
    lockArray = []
    for i in range(1):
        qArray.append(queue.Queue())
        lockArray.append(threading.Lock())
    
    G = Graph("shelf.csv")

    f = open("center.csv", "r")
    reader = csv.reader(f)
    centers = []
    for row in reader:
        centers.append(row)
    f.close()
    for i in range(len(centers)):
        for j in range(len(centers[0])):
            centers[i][j] = int(float(centers[i][j]))
    centers = np.array(centers)



    f = open("popularity.csv", "r")
    reader = csv.reader(f)
    popularity = []
    for row in reader:
        popularity.append(row)
    f.close()
    popularity = np.array(popularity)

    sname_quan = {}
    for i in range(len(popularity)):
        sname_quan.update({popularity[i][2]: int(popularity[i][3])})

    Population = []

    dispute_times = 0

    PEOPLE_NUMBER = 100

    counter = 0
    while counter < PEOPLE_NUMBER:
        for i in range(134):
            if counter >= PEOPLE_NUMBER:
                break
            loc = centers[int(popularity[i][1]) - 1]
            sid = popularity[i][1]
            sname = popularity[i][2]
            P = Person([{"loc": loc, "sid": sid, "sname": sname}], (95, 68), qArray, lockArray)
            G.update(None, (95, 68))
            Population.append(P)
            counter += 1

    for person in Population:
        person.start()

    finished = 0
    counter = 0
    loop_time = 0
    while True:
        if counter == PEOPLE_NUMBER:
            G.save(str(loop_time) + ".npy")
            loop_time += 1
            counter = 0

        if finished == PEOPLE_NUMBER:
            break
        
        # queueLock.acquire()
        for i in range(1):
            q = qArray[i]
            if not q.empty():
                message = q.get()
                message = eval(message)
                # print(message)
                if message["mode"] == "loc":
                    G.update(message["loc_before"], message["loc_after"])
                    counter += 1
                elif message["mode"] == "dispute":
                    dispute_times += 1
                elif message["mode"] == "buy":
                    sname_quan[message["prod"]] -= 1
                elif message["mode"] == "done":
                    finished += 1

    print(dispute_times)
    f = open("dist", "w")
    f.write("people num: " + str(PEOPLE_NUMBER) + "\n")
    f.write("dispute: " + str(dispute_times) + "\n")
    f.close()
