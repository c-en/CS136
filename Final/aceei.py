import itertools
#import tabu_gen
import numpy as np

#def gen_data(min_workers_shift, )

def main():
    # randomly generate:
    #   - agents: 40
    #       - agent-object values: 0-10
    #       - agent-object-object complement values (i <= j): adjacent hours
    #       - agent capacities: 12, 30, 40 (distribute randomly)
    #   - availabiliites of objects (lower and upper bound)
    #       - 15-22 workers per shift
    # initialize shifts

    num_workers = 40
    min_workers_shift = 15
    max_workers_shift = 22
    worker_max_value = 10
    complement_val = 20
    # probability distribution of values
    worker_value_weights = [0.5]+[0.5/(worker_max_value) for i in range(worker_max_value)]
    worker_caps = [12, 30, 40]

    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    hours = range(9,17)
    shifts = list(itertools.product(days,hours))
    num_shifts = len(shifts)
    print("SHIFTS: ", shifts)

    # 1D array representing the number of workers per shift
    # day = days[int(index/7)], hour = index%7
    availabiliites = np.random.randint(min_workers_shift, max_workers_shift+1, size=num_shifts)
    print("availabiliites: ", availabiliites)

    # initialize agents, values
    workers = ['worker'+str(i) for i in range(num_workers)]
    # should there be any restrictions on values of shifts?
    worker_values = np.random.choice(worker_max_value+1, size=(num_workers, num_shifts), p=worker_value_weights)

    # initialize agent capacities
    worker_capacities = np.random.choice(worker_caps, size=num_workers)

    # initialize agent complement values
    worker_complements = np.zeros((num_workers, num_shifts, num_shifts))
    for worker in range(num_workers):
        for i in range(num_shifts):
            if worker_values[worker][i] > 0:
                worker_complements[worker][i][i] = worker_values[worker][i]
                if i < num_shifts-1 and worker_values[worker][i+1] > 0:
                    worker_complements[worker][i][i+1] = complement_val
    for i in range(len(worker_complements[0])):
        print(worker_complements[0][i])

main()