import itertools
import tabu_gen
import numpy as np
import marketLinear
#def gen_data(min_workers_shift, )

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
    print(worker_values)
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
    
    #print(worker_complements[0])
    # with open("output/prefs.csv", 'w') as f:
    #     np.savetxt(f, worker_values, fmt='%i', delimiter=",")

    # initialize MarketLinear object
    print "MarketLinear init"
    Market = marketLinear.MarketLinear(shifts, workers, worker_values, worker_complements, worker_capacities)

    # initialize tabu search, return allocation
    print "tabu init"
    allocation = tabu_gen.tabu(workers, shifts, availabilities, Market)
    return allocation

if __name__ == "__main__":
	main()