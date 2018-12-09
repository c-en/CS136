import marketLinear
import random
import itertools
import numpy as np
import test

def rsd(agents, objects, availabilities, values, complements, capacities):
    # randomly order agents to select their bundles
    a = range(len(agents))
    random.shuffle(a)
    allocation = [[] for _ in agents]
    demand = np.zeros(len(objects))
    forced = False
    for i in a:
        if not forced:
            p = np.zeros(len(objects))
            for j, d in enumerate(demand):
                if d >= availabilities[1][j]:
                    p[j] = 101
                else:
                    p[j] = 0
        else:
            p = np.zeros(len(objects))
            for j, d in enumerate(demand):
                if np.maximum(availabilities[0]-demand,0)[j] > 0:
                    p[j] = 0
                else:
                    p[j] = 101
        agent = marketLinear.AgentLinear(objects, values[i], complements[i], capacities[i], 100)
        allocation[i] = agent.demand(p)
        demand += allocation[i]
        if not forced:
            needed_hours = np.sum(np.maximum(availabilities[0]-demand,0))
            worker_hours = sum([capacities[j] for j in a[i:]])
            if needed_hours >= worker_hours:
                forced = True
    return np.array(allocation)

if __name__ == "__main__":
    input_dict = test.gen_input()
    print rsd(input_dict["workers"], input_dict["shifts"], input_dict["availabilities"], input_dict["worker_values"], input_dict["worker_complements"], input_dict["worker_capacities"])
