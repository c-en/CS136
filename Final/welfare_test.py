import numpy as np
import matplotlib.pyplot as plt

import gen_test
import snake
import rsd
import aceei
import market_linear

# calculates the total value for an agent given their allocation, value, and complementary values
# allocation: 1D array of an agent's allocation
# value: 1D array of agent's value for each shift
# complement_val: 2D array of complement values for an agent
def calc_value(allocation, value, complement_val):
	# first calculate the value from complements, add to total if the complement is satisfied
	total_complement_val = 0
	for obj in range(len(allocation)-1):
		if allocation[obj] == 1 and allocation[obj+1] == 1:
			total_complement_val += complement_val[obj][obj+1]

	# then add total value from individual allocations
	return np.sum(allocation * value) + total_complement_val

# runs the tests comparing the individual welfares of each agent for all three mechanisms
# num_tests: number of tests to run
def run_welfare_tests(num_tests):
	snake_vals = []
	rsd_vals = []
	aceei_vals = []
	for i in range(num_tests):
		print "################### TRIAL " + str(i) + " ########################"
		# generate random input
		input_dict = gen_test.gen_input()

		# find allocation from snake mechanism
		snake_alloc = snake.snake(input_dict['workers'], input_dict["shifts"], input_dict["availabilities"], input_dict["worker_values"], input_dict["worker_complements"], input_dict["worker_capacities"])
		
		# find allocation from RSD mechanism
		rsd_alloc = rsd.rsd(input_dict['workers'], input_dict["shifts"], input_dict["availabilities"], input_dict["worker_values"], input_dict["worker_complements"], input_dict["worker_capacities"])

		# find allocation from A-CEEI mechanism
		Market = market_linear.MarketLinear(input_dict["shifts"], input_dict["workers"], input_dict["worker_values"], input_dict["worker_complements"], input_dict["worker_capacities"])
		# initialize tabu search, return allocation
		(aceei_alloc, _, _) =  aceei.tabu(input_dict["workers"], input_dict["shifts"], input_dict["availabilities"], Market)
		
		# calculate each agent's utility for the allocation
		for a in range(len(input_dict["workers"])):
			snake_vals.append(calc_value(snake_alloc[a], input_dict["worker_values"][a], input_dict["worker_complements"][a]))
			rsd_vals.append(calc_value(rsd_alloc[a], input_dict["worker_values"][a], input_dict["worker_complements"][a]))
			aceei_vals.append(calc_value(aceei_alloc[a], input_dict["worker_values"][a], input_dict["worker_complements"][a]))

	return snake_vals, rsd_vals, aceei_vals

# collects results and visualizes them
# snake_vals: array of values for all agents in snake draft
# rsd_vals: array of values for all agents in RSD 
# aceei_vals: array of values for all agents in A-CEEI
# num_tests: number of tests to run
def viz_welfare_results(snake_vals, rsd_vals, aceei_vals, num_tests):
	print "Average Snake value: " + str(np.mean(snake_vals))
	print "Average RSD Value: " + str(np.mean(rsd_vals))
	print "Average ACEEI Value: " + str(np.mean(aceei_vals))
	
	# save output to a CSV file
	with open("output/values.csv", 'w') as f:
		np.savetxt(f, np.c_[snake_vals, rsd_vals, aceei_vals], fmt='%i', delimiter=",")

	# plot side-by-side histogram
	plt.hist([snake_vals, rsd_vals, aceei_vals], alpha=0.4, bins=30, label=["Snake", "RSD", "A-CEEI"])
	plt.legend(loc="upper right")
	plt.suptitle("Distribution of Welfare")
	plt.xlabel("Individual Welfare")
	plt.ylabel("Number of Workers")
	plt.show()

if __name__ == "__main__":
	# number of trials 
	num_tests = 1
	snake_res, rsd_res, aceei_res = run_welfare_tests(num_tests)
	viz_welfare_results(snake_res, rsd_res, aceei_res, num_tests)