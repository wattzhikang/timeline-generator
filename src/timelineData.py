import typing
import numpy

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
    def __init__(self, data: typing.List[float], index: typing.List[float], name: str, isPrimary: bool, isDashed: bool):
        # self.data = data #Pandas
        # self.dates = data.index.to_series() #Pandas index

        self.data = data
        self.dates = index
        self.name = name
        self.isPrimary = isPrimary
        self.isDashed = isDashed

class Axis:
    """Represents an axis
    
    :cvar max: The maximum value on the axis
    :cvar min: The minimum value on the axis
    :cvar interval: The interval of the axis
    """
    def __init__(self, max: float, min: float, interval: float) -> None:
        self.max = max
        self.min = min
        self.interval = interval

# This class is meant for a csv file with one column of dates and one
# or more columns of numerical data
class Database:
    """This class is meant for a CSV file with one column of dates and one or more columns of numerical data

    :param filename: The name of the file that contains the data
    :type filename: str
    """
    def __init__(self, chartJSON: dict):
        self.createDatabase(chartJSON)

    def createDatabase(self, chartJSON: dict):
        self.title = chartJSON['title']

        self.serieses = [ ]

        self.primaryAxis = None
        if 'primaryAxis' in chartJSON:
            maximum = chartJSON['primaryAxis']['max']
            minimum = chartJSON['primaryAxis']['min']
            interval = chartJSON['primaryAxis']['interval']
            print(f'max: {maximum}')
            print(f'min: {minimum}')
            self.primaryAxis = Axis(maximum, minimum, interval)
        
        self.secondaryAxis = None
        if 'secondaryAxis' in chartJSON:
            maximum = chartJSON['secondaryAxis']['max']
            minimum = chartJSON['secondaryAxis']['min']
            interval = chartJSON['secondaryAxis']['interval']
            self.secondaryAxis = Axis(maximum, minimum, interval)

        for series in chartJSON['data']:
            data = [ ]
            index = [ ]
            for entry in series['entries']:
                data.append(entry['value'])
                index.append(entry['date'])
            title = series['title']
            isPrimary = True
            if 'axis' in series and series['axis'] == 'secondary':
                isPrimary = False
            isDashed = False
            if 'style' in series and series['style'] == 'dashed':
                isDashed = True
            self.serieses.append(Series(data, index, title, isPrimary, isDashed))

        self.minDate = min(self.serieses[0].dates)
        self.maxDate = max(self.serieses[0].dates)

    def numItems(self) -> int:
        """Return the number of data points

        :return: The number of data points
        :rtype: int
        """
        return len(self.serieses[0].data)
    
    def allDates(self) -> typing.List[float]:
        """Return a Pandas series of all the dates
        
        :return: A series of all the dates
        :rtype: A Pandas series
        """

        return self.serieses[0].dates
    
    # return a Series object, which encapsulate a Pandas series
    def seriesGenerator(self) -> Series: #standard plural form
        """A generator that yields all the serieses in this database

        :return: A Series that encapsulates a Pandas series
        :rtype: Series
        """
        for series in self.serieses:
            yield series

    def allValues(self) -> typing.List[Series]:
        """``seriesGenerator()``, but not a generator

        :return: All the Serieses in the database
        :rtype: list[Series]
        """
        values = [ ]
        for series in self.serieses:
            values.append(series.data)
        return values

    # returns a pandas series
    def getColumnLabels(self) -> typing.List[str]:
        """Return all the column labels

        :return: The labels for all the columns in the database
        :rtype: A Pandas Series
        """
        
        labels = [ ]
        for series in self.serieses:
            labels.append(series.name)

        return labels

    # TODO: rewrite
    # def __repr__(self) -> str:
    #     """Return the string representation of this database.

    #     :return: The string representation of the internal Pandas database
    #     :rtype: str
    #     """
    #     return repr(self.database)

class GanttDatabase:
    """A database for Gantt data
    
    """
    def __init__(self, chartJSON: dict):
        self.createDatabase(chartJSON)
    
    def createDatabase(self, chartJSON: dict):
        self.title = chartJSON['title']

        self.minStartDate = None
        self.maxStartDate = None
        self.minEndDate = None
        self.maxEndDate = None

        self.dashes = [ ]
        for dashJSON in chartJSON['data']:
            name = dashJSON['label']
            start = dashJSON['start']
            end = dashJSON['end']

            dash = Dash(name, start, end)

            if self.minStartDate is None or start < self.minStartDate:
                self.minStartDate = start
            if self.maxStartDate is  None or self.maxStartDate < start:
                self.maxStartDate = start
            if self.minEndDate is None or end < self.minEndDate:
                self.minEndDate = end
            if self.maxEndDate is None or self.maxEndDate < end:
                self.maxEndDate = end

            self.dashes.append(dash)
        self.dashes.sort(key = lambda dash : dash.start)

        self.minDate = self.minStartDate
        self.maxDate = self.maxEndDate
    
    def dashes(self) -> Dash:
        """Yield all the dashes in this collection

        :return: A dash
        :rtype: Iterator[:class:`Dash`]
        """
        for dash in self.dashes:
            yield dash
    
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
        for dash in self.dashes:
            currentOverlaps = currentOverlaps[currentOverlaps >= dash.start]
            currentOverlaps = numpy.append(currentOverlaps, dash.end)
            maximum = max(maximum, len(currentOverlaps))
        return maximum

class EventDatabase:
    """A collection of events.

    Events are just labeled points in time
    """
    def __init__(self, chartJSON: dict):
        # because there may be multiple events on the same date, DO NOT take the date column
        # as the index
        self.createDatabase(chartJSON)
    
    def createDatabase(self, chartJSON: dict):
        self.title = chartJSON['title']

        self.minDate = None
        self.maxDate = None

        self.dates = [ ]
        self.events = [ ]
        for eventJSON in chartJSON['data']:
            brief = eventJSON['label']
            date = eventJSON['date']
            
            self.dates.append(date)
            self.events.append(Event(date, brief))

            if self.minDate is None or date < self.minDate:
                self.minDate = date
            if self.maxDate is None or self.maxDate < date:
                self.maxDate = date
    
    def events(self) -> Event:
        """A generator with returns all the events in the collection

        :return: Every event in the collection
        :rtype: Iterator[:class:`Event`]
        """
        for event in self.events:
            yield event
    
    def __len__(self):
        return len(self.events)
