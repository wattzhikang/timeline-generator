import argparse
import matplotlib.pyplot as plt
import numpy
import json

from timelineData import *
from colorGenerator import ColorGenerator

### Set up the Argument Parser to retrieve arguments from the user

parser = argparse.ArgumentParser(
    description="A simple python tool for creating time-based charts based on multiple types of data"
)
parser.add_argument(
    nargs=1,
    help='Data file',
    dest='dataFilePath',
    metavar='data.json'
)

dataFilePath = parser.parse_args().dataFilePath[0]

### Construct database objects

dataFile = open(dataFilePath)
dataFileJSON = json.load(dataFile)

ganttData = [ ]
linearData = [ ]
areaData = [ ]
eventData = [ ]
for chart in dataFileJSON['charts']:
    print(type(chart))
    if chart['type'] == 'gantt':
        ganttData.append(GanttDatabase(chart))
    elif chart['type'] == 'event':
        eventData.append(EventDatabase(chart))
    elif chart['type'] == 'linear':
        linearData.append(Database(chart))
    elif chart['type'] == 'area':
        areaData.append(Database(chart))

### Get applicable subplots

import matplotlib.pyplot as plt
from matplotlib import gridspec

if len(ganttData) != 0:
# calculate height ratios for the plots, shrinking gantt plots with fewer elements
    maxGantt = max(ganttData, key= lambda database : database.maxOverlaps).maxOverlaps
    heights = [ ]
    for database in ganttData:
        heights.append(database.maxOverlaps / maxGantt)
    heights = heights + ([ 1 ] * len(linearData + areaData))
    heights = heights + ([0.5] * len(eventData))

    print(heights)
else:
    heights = numpy.repeat(1.0, len(ganttData + linearData + areaData + eventData))

gdspec = gridspec.GridSpec(len(ganttData + linearData + areaData + eventData), 1, height_ratios=heights)



# running index for charts
chartIndex = 0

### Biographical information

for database in ganttData:

    ## Organize and sort biographical information

    # gantt dashes will be compacted. There will not be a single
    # row for every dash
    dashStacks = [ ]

    # simple greedy algorithm for stacking gantt dashes
    for dash in database.dashes:
        if dash.column != None: # if a column is specified, place it in that column
            # if the column doesn't exist, create it by adding empty stacks
            while len(dashStacks) < dash.column + 1:
                dashStacks.append([ ])
            dashStacks[dash.column].append(dash)
        else: # otherwise, place it in the first available stack
            placed = False
            for stack in dashStacks: # look for the first stack the dash can be placed in
                if len(stack) < 1 or stack[len(stack) - 1].end <= dash.start:
                    stack.append(dash)
                    placed = True
                    break
            if not placed: # if it still hasn't been placed, create a new stack for it
                dashStacks.append([dash])
    
    dashStacks.reverse() # cosmetic

    ## Plot biographical information

    chart = plt.gcf().add_subplot(gdspec[chartIndex])

    chart.set_yticks([])
    chart.grid(axis="x")

    for stack, level in zip(dashStacks, range(len(dashStacks))): # zip this with a random color object, don't worry, zip only uses shortest
        for dash, hue in zip(stack, ColorGenerator()):
            chart.broken_barh([(dash.start, dash.duration())], (10 * level, 9), color=hue)
            chart.text(dash.start + (dash.duration() * 0.33), 10 * level + 3, dash.name)
    
    chartIndex += 1

### Linear Data

for database in linearData:
    primary = plt.gcf().add_subplot(gdspec[chartIndex])
    secondary = primary.twinx()

    for series in database.serieses:
        chart = primary if series.isPrimary else secondary
        style = "--" if series.isDashed else "-"

        chart.plot(series.dates, series.data, label=series.name, linestyle=style)
    
    primary.legend(loc=2)
    if database.primaryAxis is not None:
        primary.set_ylim(bottom=database.primaryAxis.min, top=database.primaryAxis.max)
    secondary.legend(loc=1)
    if database.secondaryAxis is not None:
        print(f'max: {database.secondaryAxis.max}')
        print(f'min: {database.secondaryAxis.min}')
        secondary.set_ylim(bottom=database.secondaryAxis.min, top=database.secondaryAxis.max)

    chartIndex += 1

### Area Data

for database in areaData:
    chart = plt.gcf().add_subplot(gdspec[chartIndex])

    chart.stackplot(database.allDates(), database.allValues(), labels=database.getColumnLabels())
    chart.legend()

    chartIndex += 1

### Event Data

for database in eventData:
    chart = plt.gcf().add_subplot(gdspec[chartIndex])

    # create an array with the level of each label. There is probably a better way to do this
    levels = numpy.tile([2, 1], int(numpy.ceil(len(database)/2)))[:len(database)]

    markerline, stemline, baseline = chart.stem(database.dates, levels)

    for event, level in zip(database.events, levels):
        chart.annotate(
            event.brief,
            xy=(event.date, level),
            xytext=(0,0),
            textcoords="offset points",
            va="top", ha="left",
            rotation_mode="anchor",
            rotation=45
        )

    markerline.set_ydata(numpy.zeros(len(database))) #brings dots down to the bottom for clarity
    chart.set_ylim(0,3) # give room for the text

    plt.setp(baseline, visible=False)
    chart.get_yaxis().set_visible(False)

    chartIndex += 1

### Plot the chart

minDate, maxDate = None, None

# if the chart description does not manually specify a date range, use the min and max dates from the data
# otherwise, use the specified range
if dataFileJSON['start'] is None or dataFileJSON['end'] is None:
    for base in (ganttData + linearData + eventData):
        print(base)
        if minDate == None or base.minDate < minDate:
            minDate = base.minDate
        if maxDate == None or base.maxDate > maxDate:
            maxDate = base.maxDate

if dataFileJSON['start'] is not None:
    minDate = dataFileJSON['start']

if dataFileJSON['end'] is not None:
    maxDate = dataFileJSON['end']

for ax in plt.gcf().get_axes():
    ax.set_xlim(minDate, maxDate)

plt.show()