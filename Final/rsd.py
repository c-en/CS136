import market_linear
import random
import numpy as np
import gen_test

# performs a random serial dictatorship for the given market
# agents: list of agents
# objects: list of objects
# availabilities: availability of each object (standard) - format [[array of lower bound],[array of upper bound]]
# values: linear values of objects for each agent (|agent| by |object| array)
# complements: matrix of values for each agent for having 2 objects simultaneously (|agent| by |object| by |object|)
# capacities: allocation capacity of each agent (|agent| length array)
# returns allocation
def rsd(agents, objects, availabilities, values, complements, capacities):
    # randomly order agents to select their bundles
    a = range(len(agents))
    random.shuffle(a)
    allocation = [[] for _ in agents]
    demand = np.zeros(len(objects))
    forced = False
    # agents take turns selecting their schedules
    for i in a:
        # if surplus of worker-hours, workers can select any shift not at capacity
        if not forced:
            p = np.zeros(len(objects))
            for j, d in enumerate(demand):
                if d >= availabilities[1][j]:
                    p[j] = 101
                else:
                    p[j] = 0
        # if shortage of worker-hours, workers must select from understaffed shifts
        else:
            p = np.zeros(len(objects))
            for j, d in enumerate(demand):
                if np.maximum(availabilities[0]-demand,0)[j] > 0:
                    p[j] = 0
                else:
                    p[j] = 101
        # solve for agent's demand given available shifts
        agent = market_linear.AgentLinear(objects, values[i], complements[i], capacities[i], 100)
        allocation[i] = agent.demand(p)
        demand += allocation[i]
        # check for surplus or shortage of worker-shifts
        if not forced:
            needed_hours = np.sum(np.maximum(availabilities[0]-demand,0))
            worker_hours = sum([capacities[j] for j in a[i:]])
            if needed_hours >= worker_hours:
                forced = True
    return np.array(allocation)

if __name__ == "__main__":
    input_dict = gen_test.gen_input()
    print rsd(input_dict["workers"], input_dict["shifts"], input_dict["availabilities"], input_dict["worker_values"], input_dict["worker_complements"], input_dict["worker_capacities"])
