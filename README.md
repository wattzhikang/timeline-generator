# Timeline Chart Generator

This program takes one or more input files and produces a time graph. Supported (and planned) features include:

* **[Gantt charts](https://en.wikipedia.org/wiki/Gantt_chart)** can be used to plot lifespans, events with duration, eras and historical periods, etc. Biographical Gantt charts can look much like [this example](https://en.wikipedia.org/wiki/A_Chart_of_Biography).

* **Numerical data** can be plotted as a [line chart](https://en.wikipedia.org/wiki/Line_chart) or a stacked area chart, depending on the command line switch

* **Text timelines** for events without duration

## Status

Most planned features supported. The charts should look prettier, though.

## Input file format

Currently this program only supports data files in CSV (comma-separated values) format, although there are plans to add the ability to read data from Excel and OpenDocument spreadsheets, and even JSON.

Files are not required to have column labels, but they may be useful for chart legends in numerical data. The program should have the ability to detect the presence or absence of column labels.

### Date format

Currently, the program only supports decimal numbers for time indexing. Those decimal numbers can represent whatever you want (years, days, etc).

There are plans to support more date formats.

### Gantt Data

Three columns:

1. **Name**: a string containing the name of the event
2. **Start Date**: a decimal number representing the start of the event
3. **Death Date**: a decimal number representing the end of the event

```
John Smith,-15.8,40.01
Jane Smith,-13.14,50.6
Archie Smith,10.9,98.6
```

### Numerical Data

At least two columns:

1. **Date**: the date of the observation
2. **Number**: the numerical value at the date
n. *More Numbers*: more numerical values at the same date

```
1.4,7.825
2.6,14.21
5.1,28.6
7,56.98
8.5,112.5
```

### Event Data

Two columns:

1. **Date**: the date of the event
2. **Event**: a string describing or naming the event

```
1.4,A thing happened
12,Another thing happened
```

## Usage

This program is invoked from the command line. There are two switches for the two different types of data:

* **-g**: Gantt chart data
* **-l**: Linear numerical data
* **-a**: Area data for a stacked area chart
* **-e**: Event data

There will be one file generated per chart

### Example

```bash
python3 timeline -g importantPeople.csv importantProjects.csv -l gdp.csv population.csv -a energyProduction.csv -e events.csv
```