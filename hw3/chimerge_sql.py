#! /usr/bin/python

import string
from pysqlite2 import dbapi2 as sqlite

connection = sqlite.connect(':memory:')
cursor = connection.cursor()
cursor.execute("CREATE TABLE irises (septal_length FLOAT, septal_width FLOAT, petal_length FLOAT, petal_width FLOAT, class VARCHAR(50))")

intervals = {}
interval_indexes = []
chi2Values = []
cursor = None

f = open("./bezdekIris.data")
for tuple in f:
	tuple = tuple.strip()
	if tuple != '':
		values = tuple.split(',')
		cursor.execute("INSERT INTO irises VALUES ("+values[0]+", "+values[1]+", "+values[2]+", "+values[3]+", \""+values[4]+"\")")
		connection.commit()

def fetchIntervals(column):
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

def getIndex(data):
    keys = data.keys()
    keys.sort(reverse=True)
    return keys

def merge(index1, index2):
  global interval_indexes
  global intervals
  new_key = index1+","+index2
  intervals[new_key] = {}
  intervals[new_key]['Iris-setosa'] = intervals[index1]['Iris-setosa'] + intervals[index2]['Iris-setosa']
  intervals[new_key]['Iris-versicolor'] = intervals[index1]['Iris-versicolor'] + intervals[index2]['Iris-versicolor']
  intervals[new_key]['Iris-virginica'] = intervals[index1]['Iris-virginica'] + intervals[index2]['Iris-virginica']
  del(intervals[index2])
  del(intervals[index1])
  interval_indexes[interval_indexes.index(index1)] = new_key
  interval_indexes.remove(index2)
  
def calcChi2(index1, index2):
  global interval_indexes
  global intervals
  E = (intervals[index1]['Iris-setosa'] + )
  

def intervalSum(i):
  global intervals
  intervals[i]['Iris-setosa'] + intervals[i]['Iris-versicolor'] + intervals[i]['Iris-virginica']

intervals = fetchIntervals('septal_length')
interval_index = getIndex(intervals)
print interval_index
merge(interval_index[0], interval_index[1])
interval_index = getIndex(intervals)
print interval_index


