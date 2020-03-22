# Timeline Chart Generator

This program takes one or more input files and produces a time graph. Supported (and planned) features include:

* If the input file contains **biographical data**, the resulting output will take the form of a [Gantt chart](https://en.wikipedia.org/wiki/Gantt_chart), much like [this example](https://en.wikipedia.org/wiki/A_Chart_of_Biography).

* If the input file contains one or more columns of **numerical data**, the output will take the form of a [line chart](https://en.wikipedia.org/wiki/Line_chart). If there are multiple columns of data, the result will be a stacked line chart.

* If the input file contains a single column of text data (and an obligatory date column), the output will result in a text timeline.

## Status

Basic biographical Gantt charts are now supported. Line charts and stacked area charts now supported. Basic timelines are now supported. NOTE: only one file per feature is supported. This will change in the future.
## Input file format

Currently this program only supports data files in CSV (comma-separated values) format, although there are plans to add the ability to read data from Excel and OpenDocument spreadsheets, and even JSON.

### Date format

Currently, the program only supports decimal numbers for time indexing. Those decimal numbers can represent whatever you want (years, days, etc).

There are plans to support more date formats.

### Biographical Data

Four columns:

1. **Name**: a string containing the name of the person
2. **Birth Date**: a decimal number representing the birth date of the person
3. **Death Date**: a decimal number representing the death date of the person

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

* **-b**: biographical data. Data from multiple files will be combined into the same chart.
* **-d**: numerical data: Each file will be depicted in a different (but parallel) chart. If you want to show related data in one chart, use multiple columns in stead.
* **-e**: event data: Data from multiple files will be combined into the same chart.

DO NOT use multiple instances of the same switch (eg "timeline -b some-data.csv -b some-more-data.csv").

### Example

```bash
timeline -b importantPeople.csv importantEvents.csv -n energyProduction.csv population.csv -e events.csv
```