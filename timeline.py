import argparse
import matplotlib.pyplot as plt
import numpy

from timelineData import *

### Set up the Argument Parser to retrieve arguments from the user

parser = argparse.ArgumentParser(
    description="A simple python tool for creating time-based charts based on multiple types of data"
)
parser.add_argument(
    "-g",
    "--gantt-data",
    nargs="+",
    help="One or more files containing event duration data",
    dest="dashFiles",
    metavar="filename.csv"
)
parser.add_argument(
    "-l",
    "--line-data",
    nargs="+",
    help="One or more files containing numerical data for a line chart",
    dest="numFiles",
    metavar="filename.csv"
)
parser.add_argument(
    "-a",
    "--stacked-area-data",
    nargs="+",
    help="One or more files containing numerical data for a stacked area chart",
    dest="areaFiles",
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

dashFiles = parser.parse_args().dashFiles
linearFiles = parser.parse_args().numFiles
areaFiles = parser.parse_args().areaFiles
labelFiles = parser.parse_args().eventFiles

### Construct database objects

if dashFiles == None and linearFiles == None and labelFiles == None:
    print("You must specify at least one file")
    exit(0)

ganttData = [ ]
if dashFiles != None:
    for file in dashFiles:
        ganttData.append(GanttDatabase(file))

linearData = [ ]
if linearFiles != None:
    for file in linearFiles:
        linearData.append(Database(file))

areaData = [ ]
if areaFiles != None:
    for file in areaFiles:
        areaData.append(Database(file))

eventData = [ ]
if labelFiles != None:
    for file in labelFiles:
        eventData.append(EventDatabase(file))

### Get applicable subplots

import matplotlib.pyplot as plt

chartsToGenerate = 0
chartIndicies = [0, 0, 0, 0]

# End invariants:
#   chartsToGenerate has the number of charts to generate and the starting index
#       of the next chart to allocate
#   chartIndicies[i] holds the index of the charts allocated to i
for i, base in zip(range(4), [ganttData, linearData, areaData, eventData]):
    chartIndicies[i] = chartsToGenerate
    chartsToGenerate += len(base)

fig, *charts = plt.subplots(nrows=chartsToGenerate, sharex="all")

# allocate charts

if len(ganttData + linearData + areaData + eventData) > 1:
    ganttCharts = charts[0][chartIndicies[0] : (chartIndicies[0] + len(ganttData))]
    linearCharts = charts[0][chartIndicies[1] : (chartIndicies[1] + len(linearData))]
    areaCharts = charts[0][chartIndicies[2] : (chartIndicies[2] + len(areaData))]
    eventCharts = charts[0][chartIndicies[3] : (chartIndicies[3] + len(eventData))]
else:
    ganttCharts = charts[chartIndicies[0] : (chartIndicies[0] + len(ganttData))]
    linearCharts = charts[chartIndicies[1] : (chartIndicies[1] + len(linearData))]
    areaCharts = charts[chartIndicies[2] : (chartIndicies[2] + len(areaData))]
    eventCharts = charts[chartIndicies[3] : (chartIndicies[3] + len(eventData))]

### Biographical information

for database, chart in zip(ganttData, ganttCharts):

    ## Organize and sort biographical information

    # gantt dashes will be compacted. There will not be a single
    # row for every dash
    dashStacks = [ ]

    # simple greedy algorithm for stacking gantt dashes
    for dash in database.dashes():
        placed = False
        for stack in dashStacks: # look for the first stack the dash can be placed in
            if len(stack) < 1 or stack[len(stack) - 1].end < dash.start:
                stack.append(dash)
                placed = True
                break
        if not placed: # if it still hasn't been placed, create a new stack for it
            dashStacks.append([dash])
    
    dashStacks.reverse() # cosmetic

    ## Plot biographical information

    chart.set_yticks([])
    chart.grid(axis="x")

    for stack, level in zip(dashStacks, range(len(dashStacks))): # zip this with a random color object, don't worry, zip only uses shortest
        for dash in stack:
            chart.broken_barh([(dash.start, dash.duration())], (10 * level, 9))
            chart.text(dash.start + (dash.duration() / 2), 10 * level + 3, dash.name)

### Linear Data

for database, chart in zip(linearData, linearCharts):
    for series in database.serieses():
        chart.plot(database.allDates(), series)

### Area Data

for database, chart in zip(areaData, areaCharts):
    chart.stackplot(database.allDates(), database.allSerieses(), labels=database.getColumnLabels())
    chart.legend()

### Event Data

for database, chart in zip(eventData, eventCharts):

    # create an array with the level of each label. There is probably a better way to do this
    levels = numpy.tile([3, 2, 1], int(numpy.ceil(database.numItems()/3)))[:database.numItems()]

    markerline, stemline, baseline = chart.stem(database.allDates(), levels, use_line_collection=True)

    for event, level in zip(database.events(), levels):
        chart.annotate(event.brief, xy=(event.date, level), xytext=(0,0), textcoords="offset points", va="top", ha="left")

    markerline.set_ydata(numpy.zeros(database.numItems()))

    plt.setp(baseline, visible=False)

    chart.get_yaxis().set_visible(False)

### Plot the chart

minDate, maxDate = None, None

for base in (ganttData + linearData + eventData):
    if minDate == None or base.minDate() < minDate:
        minDate = base.minDate()
    if maxDate == None or base.maxDate() > maxDate:
        maxDate = base.maxDate()

plt.xlim(minDate, maxDate)

plt.show()