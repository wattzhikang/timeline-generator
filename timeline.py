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
    dest="bioFile",
    metavar="filename.csv"
)
parser.add_argument(
    "-d",
    "--numerical-data",
    nargs="+",
    help="One or more files containing numerical data",
    dest="numFile",
    metavar="filename.csv"
)
parser.add_argument(
    "-e",
    "--event-data",
    nargs="+",
    help="One or more files containing numerical data",
    dest="eventFile",
    metavar="filename.csv"
)

bioFile = parser.parse_args().bioFile[0]
numFile = parser.parse_args().numFile[0]
eventFile = parser.parse_args().eventFile[0]

if bioFile == None and numFile == None and eventFile == None:
    print("You must specify at least one file")
    exit(0)

ganttData = None
if bioFile != None:
    ganttData = GanttDatabase(bioFile)

numData = None
if numFile != None:
    numData = Database(numFile)

eventData = None
if eventFile != None:
    eventData = EventDatabase(eventFile)

### Get applicable subplots

import matplotlib.pyplot as plt

chartsToGenerate = 0
chartIndicies = [0, 0, 0]

for i, base in zip(range(3), [ganttData, numData, eventData]):
    if base != None:
        chartIndicies[i] = chartsToGenerate
        chartsToGenerate += 1

fig, *charts = plt.subplots(nrows=chartsToGenerate, sharex="all")

ganttChart = None
if ganttData != None:
    ganttChart = charts[0][chartIndicies[0]]

numChart = None
if numData != None:
    numChart = charts[0][chartIndicies[1]]

eventChart = None
if eventData != None:
    eventChart = charts[0][chartIndicies[2]]

### Biographical information
## Organize and sort biographical information

if ganttData != None:

    dashStacks = [ ]

    for dash in ganttData.dashes():
        placed = False
        for stack in dashStacks:
            if len(stack) < 1 or stack[len(stack) - 1].end < dash.start:
                stack.append(dash)
                placed = True
                break
        if not placed:
            dashStacks.append([dash])
    
    dashStacks.reverse()

    ## Plot biographical information

    ganttChart.set_xlabel("Year")
    ganttChart.set_yticks([])
    ganttChart.grid(axis="x")

    for stack, level in zip(dashStacks, range(len(dashStacks))): # zip this with a random color object, don't worry, zip only uses shortest
        for dash in stack:
            ganttChart.broken_barh([(dash.start, dash.duration())], (10 * level, 9))
            ganttChart.text(dash.start + (dash.duration() / 2), 10 * level + 3, dash.name)

### Numerical Data

if numData != None:
    numChart.stackplot(numData.allDates(), numData.allSerieses(), labels=numData.getColumnLabels())
    numChart.legend()

### Event Data

if eventData != None:
    levels = numpy.tile([3, 2, 1], int(numpy.ceil(eventData.numItems()/3)))[:eventData.numItems()]

    markerline, stemline, baseline = eventChart.stem(eventData.allDates(), levels, use_line_collection=True)

    for event, level in zip(eventData.events(), levels):
        eventChart.annotate(event.brief, xy=(event.date, level), xytext=(0,0), textcoords="offset points", va="top", ha="left")

    markerline.set_ydata(numpy.zeros(eventData.numItems()))

    plt.setp(baseline, visible=False)

    eventChart.get_yaxis().set_visible(False)

### Plot the chart

minDate, maxDate = None, None

for base in [ganttData, numData, eventData]:
    if minDate == None or base.minDate() < minDate:
        minDate = base.minDate()
    if maxDate == None or base.maxDate() > maxDate:
        maxDate = base.maxDate()

plt.xlim(minDate, maxDate)

plt.show()