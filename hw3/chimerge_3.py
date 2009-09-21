#! /usr/bin/env python

import string

"""
	constants/global variables
"""

data_file = "./bezdekIris.data"
attributes = {"Sepal Length":0, "Sepal Width": 1, "Petal Length": 2, "Petal Width": 3, "Class": 4}
num_intervals = 6

# calcs is used to collect the metric of how many times the chi^2 algorithm is run for each run
calcs = 0

"""
	utility functions
"""

# collect_classes returns a list containing exactly one representation
# of each class found in the submitted intervals
def collect_classes(a, b):
	global attributes
	class_index = attributes["Class"]
	classes = []
	for x in a:
		if classes.count(x[class_index]) == 0:
			classes.append(x[class_index])
	for x in b:
		if classes.count(x[class_index]) == 0:
			classes.append(x[class_index])
	return classes

# class_count counts the number of times the class appears in the submitted interval
def class_count(cls, list):
	count = 0
	for x in list:
		if type(x).__name__ == 'list':
			count += class_count(cls, x)
		elif x == cls:
			count += 1
	return count

# calc_chi calculates the chi^2 value between (two) intervals
def calc_chi(intervals):
	global calcs
	calcs += 1
	interval_classes = collect_classes(intervals[0], intervals[1])
	k = len(interval_classes)
	chi = 0.0
	for i in range(0, len(intervals)):
		inner_sum = 0.0
		for j in range(0, k):
			jth_class = interval_classes[j]
			A = class_count(jth_class, intervals[i])
			R = len(intervals[i])
			C = class_count(jth_class, intervals)
			N = len(intervals[0]) + len(intervals[1])
			E = R * C / N
			inner_sum += ((A - E) * (A - E))/E
		chi += inner_sum
	return chi

# calculates chi^2 values and merges intervals until there are "number" intervals left.
# takes advantage of python's use of reference data types: the parameters passed to this function
# are changed in place, so it doesn't have to return anything.
def calc_intervals(number, intervals, chis, data):
	while len(chis) >= number:
		# find the first smallest chi^2 value.  The intervals bracketing this value will be merged.
		y = chis.index(min(chis))
		# merge the adjoining intervals together so that the interval encompasses from
		# the first line of the first interval to the last line of the second interval
		intervals[y] = (intervals[y][0], intervals[y+1][1])
		# clean up the old interval and chi^2 value
		del intervals[y+1]
		del chis[y]
		# recalculate the neighboring chi^2 values
		# the conditional statements avoid index errors for
		# the edge cases of the first and last intervals in the list
		ci = intervals[y]
		if y > 0:
			oi = intervals[y-1]
			chis[y-1] = calc_chi([data[oi[0]:oi[1]], data[ci[0]:ci[1]]])
		if y < len(chis):
			oi = intervals[y+1]
			chis[y] = calc_chi([data[ci[0]:ci[1]], data[oi[0]:oi[1]]])

"""
	main program
"""

# read all of the data from the data file into a list
# store each line as a list so that index semantics can be used to reference each attribute
data = []
f = open(data_file)
for entry in f:
	entry = entry.strip()
	if entry != '':
		data.append(entry.split(','))
l = len(data)

# calculate ChiMerge for each attribute
for a in ("Sepal Length", "Sepal Width", "Petal Length", "Petal Width"):
	# for each attribute, sort the data using that attribute as the sort key
	data.sort(key = lambda x: x[attributes[a]])
	# initialize the list of interval boundaries so that each entry starts out as its own interval
	intervals = [(x, x + 1) for x in range(0, l)]
	
	# set up the list of chi^2 values
	chis = [0 for x in range(0, l - 1)]
	# reset the chi^2 calculation tracking variable
	calcs = 0
	# do the initial chi^2 calculations
	for x in range(0, len(chis)):
		ci = intervals[x]
		oi = intervals[x+1]
		chis[x] = calc_chi([data[ci[0]:ci[1]], data[oi[0]:oi[1]]])
	# once the chi^2 values between each entry are calculated,
	# merge and recalculate until there are only the specified number of intervals left
	calc_intervals(num_intervals, intervals, chis, data)
	# display the results
	print("")
	print(a)
	print(" ", calcs, "chi^2 calculations")
	print("  intervals and chi^2 separation values:")
	for x in range(0, len(intervals)):
		print(" ", intervals[x])
		if x < len(chis):
			print("   ", chis[x])
