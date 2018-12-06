import marketLinear

def snake(agents, objects, availabilities, values, complements, capacities):
    # randomly order agents
    a = random.shuffle(range(len(agents)))
    allocation = [[] for _ in agents]
    demand = np.zeros(objects)
    complete = [False] * len(agents)
    allocation = [np.zeros(objects) for _ in agents]
    while False in complete:
        for i in a:
            p = np.zeros(objects)
            for i, d in enumerate(demand):
                if d >= availabilities[1][i]:
                    p[i] = 100
                else:
                    p[i] = 0
            value = values[i]
            for j, d in enumerate(allocation[i]):
                s = sum(values[i]) + sum(complements[i])
                if d == 1:
                    value[d] = s
            agent = marketLinear.AgentLinear(objects, value, complements[i], capacities[i], 100)
            tempalloc = agent.demand()
            if tempalloc == agent.demand():
                complete[i] = True
                a.remove(i)
            else:
                demand = demand - allocation[i] + tempalloc
                allocation[i] = tempalloc
    return allocation
