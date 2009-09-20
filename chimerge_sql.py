#! /usr/bin/python

import string
from pysqlite2 import dbapi2 as sqlite

connection = sqlite.connect(':memory:')
cursor = connection.cursor()
cursor.execute("CREATE TABLE irises (septal_length FLOAT, septal_width FLOAT, petal_length FLOAT, petal_width FLOAT, class VARCHAR(50))")

f = open("./bezdekIris.data")
for tuple in f:
	tuple = tuple.strip()
	if tuple != '':
		values = tuple.split(',')
		cursor.execute("INSERT INTO irises VALUES ("+values[0]+", "+values[1]+", "+values[2]+", "+values[3]+", \""+values[4]+"\")")
		connection.commit()

def fetchData(column, cursor):
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



data = fetchData('septal_length', cursor)
index = getIndex(data)
print index


