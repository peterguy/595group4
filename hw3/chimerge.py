#!/Library/Frameworks/Python.framework/Versions/3.1/bin/python3

import string
from pysqlite2 import dbapi2 as sqlite

connection = sqlite.connect(':memory:')
cursor = connection.cursor()
cursor.execute('CREATE TABLE irises (septal_length FLOAT, septal_width FLOAT, petal_length FLOAT, petal_width FLOAT, class VARCHAR(50))')

calcs = 0

def collect_classes(a, b):
	classes = []
	for x in a:
		if classes.count(x[4]) == 0:
			classes.append(x[4])
	for x in b:
		if classes.count(x[4]) == 0:
			classes.append(x[4])
	return classes

def class_count(cls, list):
	count = 0
	for x in list:
		if type(x).__name__ == 'list':
			count += class_count(cls, x)
		elif x == cls:
			count += 1
	return count

def calc_chi(intervals):
	global calcs
	calcs += 1
	interval_classes = collect_classes(intervals[0], intervals[1])
	k = len(interval_classes)
	chi = 0.0
	for i in (0, 1):
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

def extract_range(data, range):
	if range[0] == range[1]:
		return [data[range[0]]]
	else:
		return data[range[0]:range[1]]

data = []

f = open("./bezdekIris.data")
for tuple in f:
	tuple = tuple.strip()
	if tuple != '':
		#data.append(tuple.split(','))
		values = tuple.split(',')
		cursor.execute("INSERT INTO irises VALUES (${values[0]}, ${values[1]}, ${values[2]}, ${values[3]}, ${values[4]})")
		connection.commit()
#data.sort(key = lambda x: x[0])
#l = len(data)

intervals = [(x, x) for x in range(0, l)]
chis = [0 for x in range(0, l -1)]

#[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), ...]
#[       0,      0,      2,      0,      3,    ...]
#[(1, 2), (3, 3), (4, 4), (5, 5), (6, 6), ...]
#[       1,      2,      0,      3,    ...]
#[(1, 2), (3, 3), (4, 5), (6, 6), ...]
#[       1,      2,      0,    ...]
#[(1, 2), (3, 3), (4, 6), ...]
#[       1,      4, ...]

for x in range(0, len(chis)):
	chis[x] = calc_chi([extract_range(data, intervals[x]), extract_range(data, intervals[x+1])])

while len(chis) > 5:
	y = chis.index(min(chis))
	intervals[y] = (intervals[y][0], intervals[y+1][1])
	del intervals[y+1]
	del chis[y]
	if y > 0:
		chis[y-1] = calc_chi([extract_range(data, intervals[y-1]), extract_range(data, intervals[y])])
	if y < len(chis):
		chis[y] = calc_chi([extract_range(data, intervals[y]), extract_range(data, intervals[y+1])])
	
print("")
print(calcs, "chi^2 calculations")
print("")
print("intervals and chi^2 separation values:")
for x in range(0, len(intervals)):
	print(intervals[x])
	if x < len(chis):
		print(chis[x])
	