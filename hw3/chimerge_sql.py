#! /usr/bin/python

import string
from pysqlite2 import dbapi2 as sqlite

connection = sqlite.connect(':memory:')
cursor = connection.cursor()
cursor.execute("CREATE TABLE irises (septal_length FLOAT, septal_width FLOAT, petal_length FLOAT, petal_width FLOAT, class VARCHAR(50))")

intervals = {}
interval_indexes = []
chi2Values = []

# Build sqlite table
f = open("./bezdekIris.data")
for tuple in f:
	tuple = tuple.strip()
	if tuple != '':
		values = tuple.split(',')
		cursor.execute("INSERT INTO irises VALUES ("+values[0]+", "+values[1]+", "+values[2]+", "+values[3]+", \""+values[4]+"\")")
		connection.commit()

# Builds intervals from a colum in the sqlite database
def buildIntervals(column):
  global cursor
  data = {}
  cursor.execute('SELECT class, '+column+', COUNT('+column+') FROM irises GROUP BY class, '+column+' ORDER BY '+column+' DESC')
  for row in cursor:
    try:
      label = "%.2f" % row[1]
      data[label][row[0]] = row[2]
    except KeyError:
      data[label] = {'Iris-setosa':0, 'Iris-versicolor':0, 'Iris-virginica':0}
      data[label][row[0]] = row[2]
  return data

# Generates a sortable list of indexes into the interval dictionary
def createIndex(data):
    keys = data.keys()
    keys.sort(reverse=True)
    return keys

# Provides a quick sum of classes in an interval
def intervalSum(i):
  global intervals
  return intervals[i]['Iris-setosa'] + intervals[i]['Iris-versicolor'] + intervals[i]['Iris-virginica']

# Calulates the chi2 value for two indexes
def calcChi2(index1, index2):
  global interval_indexes
  global intervals
  E1 = (intervalSum(index1) + 50)/150.0
  E2 = (intervalSum(index2) + 50)/150.0
  return (intervals[index1]['Iris-setosa'] - E1)/E1 + (intervals[index1]['Iris-versicolor'] - E1)/E1 + (intervals[index1]['Iris-virginica'] - E1)/E1 + (intervals[index2]['Iris-setosa'] - E2)/E2 + (intervals[index2]['Iris-versicolor'] - E2)/E2 + (intervals[index2]['Iris-virginica'] - E2)/E2  

# The comparision function used when sorting the chi2 list
def chi2Compare(x,y):
  if x['value']>y['value']:
    return 1
  elif x['value']==y['value']:
    return 0
  else: # x<y
    return -1

# Function to merge two indexes into one composite index and recalculate chi2 values for neighbors
def merge(index1, index2):
  global interval_indexes
  global intervals
  global chi2Values
  new_key = index1+","+index2
  intervals[new_key] = {}
  intervals[new_key]['Iris-setosa'] = intervals[index1]['Iris-setosa'] + intervals[index2]['Iris-setosa']
  intervals[new_key]['Iris-versicolor'] = intervals[index1]['Iris-versicolor'] + intervals[index2]['Iris-versicolor']
  intervals[new_key]['Iris-virginica'] = intervals[index1]['Iris-virginica'] + intervals[index2]['Iris-virginica']
  del(intervals[index2])
  del(intervals[index1])
  interval_indexes[interval_indexes.index(index1)] = new_key
  interval_indexes.remove(index2)
  for c in chi2Values:
    if (c['index1'] == index1 or c['index1'] == index2):
      c['value'] = calcChi2(new_key, c['index2'])
      c['index1'] = new_key
    elif (c['index2'] == index1 or c['index2'] == index2):
      c['value'] = calcChi2(c['index1'], new_key)
      c['index2'] = new_key
  chi2Values.sort(chi2Compare)

# Driver function to start chiMerge for a specific column, will execute until 6 intervals are found
def doChiMerge(column):
  global interval_indexes
  global intervals
  global chi2Values
  intervals = {}
  interval_indexes = []
  chi2Values = []
  intervals = buildIntervals(column)
  interval_indexes = createIndex(intervals)
  for index in range(len(interval_indexes)-1):
    chi2Values.append({'value':calcChi2(interval_indexes[index], interval_indexes[index+1]), 'index1':interval_indexes[index], 'index2':interval_indexes[index+1]})
  chi2Values.sort(chi2Compare)
  while len(interval_indexes) > 5:
    chival = chi2Values.pop(0)
    merge(chival['index1'], chival['index2'])
  print column+":",interval_indexes

doChiMerge('septal_length')
doChiMerge('septal_width')
doChiMerge('petal_length')
doChiMerge('petal_width')
