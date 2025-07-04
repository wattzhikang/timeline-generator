import argparse
import matplotlib.pyplot as plt
import numpy
import json

from timelineData import *
from colorGenerator import ColorGenerator

### Biographical information

# for database in ganttData:
def ganttChart(database: GanttDatabase, chartIndex: int):

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
                if len(stack) < 1 or stack[len(stack) - 1].maxEnd <= dash.start:
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
        for dash, (hue, lighterHue) in zip(stack, ColorGenerator()):
            chart.broken_barh([(dash.start, dash.duration())], (10 * level, 9), color=hue)
            if dash.extendTo is not None:
                # If this dash is to be extended, put another dash at the end of this dash
                # that has a dashed line border, and that lighter color as the fill
                chart.broken_barh([(dash.end, dash.extendedDuration())], (10 * level, 9), color=lighterHue, linestyle="--")
            if dataFileJSON['start'] is not None and dash.start > dataFileJSON['start']:
                chart.text(dash.start + (dash.duration() * 0.33), 10 * level + 3, dash.name, rotation=30)
            else:
                # otherwise the text will be off the chart
                # so place the text at the beginning of the chart, and not the beginning of the dash
                chart.text(dataFileJSON['start'], 10 * level + 3, dash.name, rotation=30)

### Linear Data

# for database in linearData:
def linearChart(database: Database, chartIndex: int):
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

### Area Data

# for database in areaData:
def areaChart(database: Database, chartIndex: int):
    chart = plt.gcf().add_subplot(gdspec[chartIndex])

    chart.stackplot(database.allDates(), database.allValues(), labels=database.getColumnLabels())
    chart.legend()

### Event Data

# for database in eventData:
def eventChart(database: EventDatabase, chartIndex: int):
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

databases = [ ]
ganttData = [ ]
linearData = [ ]
areaData = [ ]
eventData = [ ]
for chart in dataFileJSON['charts']:
    print(type(chart))
    if chart['type'] == 'gantt':
        databases.append(GanttDatabase(chart))
        ganttData.append(databases[len(databases) - 1])
    elif chart['type'] == 'event':
        databases.append(EventDatabase(chart))
        eventData.append(databases[len(databases) - 1])
    elif chart['type'] == 'linear':
        databases.append(Database(chart))
        linearData.append(databases[len(databases) - 1])
    elif chart['type'] == 'area':
        databases.append(Database(chart))
        areaData.append(databases[len(databases) - 1])

### Get applicable subplots

import matplotlib.pyplot as plt
from matplotlib import gridspec

# calculate height ratios for the plots, shrinking gantt plots with fewer elements
heights = [ ]

# Get the maximum number of overlaps for all gantt charts
# and use that to scale the height of the gantt charts
maxGantt = 1
if len(ganttData) > 0:
    maxGantt = max(ganttData, key= lambda database : database.maxOverlaps).maxOverlaps
# for database in ganttData:
#     heights.append(database.maxOverlaps / maxGantt)

# heights = heights + ([ 1 ] * len(linearData + areaData))
# heights = heights + ([0.5] * len(eventData))

for database in databases:
    if database.type == 'gantt':
        heights.append(database.maxOverlaps / maxGantt)
    elif database.type == 'linear':
        heights.append(1.0)
    elif database.type == 'area':
        heights.append(1.0)
    elif database.type == 'event':
        heights.append(0.5)

gdspec = gridspec.GridSpec(len(databases), 1, height_ratios=heights)

# running index for charts
chartIndex = 0
for database in databases:
    if database.type == 'gantt':
        ganttChart(database, chartIndex)
    elif database.type == 'linear':
        linearChart(database, chartIndex)
    elif database.type == 'area':
        areaChart(database, chartIndex)
    elif database.type == 'event':
        eventChart(database, chartIndex)
    chartIndex += 1

### Plot the chart

minDate, maxDate = None, None

# if the chart description does not manually specify a date range, use the min and max dates from the data
# otherwise, use the specified range
if 'start' not in dataFileJSON or 'end' not in dataFileJSON:
    for base in (ganttData + linearData + eventData):
        print(base)
        if minDate == None or base.minDate < minDate:
            minDate = base.minDate
        if maxDate == None or base.maxDate > maxDate:
            maxDate = base.maxDate

if 'start' in dataFileJSON:
    minDate = dataFileJSON['start']

if 'end' in dataFileJSON:
    maxDate = dataFileJSON['end']

for ax in plt.gcf().get_axes():
    ax.set_xlim(minDate, maxDate)

# users can specify a year interval for ticks
# set the ticks for every chart
if 'majorInterval' in dataFileJSON:
    for ax in plt.gcf().get_axes():
        ax.xaxis.set_major_locator(plt.MultipleLocator(dataFileJSON['majorInterval']))

if 'minorInterval' in dataFileJSON:
    for ax in plt.gcf().get_axes():
        ax.xaxis.set_minor_locator(plt.MultipleLocator(dataFileJSON['minorInterval']))

plt.show()