import marketLinear
import random

def rsd(agents, objects, availabilities, values, complements, capacities):
    # randomly order agents to select their bundles
    a = random.shuffle(range(len(agents)))
    allocation = [[] for _ in agents]
    demand = np.zeros(objects)
    for i in a:
        p = np.zeros(objects)
        for i, d in enumerate(demand):
            if d >= availabilities[1][i]:
                p[i] = 100
            else:
                p[i] = 0
        agent = marketLinear.AgentLinear(objects, values[i], complements[i], capacities[i])
        allocation[i] = agent.demand()
        demand += allocation[i]
    return np.array(allocation)




