import argparse
import matplotlib.pyplot as plt

from timelineData import *

parser = argparse.ArgumentParser(
    description="A simple python tool for creating time-based charts based on multiple types of data"
)
parser.add_argument(
    "-b",
    "--biographical-data",
    nargs="+",
    help="One or more files containing biographical data",
    dest="bioFiles",
    metavar="filename.csv"
)
parser.add_argument(
    "-d",
    "--numerical-data",
    nargs="+",
    help="One or more files containing numerical data",
    dest="numFiles",
    metavar="filename.csv"
)
parser.add_argument(
    "-e",
    "--event-data",
    nargs="+",
    help="One or more files containing numerical data",
    dest="eventFiles",
    metavar="filename.csv"
)

bioFiles = parser.parse_args().bioFiles
numFiles = parser.parse_args().numFiles
eventFiles = parser.parse_args().eventFiles

if bioFiles == None and numFiles == None and eventFiles == None:
    print("You must specify at least one file")
    exit(0)

bioDatabase = PersonDatabase()
numDatabases = []

if bioFiles != None:
    for fileName in bioFiles:
        bioDatabase.addData(fileName)

if numFiles != None:
    for filename in numFiles:
        numDatabases.append(NumericalData(filename))

print(bioDatabase)
for database in numDatabases:
    print(database)

### Get applicable subplots

import matplotlib.pyplot as plt

fig, (bioChart, *numCharts) = plt.subplots(nrows=1+len(numDatabases))


### Biographical information
## Organize and sort biographical information

bioDatabase.sortByBirthDate()

bioStacks = [ ]

for person in bioDatabase.people():
    placed = False
    for stack in bioStacks:
        if len(stack) < 1 or stack[len(stack) - 1].death < person.birth:
            stack.append(person)
            placed = True
            break
    bioStacks.append([person])

bioStacks.reverse()

## Plot biographical information

bioChart.set_xlim(bioDatabase.minBirthDate(), bioDatabase.maxDeathDate())
bioChart.set_xlabel("Year")
bioChart.set_yticks([])
bioChart.grid(axis="x")

for stack, level in zip(bioStacks, range(len(bioStacks))): # zip this with a random color object, don't worry, zip only uses shortest
    for person in stack:
        bioChart.broken_barh([(person.birth, person.lifespan())], (10 * level, 9))
        bioChart.text(person.birth + (person.lifespan() / 2), 10 * level + 3, person.name)

### Numerical Data

for axis, database in zip(numCharts, numDatabases):
    if database.numColumns() > 1:
        axis.stackplot(database.getTimeIndex(), database.allColumns(), labels=database.allColumnLabels())
    else:
        axis.plot(database.getTimeIndex(), database.getColumn(), label=database.firstColumnLabel())
    axis.legend()

### Plot the chart

plt.show()