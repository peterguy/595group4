#! /usr/bin/python

import string
from pysqlite2 import dbapi2 as sqlite

connection = sqlite.connect(':memory:')
cursor = connection.cursor()
cursor.execute("CREATE TABLE irises (sepal_length FLOAT, sepal_width FLOAT, petal_length FLOAT, petal_width FLOAT, class VARCHAR(50))")

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
      data[label] = {'Iris-setosa':0, 'Iris-versicolor':0, 'Iris-virginica':0, 'boundry':label}
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

def classSum(index1, index2):
  global intervals
  #return {'Iris-setosa':intervals[index1]['Iris-setosa'] + intervals[index2]['Iris-setosa'], 'Iris-versicolor':intervals[index1]['Iris-versicolor'] + intervals[index2]['Iris-versicolor'], 'Iris-virginica':intervals[index1]['Iris-virginica'] + intervals[index2]['Iris-virginica']}
  return {'Iris-setosa':50, 'Iris-versicolor':50, 'Iris-virginica':50}
  
# Calulates the chi2 value for two indexes
# This is horrible I know....
def calcChi2(index1, index2):
  global interval_indexes
  global intervals
  classSums = classSum(index1, index2)
  intervalSum1 = intervalSum(index1)
  intervalSum2 = intervalSum(index2)
  #N = float(intervalSum1 + intervalSum2 + classSums['Iris-setosa'] + classSums['Iris-versicolor'] + classSums['Iris-virginica'])
  N = 150.0
  E11 = (intervalSum1 + classSums['Iris-setosa'])/N
  E12 = (intervalSum1 + classSums['Iris-versicolor'])/N
  E13 = (intervalSum1 + classSums['Iris-virginica'])/N
  E21 = (intervalSum2 + classSums['Iris-setosa'])/N
  E22 = (intervalSum2 + classSums['Iris-versicolor'])/N
  E23 = (intervalSum2 + classSums['Iris-virginica'])/N
  if E11 < 0.5:
    A11 = pow(intervals[index1]['Iris-setosa'] - E11, 2)/0.5
  else:
    A11 = pow(intervals[index1]['Iris-setosa'] - E11, 2)/E11
  if E12 < 0.5:
    A12 = pow(intervals[index1]['Iris-versicolor'] - E12, 2)/0.5
  else:
    A12 = pow(intervals[index1]['Iris-versicolor'] - E12, 2)/E12
  if E13 < 0.5:
    A13 = pow(intervals[index1]['Iris-virginica'] - E13, 2)/0.5
  else:
    A13 = pow(intervals[index1]['Iris-virginica'] - E13, 2)/E13
  if E21 < 0.5:
    A21 = pow(intervals[index2]['Iris-setosa'] - E21, 2)/0.5
  else:
    A21 = pow(intervals[index2]['Iris-setosa'] - E21, 2)/E21
  if E22 < 0.5:
    A22 = pow(intervals[index2]['Iris-versicolor'] - E22, 2)/0.5
  else:
    A22 = pow(intervals[index2]['Iris-versicolor'] - E22, 2)/E22
  if E23 < 0.5:
    A23 = pow(intervals[index2]['Iris-virginica'] - E23, 2)/0.5
  else:
    A23 = pow(intervals[index2]['Iris-virginica'] - E23, 2)/E23 
  return A11 + A12 + A13 + A21 + A22 + A23 

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
  intervals[new_key]['boundry'] = min(intervals[index1]['boundry'], intervals[index2]['boundry'])
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
  while len(interval_indexes) > 6:
    chival = chi2Values.pop(0)
    merge(chival['index1'], chival['index2'])
  print column+":",intervals

doChiMerge('sepal_length')
doChiMerge('sepal_width')
doChiMerge('petal_length')
doChiMerge('petal_width')
