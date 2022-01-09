import re
import typing
import pandas
import numpy
import json

class Dash:
    """Simple struct used for iteration in building the Gantt Chart
    
    :cvar str name: The name of this task
    :cvar float start: The start date of this task
    :cvar float end: The end date of this task
    """
    def __init__(self, name: str, start: float, end: float):
        self.name = name
        self.start = start
        self.end = end
    
    def duration(self) -> float:
        """The duration of this task

        Determined by subtracting the start from the end dates

        :return: The duration of this task
        :rtype: float
        """
        return self.end - self.start

    def __repr__(self) -> str:
        """The string representation of this object

        "{self.name}, started {self.end}, ended {self.end}"

        :return: A string representing this object
        :rtype: str
        """
        return f"{self.name}, started {self.end}, ended {self.end}"

class Event:
    """Simple struct used for iteration in building the Gantt Chart

    :cvar float date: The date of this event
    :cvar str brief: A (brief) description of the event. The event's label
    """
    def __init__(self, date: float, brief: str):
        self.date = date
        self.brief = brief

class Series:
    """Encapsulates a numerical data series.
    
    It's basically a data series plus information on how to display it

    :cvar Pandas.Series data: The Pandas Series representation of the data
    :cvar Pandas.Series dates: The dates. Basically the index of the data
    :cvar str name: The name of the series
    :cvar boolean isPrimary: Indicates whether or not the data should be plotted against the primary or secondary axis
    :cvar boolean isDashed: Indicates whether or not the data should be drawn with the dashed line
    """
    def __init__(self, data: pandas.Series, name: str, isPrimary: bool, isDashed: bool):
        # self.data = data #Pandas
        # self.dates = data.index.to_series() #Pandas index

        self.data = [ ]
        self.dates = [ ]

        for index, value in data.items():
            self.data.append(value)
            self.dates.append(index)

        self.name = name
        self.isPrimary = isPrimary
        self.isDashed = isDashed

# This class is meant for a csv file with one column of dates and one
# or more columns of numerical data
class Database:
    """This class is meant for a CSV file with one column of dates and one or more columns of numerical data

    :param filename: The name of the file that contains the data
    :type filename: str
    """
    def __init__(self, filename: str):
        self.createDatabase(filename)

    def createDatabase(self, filename: str, hasIndexColumn: bool=True, columnLabels=None):
        file = open(filename, "r")

        # these methods mess with the file read head, be careful in changing them
        jsonStr = self.getJSONString(file) # read json string, if it exists
        hasHeader = self.isHeader(file.readline()) #
        file.seek(len(jsonStr)) # seek file back for reading

        # read the database
        if hasHeader: # pandas needs to be told if the file has a header or not
            self.database = pandas.read_csv(file, header=0)
        else:
            self.database = pandas.read_csv(file, header=None)
        if columnLabels != None:
            self.database.columns = columnLabels
        if hasIndexColumn: # an index column would be a series of dates
            self.database.set_index(self.database.columns[0], inplace=True)
        
        # we're done with the file
        file.close()

        self.parseSerieses(jsonStr)
    
    def getJSONString(self, file):
        if file.read(1) == "{":
            jsonStr = "{"

            matchParenthases = 1
            while matchParenthases > 0:
                char = file.read(1)
                if char == "{":
                    matchParenthases += 1
                elif char == "}":
                    matchParenthases -= 1
                jsonStr += char
            
            return jsonStr
        else:
            file.seek(0,0)
            return ""

    #fill out the series objects using optional json string
    def parseSerieses(self, jsonStr):
        self.serieses = [ ]
        addedColumns = [ ] # to avoid duplication of series
        if jsonStr != "":
            jsonObj = json.loads(jsonStr)

            if "primaryAxis" in jsonObj:
                axSpec = jsonObj["primaryAxis"]

                # first parse out axis specifications, if any
                self.primaryMax = axSpec["max"] if "max" in axSpec else None
                self.primaryMin = axSpec["max"] if "min" in axSpec else None
                self.primaryInterval = axSpec["interval"] if "interval" in axSpec else None

                # then parse out specifications for any mentioned columns
                if "columns" in axSpec:
                    for column in axSpec["columns"]:
                        self.serieses.append(Series(
                            self.database[column["name"]],
                            column["name"], # this is not optional. You must name the column
                            True,
                            True if "style" in column and column["style"] == "dashed" else False
                        ))
                        addedColumns.append(column["name"])
            else:
                self.primaryMax, self.primaryMin, self.primaryInterval = None, None, None

            if "secondaryAxis" in jsonObj:
                axSpec = jsonObj["secondaryAxis"]
                self.secondaryMax = axSpec["max"] if "max" in axSpec else None
                self.secondaryMin = axSpec["max"] if "min" in axSpec else None
                self.secondaryInterval = axSpec["interval"] if "interval" in axSpec else None
                if "columns" in axSpec:
                    for column in axSpec["columns"]:
                        self.serieses.append(Series(
                            self.database[column["name"]],
                            column["name"],
                            False,
                            True if "style" in column and column["style"] == "dashed" else False
                        ))
                        addedColumns.append(column["name"])
            else:
                self.secondaryMax, self.secondaryMin, self.secondaryInterval = None, None, None
        
        for column in self.database.columns:
            if column not in addedColumns:
                self.serieses.append(Series(
                    self.database[column],
                    column,
                    True,
                    False
                ))


    # This regex basically looks for a number that takes up an entire column. If a row has a number that
    # takes up an entire column, then the row probably isn't a header.
    headerRegex = re.compile(r"^-?[0-9]+\.?[0-9]*[,\t]|[,\t]-?[0-9]+\.?[0-9]*[,\t]|[,\t]-?[0-9]+\.?[0-9]*$")
    def isHeader(self, line):
        return self.headerRegex.search(line) == None
    
    def numItems(self) -> int:
        """Return the number of data points

        :return: The number of data points
        :rtype: int
        """
        return len(self.database.index)
    
    def minDate(self) -> float:
        """Returns the earliest date in the database

        :return: The earliest date in the database
        :rtype: float
        """
        return self.database.index.min()
    
    def maxDate(self) -> float:
        """Returns the latest date in the database

        :return: The latest date in the database
        :rtype: float
        """
        return self.database.index.max() #Pandas
    
    def allDates(self) -> typing.List[float]:
        """Return a Pandas series of all the dates
        
        :return: A series of all the dates
        :rtype: A Pandas series
        """

        dates = [ ]
        for index, value in self.database.index.to_series().items():
            dates.append(value)

        return dates
    
    # return a Series object, which encapsulate a Pandas series
    def seriesGenerator(self) -> Series: #standard plural form
        """A generator that yields all the serieses in this database

        :return: A Series that encapsulates a Pandas series
        :rtype: Series
        """
        for series in self.serieses:
            yield series

    def allSerieses(self) -> typing.List[Series]:
        """``seriesGenerator()``, but not a generator

        :return: All the Serieses in the database
        :rtype: list[Series]
        """
        retSerieses = []
        for column in self.database.columns:
            retSerieses.append(self.database[column])
        return retSerieses

    # returns a pandas series
    def getColumnLabels(self) -> typing.List[str]:
        """Return all the column labels

        :return: The labels for all the columns in the database
        :rtype: A Pandas Series
        """
        
        labels = [ ]
        for index, value in self.database.columns.to_series().items():
            labels.append(value)

        return labels

    def __repr__(self) -> str:
        """Return the string representation of this database.

        :return: The string representation of the internal Pandas database
        :rtype: str
        """
        return repr(self.database)

