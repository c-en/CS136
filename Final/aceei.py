import itertools
import tabu_gen

def main():
    # initialize shifts
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    hours = range(9,17)
    shifts = list(itertools.product(days,hours))
    # initialize agents, values
    workers = ['worker'+str(i) for i in range(10)]
