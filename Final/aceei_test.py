import itertools
import aceei
import numpy as np
import marketLinear
import csv
import matplotlib.pyplot as plt
import test

def run_aceei():
    input_dict = test.gen_input()
    #print(worker_complements[0])
    # with open("output/prefs.csv", 'w') as f:
    #     np.savetxt(f, worker_values, fmt='%i', delimiter=",")

    # initialize MarketLinear object
    print "MarketLinear init"
    Market = marketLinear.MarketLinear(input_dict["shifts"], input_dict["workers"], input_dict["worker_values"], input_dict["worker_complements"], input_dict["worker_capacities"])

    # initialize tabu search, return allocation
    print "tabu init"
    return aceei.tabu(workers, shifts, availabilities, Market)

if __name__ == "__main__":
    times_arr = []
    err_arr = []
    num_trials = 10
    for i in range(num_trials):
       allocation, times, besterrors = run_aceei()
       times_arr.append(np.array(times))
       err_arr.append(np.array(besterrors))

    with open("output/aceei_times.csv", mode='w') as f:
        writer = csv.writer(f, delimiter=",")
        for row in times_arr:
            writer.writerow(row)
    with open("output/aceei_errors.csv", mode='w') as f:
        writer = csv.writer(f, delimiter=",")
        for row in err_arr:
            writer.writerow(row)

    for i in range(num_trials):
        plt.step(times_arr[i], err_arr[i])

    plt.title("Error vs. Time")
    plt.show()




