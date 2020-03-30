import re
import pandas
import numpy
import json

# Simple struct used for iteration in building the Gantt Chart
class Dash:
    def __init__(self, name, start, end):
        self.name = name
        self.start = start
        self.end = end
    
    def duration(self):
        return self.end - self.start

    def __repr__(self):
        return f"{self.name}, started {self.end}, ended {self.end}"

# Simple struct used for iteration in building the Gantt Chart
class Event:
    def __init__(self, date, brief):
        self.date = date
        self.brief = brief

# This class is meant for a csv file with one column of dates and one
# or more columns of numerical data
class Database:
    def __init__(self, filename):
        self.createDatabase(filename)

    def createDatabase(self, filename, hasIndexColumn=True, columnLabels=None):
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

        # parse the json string, if it exists
        if jsonStr != "":
            jsonObj = json.loads(jsonStr)

            # parse out which columns go on which axis
            self.leftColumns = [ ]
            self.rightColumns = [ ]
            for column in self.database.columns:
                if "rightAxis" in jsonObj and column in jsonObj["rightAxis"]:
                    self.rightColumns.append(column)
                else:
                    self.leftColumns.append(column)

            # parse out axis scales, if they exist
            if "leftAxisMax" in jsonObj:
                self.leftAxisMax = jsonObj["leftAxisMax"]
            else:
                self.leftAxisMax = None
            if "leftAxisMin" in jsonObj:
                self.leftAxisMin = jsonObj["leftAxisMin"]
            else:
                self.leftAxisMin = None
            if "rightAxisMax" in jsonObj:
                self.rightAxisMax = jsonObj["rightAxisMax"]
            else:
                self.rightAxisMax = None
            if "rightAxisMin" in jsonObj:
                self.rightAxisMin = jsonObj["rightAxisMin"]
            else:
                self.rightAxisMin = None
        else:
            self.leftColumns = self.database.columns
            self.rightColumns = [ ]
    
    def getJSONString(self, file):
        if file.read(1) == "{":
            file.seek(0,0)
            str = ""
            char = file.read(1)
            while char != "}":
                str += char
                char = file.read(1)
            str += char
            return str
        else:
            file.seek(0,0)
            return ""

    # This regex basically looks for a number that takes up an entire column. If a row has a number that
    # takes up an entire column, then the row probably isn't a header.
    headerRegex = re.compile(r"^-?[0-9]+\.?[0-9]*[,\t]|[,\t]-?[0-9]+\.?[0-9]*[,\t]|[,\t]-?[0-9]+\.?[0-9]*$")
    def isHeader(self, line):
        return self.headerRegex.search(line) == None
    
    def numItems(self):
        return len(self.database.index)
    
    def minDate(self):
        return self.database.index.min()
    
    def maxDate(self):
        return self.database.index.max()
    
    # returns a pandas series
    def allDates(self):
        return self.database.index.to_series()
    
    # returns a pandas series
    def serieses(self): #standard plural form
        for column in self.database.columns:
            yield self.database[column]

    def leftSerieses(self):
        serieses = []
        for column in self.database.columns:
            if column in self.leftColumns:
                serieses.append(self.database[column])
        return serieses
    
    def rightSerieses(self):
        serieses = []
        for column in self.database.columns:
            if column in self.rightColumns:
                serieses.append(self.database[column])
        return serieses
    
    # returns a list of pandas serieses
    def allSerieses(self):
        retSerieses = []
        for column in self.database.columns:
            retSerieses.append(self.database[column])
        return retSerieses
    
    # returns a pandas series
    def getColumnLabels(self):
        return self.database.columns.to_series()

    def __repr__(self):
        return repr(self.database)

class GanttDatabase(Database):
    def __init__(self, filename):
        self.createDatabase(filename, hasIndexColumn=False, columnLabels=["name","start","end"])
        self.database.sort_values(by="start", inplace=True, ignore_index=True) # it's useful to have it sorted this way
    
    # defined as the start date of the first task
    def minDate(self):
        return self.minStartDate()
    
    # defined as the end date of the last task to be finished
    # when these two methods are defined this way, you can use them to get a range for a chart
    def maxDate(self):
        return self.maxEndDate()
    
    # start date of the first task
    def minStartDate(self):
        return self.database["start"].min()
    
    # start date of task started last
    def maxStartDate(self):
        return self.database["start"].max()
    
    # end date of earliest task to be finished
    def minEndDate(self):
        return self.database["end"].min()
    
    # end date of last task to be finished
    def maxEndDate(self):
        return self.database["end"].max()
    
    # returns all the dashes in this database
    def dashes(self):
        for record in self.database.itertuples():
            yield Dash(record.name, record.start, record.end)
    
    # a naive approach requiring O(n^2) time and O(n) space
    # but unless you have thousands of people, it isn't worth
    # the time to build a tree
    def maxOverlaps(self):
        maximum = 0
        currentOverlaps = numpy.array( [ ] ) # end points
        for dash in self.dashes():
            currentOverlaps = currentOverlaps[currentOverlaps >= dash.start]
            currentOverlaps = numpy.append(currentOverlaps, dash.end)
            maximum = max(maximum, len(currentOverlaps))
        return maximum

class EventDatabase(Database):
    def __init__(self, filename):
        # because there may be multiple events on the same date, DO NOT take the date column
        # as the index
        self.createDatabase(filename, hasIndexColumn=False, columnLabels=["date","brief"])
    
    def minDate(self):
        return self.database["date"].min()
    
    def maxDate(self):
        return self.database["date"].max()
    
    # since the date column can't be the index, return the date column itself
    def allDates(self):
        return self.database["date"]
    
    def events(self):
        for record in self.database.itertuples():
            yield Event(record.date, record.brief)
