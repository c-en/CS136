import itertools
import numpy as np
import matplotlib.pyplot as plt

import snake
import rsd
import aceei
import marketLinear

def gen_input():
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
				worker_array.extend([work_val]*2 + [0.001])
			# end of day
			elif work_time == 2:
				worker_array.extend([0.001] + [work_val]*2)
			else:
				worker_array.extend([0.001]*3)

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
			if i%len(hours) != len(hours)-1 and worker_values[worker][i] >= 1 and worker_values[worker][i+1] >= 1:
					worker_complements[worker][i][i+1] = worker_values[worker][i]
	input_dict = {
		"workers": workers,
		"shifts": shifts,
		"availabilities": availabilities,
		"worker_values": worker_values,
		"worker_complements": worker_complements,
		"worker_capacities": worker_capacities
	}
	return input_dict

# calculate the total value for an agent given their allocation, value, and complementary values
def calc_value(allocation, value, complement_val):
	# print "Allocation: " + str(allocation)
	# print "Value: " + str(value)
	# print "Complements: " + str(complement_val)
	total_complement_val = 0
	for obj in range(len(allocation)-1):
		if allocation[obj] == 1 and allocation[obj+1] == 1:
			total_complement_val += complement_val[obj][obj+1]
	#print allocation * value
	return np.sum(allocation * value) + total_complement_val


def run_welfare_tests(num_tests):
	all_snake_vals = []
	all_rsd_vals = []
	all_aceei_vals = []
	for i in range(num_tests):
		print "################### TRIAL " + str(i) + " ########################"
		input_dict = gen_input()
		snake_alloc = snake.snake(input_dict['workers'], input_dict["shifts"], input_dict["availabilities"], input_dict["worker_values"], input_dict["worker_complements"], input_dict["worker_capacities"])
		# print "SNAKE ALLOC: " + str(snake_alloc)
		# print "*******************************"

		rsd_alloc = rsd.rsd(input_dict['workers'], input_dict["shifts"], input_dict["availabilities"], input_dict["worker_values"], input_dict["worker_complements"], input_dict["worker_capacities"])
		# print "RSD ALLOC: " + str(rsd_alloc)
		# print "*******************************"

		Market = marketLinear.MarketLinear(input_dict["shifts"], input_dict["workers"], input_dict["worker_values"], input_dict["worker_complements"], input_dict["worker_capacities"])
		# initialize tabu search, return allocation
		(aceei_alloc, _, _) =  aceei.tabu(input_dict["workers"], input_dict["shifts"], input_dict["availabilities"], Market)
		# print "ACEEI ALLOC: " + str(aceei_alloc)
		# print "*******************************"

		snake_vals = []
		rsd_vals = []
		aceei_vals = []
		for a in range(len(input_dict["workers"])):
			snake_vals.append(calc_value(snake_alloc[a], input_dict["worker_values"][a], input_dict["worker_complements"][a]))
			rsd_vals.append(calc_value(rsd_alloc[a], input_dict["worker_values"][a], input_dict["worker_complements"][a]))
			aceei_vals.append(calc_value(aceei_alloc[a], input_dict["worker_values"][a], input_dict["worker_complements"][a]))
		
		all_snake_vals.append(snake_vals)
		all_rsd_vals.append(rsd_vals)
		all_aceei_vals.append(aceei_vals)
	# print "&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&"
	# print all_snake_vals
	# print len(all_snake_vals)
	# print np.mean(all_snake_vals, axis=0)
	# print len(np.mean(all_snake_vals, axis=0))

	return np.mean(all_snake_vals, axis=0), np.mean(all_rsd_vals, axis=0), np.mean(all_aceei_vals, axis=0)

def viz_welfare_results(snake_vals, rsd_vals, aceei_vals):
	# snake_vals = [119.0, 61.0, 118.0, 99.0, 77.0, 32.0, 116.0, 30.0, 40.0, 27.0, 49.0, 122.0, 30.0, 50.0, 24.0, 30.0, 53.0, 39.0, 91.0, 25.0, 126.0, 30.0, 9.0, 30.0, 40.0, 70.0, 35.0, 89.0, 111.0, 50.0, 97.0, 76.0, 27.0, 63.0, 5.0, 78.0, 95.0, 35.0, 56.0, 83.0]
	# rsd_vals = [119.0, 71.0, 128.0, 78.0, 107.0, 60.0, 116.0, 45.0, 40.0, 45.0, 64.0, 122.0, 40.0, 0.0, 65.0, 45.0, 77.0, 69.0, 91.0, 39.0, 126.0, 30.0, 9.0, 51.0, 45.0, 75.0, 137.0, 15.0, 111.0, 12.0, 97.0, 76.0, 39.0, 84.0, 40.0, 78.0, 95.0, 35.0, 45.0, 92.0]
	# aceei_vals = [89.0, 61.0, 94.0, 45.0, 80.0, 60.0, 59.0, 45.0, 40.0, 45.0, 55.0, 72.0, 40.0, 60.0, 100.0, 45.0, 77.0, 69.0, 66.0, 39.0, 126.0, 45.0, 25.0, 57.0, 45.0, 75.0, 107.0, 92.0, 87.0, 57.0, 97.0, 76.0, 39.0, 81.0, 40.0, 78.0, 95.0, 35.0, 101.0, 72.0]
	print "Average Snake value: " + str(np.mean(snake_vals))
	print "Average RSD Value: " + str(np.mean(rsd_vals))
	print "Average ACEEI Value: " + str(np.mean(aceei_vals))

	plt.hist(snake_vals, alpha=0.4, bins=5, label="snake")
	plt.hist(rsd_vals, alpha=0.4, bins=5, label="rsd")
	plt.hist(aceei_vals, alpha=0.4, bins=5, label="aceei")
	plt.legend(loc="upper right")
	plt.suptitle("Distribution of Welfare")
	plt.show()

if __name__ == "__main__":
	#run_tests()
	snake_res, rsd_res, aceei_res = run_welfare_tests(2)
	viz_welfare_results(snake_res, rsd_res, aceei_res)
