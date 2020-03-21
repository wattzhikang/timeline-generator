import re
import pandas

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
    def __init__(self, filename, database):
        if filename == None:
            self.database = database
        else:
            self.database = self.createDatabase(filename)
    
    def createDatabase(self, filename):
        file = open(filename, "r")
        if self.hasHeader(file):
                database = pandas.read_csv(file, header=0, names=["name", "birth", "death"])
        else:
            database = pandas.read_csv(file, header=None, names=["name","birth","death"])
        file.close()
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
    def __init__(self):
        Data.__init__(self, None, database=pandas.DataFrame({"name": [], "birth": [], "death": []}))
    
    def addData(self, filename):
        newDatabase = self.createDatabase(filename)
        self.database = pandas.concat([self.database, newDatabase], ignore_index=True)

    def sortByBirthDate(self):
        self.database = self.database.sort_values(by="birth")
    
    def minBirthDate(self):
        return self.database["birth"].min()
    
    def maxDeathDate(self):
        return self.database["death"].max()
    
    def people(self):
        for row in self.database.itertuples():
            yield Person(row.name, row.birth, row.death)
