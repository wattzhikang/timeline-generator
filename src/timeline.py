import argparse
import matplotlib.pyplot as plt
import numpy

from timelineData import *
from colorGenerator import ColorGenerator

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

if dashFiles == None and linearFiles == None and areaFiles == None and labelFiles == None:
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
from matplotlib import gridspec

if len(ganttData) != 0:
# calculate height ratios for the plots, shringking gantt plots with fewer elements
    maxGantt = max(ganttData, key= lambda database : database.maxOverlaps()).maxOverlaps()
    heights = [ ]
    for database in ganttData:
        heights.append(database.maxOverlaps() / maxGantt)
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
    for dash in database.dashes():
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
    secondary.legend(loc=1)

    chartIndex += 1

### Area Data

for database in areaData:
    chart = plt.gcf().add_subplot(gdspec[chartIndex])

    chart.stackplot(database.allDates(), database.allSerieses(), labels=database.getColumnLabels())
    chart.legend()

    chartIndex += 1

### Event Data

for database in eventData:
    chart = plt.gcf().add_subplot(gdspec[chartIndex])

    # create an array with the level of each label. There is probably a better way to do this
    levels = numpy.tile([2, 1], int(numpy.ceil(database.numItems()/2)))[:database.numItems()]

    markerline, stemline, baseline = chart.stem(database.allDates(), levels, use_line_collection=True)

    for event, level in zip(database.events(), levels):
        chart.annotate(
            event.brief,
            xy=(event.date, level),
            xytext=(0,0),
            textcoords="offset points",
            va="top", ha="left",
            rotation_mode="anchor",
            rotation=45
        )

    markerline.set_ydata(numpy.zeros(database.numItems())) #brings dots down to the bottom for clarity
    chart.set_ylim(0,3) # give room for the text

    plt.setp(baseline, visible=False)
    chart.get_yaxis().set_visible(False)

    chartIndex += 1

### Plot the chart

minDate, maxDate = None, None

for base in (ganttData + linearData + eventData):
    if minDate == None or base.minDate() < minDate:
        minDate = base.minDate()
    if maxDate == None or base.maxDate() > maxDate:
        maxDate = base.maxDate()

for ax in plt.gcf().get_axes():
    ax.set_xlim(minDate, maxDate)

plt.show()