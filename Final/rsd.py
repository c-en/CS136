import marketLinear
import random
import itertools
import numpy as np

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

def main():
    # randomly generate:
    #   - agents: 40
    #       - agent-object values: 0-10
    #       - agent-object-object complement values (i <= j): adjacent hours
    #       - agent capacities: 12, 30, 40 (distribute randomly)
    #   - availabiliites of objects (lower and upper bound)
    #       - 15-22 workers per shift
    num_workers = 40
    min_workers_shift = 15
    max_workers_shift = 22
    worker_max_value = 10
    complement_val = 20
    # probability distribution of values
    # worker_value_weights = [0.5]+[0.5/(worker_max_value) for i in range(worker_max_value)]
    worker_caps = [4, 10, 13]

    # 0.5 full day, 0.4 (beg, end - 12-5), 0.1 nothing
    hour_distribution = [0.5, 0.2, 0.2, 0.1]

    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    hours = range(0, 3)
    shifts = list(itertools.product(days,hours))
    num_shifts = len(shifts)
    #print("SHIFTS: ", shifts)

    # 1D array representing the number of workers per shift
    # day = days[int(index/7)], hour = index%7
    availabilities_max = np.random.randint(min_workers_shift, max_workers_shift+1, size=num_shifts)
    availabilities_min = availabilities_max-4
    availabilities_max = availabilities_max+4
    availabilities = [availabilities_min, availabilities_max]
    # print "MAX HOURS NEEDED: " + str((availabilities_max))
    # print "MIN HOURS NEEDED: " + str((availabilities_min))

    # initialize agents, values
    workers = ['worker'+str(i) for i in range(num_workers)]

    # initialize shift values
    worker_values = []
    worker_total = np.zeros(len(shifts))
    for worker in range(num_workers):
        worker_array = []
        for day in range(len(days)):
            work_time = np.random.choice(len(hour_distribution), p=hour_distribution)
            work_val = np.random.choice(worker_max_value) + 1
            # full day
            if work_time == 0:
                worker_array.extend([work_val]*3)
            # beginning of day
            elif work_time == 1:
                worker_array.extend([work_val]*2 + [0])
            # end of day
            elif work_time == 2:
                worker_array.extend([0] + [work_val]*2)
            else:
                worker_array.extend([0]*3)

        worker_values.append(worker_array)
        #worker_total = worker_total + np.array(worker_array)/np.array(worker_array)
    #print "WORKER TOTAL: " + str(worker_total)
    worker_values = np.array(worker_values)

    # initialize agent capacities
    worker_capacities = np.random.choice(worker_caps, size=num_workers)
    #print 'WORKERS CAPS: ' + str(sum(worker_capacities))

    # initialize agent complement values
    worker_complements = np.zeros((num_workers, num_shifts, num_shifts))
    for worker in range(num_workers):
        for i in range(num_shifts):
            if i%len(hours) != len(hours)-1 and worker_values[worker][i] > 0 and worker_values[worker][i+1] > 0:
                    worker_complements[worker][i][i+1] = worker_values[worker][i]

    return rsd(workers, shifts, availabilities, worker_values, worker_complements, worker_capacities)

if __name__ == "__main__":
    print main()
