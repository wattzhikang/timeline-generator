import argparse
import matplotlib.pyplot as plt
import numpy

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
eventDatabase = EventDatabase()

if bioFiles != None:
    for filename in bioFiles:
        bioDatabase.addData(filename)

if numFiles != None:
    for filename in numFiles:
        numDatabases.append(NumericalData(filename))

if eventFiles != None:
    for filename in eventFiles:
        eventDatabase.addData(filename)

### Get applicable subplots

import matplotlib.pyplot as plt

fig, (eventChart, bioChart, *numCharts) = plt.subplots(nrows=2+len(numDatabases), sharex="all")

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

### Event Data

levels = numpy.tile([3, 2, 1], int(numpy.ceil(eventDatabase.numItems()/3)))[:eventDatabase.numItems()]

markerline, stemline, baseline = eventChart.stem(eventDatabase.dateSeries(), levels, use_line_collection=True)

for event, level in zip(eventDatabase.events(), levels):
    eventChart.annotate(event.brief, xy=(event.date, level), xytext=(0,0), textcoords="offset points", va="top", ha="left")

markerline.set_ydata(numpy.zeros(eventDatabase.numItems()))

plt.setp(baseline, visible=False)

eventChart.get_yaxis().set_visible(False)

### Plot the chart

minDate, maxDate = None, None

if bioDatabase.numItems() > 0:
    minDate = bioDatabase.minBirthDate()
    maxDate = bioDatabase.maxDeathDate()

if eventDatabase.numItems() > 0:
    if eventDatabase.minEventDate() < minDate or minDate == None:
        minDate = eventDatabase.minEventDate()
    if eventDatabase.maxEventDate() > maxDate or maxDate == None:
        maxDate = eventDatabase.maxEventDate()

for numDatabase in numDatabases:
    if numDatabase.minDate() < minDate or minDate == None:
        minDate = numDatabase.minDate()
    if numDatabase.maxDate() > maxDate or maxDate == None:
        maxDate = numDatabase.maxDate()

plt.xlim(minDate, maxDate)

plt.show()