class GanttDatabase(Database):
    """A database for Gantt data
    
    """
    def __init__(self, filename):
        self.createDatabase(filename, hasIndexColumn=False, columnLabels=["name","start","end"])
        self.database.sort_values(by="start", inplace=True, ignore_index=True) # it's useful to have it sorted this way
    
    def minDate(self) -> float:
        """Get the earliest date on the chart
        
        Get the start date of the first task

        :return: Start date of first task
        :rtype: float
        """
        return self.minStartDate()
    
    def maxDate(self) -> float:
        """Get the latest date on the chart

        Get the end date of the last task to be finished

        When these two methods are defined this way, you can use them to get a range for a chart

        :return: End date of the last task
        :rtype: float
        """
        return self.maxEndDate()
    
    def minStartDate(self) -> float:
        """Get the start date of the first task to be started

        :return: Start date of first task
        :rtype: float
        """
        return self.database["start"].min()
    
    def maxStartDate(self) -> float:
        """Get the start date of the last task *to be started*

        :return: Start date of the last task to be started
        :rtype: float
        """
        return self.database["start"].max()
    
    def minEndDate(self) -> float:
        """Get the end date of the first task to end

        :return: The end date of the first task to end
        :rtype: float
        """
        return self.database["end"].min()
    
    def maxEndDate(self) -> float:
        """Get the end date of the last task to end

        :return: The end date of the last task to end
        :rtype: float
        """
        return self.database["end"].max()
    
    def dashes(self) -> Dash:
        """Yield all the dashes in this collection

        :return: A dash
        :rtype: Iterator[:class:`Dash`]
        """
        for record in self.database.itertuples():
            yield Dash(record.name, record.start, record.end)
    
    # a naive approach requiring O(n^2) time and O(n) space
    # but unless you have thousands of people, it isn't worth
    # the time to build a tree
    def maxOverlaps(self) -> int:
        """Gets the maximum number of tasks that take place at the same time

        :return: The maximum number of tasks that take place at the same time
        :rtype: int
        """
        maximum = 0
        currentOverlaps = numpy.array( [ ] ) # end points
        for dash in self.dashes():
            currentOverlaps = currentOverlaps[currentOverlaps >= dash.start]
            currentOverlaps = numpy.append(currentOverlaps, dash.end)
            maximum = max(maximum, len(currentOverlaps))
        return maximum

class EventDatabase(Database):
    """A collection of events.

    Events are just labeled points in time
    """
    def __init__(self, filename):
        # because there may be multiple events on the same date, DO NOT take the date column
        # as the index
        self.createDatabase(filename, hasIndexColumn=False, columnLabels=["date","brief"])
    
    def minDate(self) -> float:
        """The date of the earliest event

        :rtype: float
        """
        return self.database["date"].min()
    
    def maxDate(self) -> float:
        """The date of the latest event

        :rtype: float
        """
        return self.database["date"].max()
    
    # since the date column can't be the index, return the date column itself
    def allDates(self) -> pandas.Series:
        """Return all the dates in the collection

        since the date column can't be the index, return the date column itself

        :return: All the dates in the collection
        :rtype: A Pandas series?
        """

        dates = [ ]
        for index, value in self.database['date'].items():
            dates.append(value)

        return dates
    
    def events(self) -> Event:
        """A generator with returns all the events in the collection

        :return: Every event in the collection
        :rtype: Iterator[:class:`Event`]
        """
        for record in self.database.itertuples():
            yield Event(record.date, record.brief)
