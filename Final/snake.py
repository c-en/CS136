import marketLinear
import numpy as np
import random
import gen_test

def snake(agents, objects, availabilities, values, complements, capacities):
    # randomly order agents
    a = range(len(agents))
    random.shuffle(a)
    allocation = [[] for _ in agents]
    demand = np.array([0]*len(objects))
    complete = [False] * len(agents)
    allocation = [np.array([0]*len(objects)) for _ in agents]
    forced = False
    while False in complete:
        done = []
        for i in a:
            if not forced:
                p = np.zeros(len(objects))
                for j, d in enumerate(demand):
                    if d >= availabilities[1][j] and not allocation[i][j] == 1:
                        p[j] = 101
                    else:
                        p[j] = 0
            else:
                p = np.zeros(len(objects))
                hours_needed = availabilities[0]-demand
                for j, d in enumerate(demand):
                    if  hours_needed[j] <= 0 and not allocation[i][j] == 1:
                        p[j] = 101
                    else:
                        p[j] = 0
            value = np.array(values[j])
            for j, d in enumerate(allocation[i]):
                s = np.sum(values[i]) + np.sum(complements[i])
                if d == 1:
                    value[j] = 1000
            agent = marketLinear.AgentLinear(objects, value, complements[i], capacities[i], 100)
            tempalloc = agent.demand(p)
            if np.array_equal(tempalloc,allocation[i]):
                complete[i] = True
                done.append(i)
            else:
                demand = demand - allocation[i] + tempalloc
                allocation[i] = tempalloc
            if not forced:
                needed_hours = np.sum(np.maximum(availabilities[0]-demand,0))
                print "NEEDED HOURS: " + str(needed_hours)
                worker_hours = sum([capacities[j] for j in a[i:]])
                if needed_hours >= worker_hours:
                    forced = True
        for i in done:
            a.remove(i)
        a.reverse()
    return allocation

if __name__ == "__main__":
    input_dict = gen_test.gen_input()
    print snake(input_dict["workers"], input_dict["shifts"], input_dict["availabilities"], input_dict["worker_values"], input_dict["worker_complements"], input_dict["worker_capacities"])