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
    for i in a:
        p = np.zeros(len(objects))
        for j, d in enumerate(demand):
            if d >= availabilities[1][j]:
                p[j] = 101
            else:
                p[j] = 0
        agent = marketLinear.AgentLinear(objects, values[i], complements[i], capacities[i], 100)
        allocation[i] = agent.demand(p)
        demand += allocation[i]
    return np.array(allocation)

if __name__ == "__main__":
    input_dict = test.gen_input()
    print rsd(input_dict["workers"], input_dict["shifts"], input_dict["availabilities"], input_dict["worker_values"], input_dict["worker_complements"], input_dict["worker_capacities"])
