import re
import pandas
import numpy

class Person:
    def __init__(self, name, birth, death):
        self.name = name
        self.birth = birth
        self.death = death
    
    def lifespan(self):
        return self.death - self.birth

    def __repr__(self):
        return f"{self.name}, born {self.birth}, died {self.death}"

class Data:
    def createDatabase(self, columnLabels=None, filename=None, indexColumn=False):
        database = None
        # if no input file, cretae blank database
        if filename == None:
            if columnLabels == None:
                database = pandas.DataFrame()
            else:
                database = pandas.DataFrame(columns=columnLabels)
        else:
            file = open(filename, "r")
            if self.hasHeader(file):
                database = pandas.read_csv(file, header=0)
            else:
                database = pandas.read_csv(file, header=None)
            file.close()
            if columnLabels != None:
                database.columns = columnLabels
        if indexColumn:
            database = database.set_index(database.columns[0])
        return database

    headerRegex = re.compile(r"\-?[0-9]+\.?[0-9]*.\-?[0-9]+\.?[0-9]*")
    def hasHeader(self, file):
        file.seek(0,0)
        headerPresent = self.headerRegex.search(file.readline()) == None
        file.seek(0,0)
        return headerPresent
    
    def numItems(self):
        return len(self.database.index)
    
    def __repr__(self):
        return repr(self.database)

class PersonDatabase(Data):
    columns = ["name","birth","death"]

    def __init__(self):
        self.database = self.createDatabase(columnLabels=self.columns)
    
    def addData(self, fileName):
        newDatabase = self.createDatabase(filename=fileName, columnLabels=self.columns)
        self.database = pandas.concat([self.database, newDatabase], ignore_index=True, sort=False)

    def sortByBirthDate(self):
        self.database = self.database.sort_values(by="birth")
    
    def minBirthDate(self):
        return self.database["birth"].min()
    
    def maxDeathDate(self):
        return self.database["death"].max()
    
    def people(self):
        for row in self.database.itertuples():
            yield Person(row.name, row.birth, row.death)

class NumericalData(Data):
    def __init__(self, fileName):
        self.database = self.createDatabase(filename=fileName, indexColumn=True)
    
    def getTimeIndex(self):
        return self.database.index
    
    def allColumns(self):
        serieses = []
        for column in self.database.columns:
            serieses.append(self.database[column])
        return serieses
    
    def allColumnLabels(self):
        return self.database.columns
    
    def firstColumnLabel(self):
        return self.database.columns[0]
    
    def numColumns(self):
        return len(self.database.columns)
    
    def getColumn(self):
        return self.database[self.database.columns[0]]