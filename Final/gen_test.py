import itertools
import numpy as np

# helper function to randomly generate input
def gen_input():
	# randomly generates:
	#   - agents: 40
	#       - agent-object values: 0-10
	#       - agent-object-object complement values (i <= j, adjacent shifts): same value as object value
	#       - agent capacities: [12, 30, 40] or adjusted proportionally
	#   - availabiliites of objects (lower and upper bound)
	#       - 15-22 workers per shift

	num_workers = 40
	min_workers_shift = 15
	max_workers_shift = 22
	worker_max_value = 10

	# worker capacity possibilities
	worker_caps = [4, 10, 13]

	# probability distribution of hours
	# 0.5 (full day), 0.2 (beginning of day), 0.2 (end of day), 0.1 (nothing)
	hour_distribution = [0.5, 0.2, 0.2, 0.1]

	# shifts
	days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
	hours = range(0, 3)
	shifts = list(itertools.product(days,hours))
	num_shifts = len(shifts)

	# randomly generate range of availabilities for each shift
	availabilities_max = np.random.randint(min_workers_shift, max_workers_shift+1, size=num_shifts)
	availabilities_min = availabilities_max-4
	availabilities_max = availabilities_max+4
	availabilities = [availabilities_min, availabilities_max]

	# initialize agents
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

	worker_values = np.array(worker_values)

	# initialize agent capacities
	worker_capacities = np.random.choice(worker_caps, size=num_workers)

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