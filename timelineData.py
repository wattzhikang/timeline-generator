import re
import pandas

class Data:
    def __init__(self, filename):
        self.__file = open(filename, "r")

        if self.hasHeader():
            self.__database = pandas.read_csv(self.__file)
        else:
            self.__database = pandas.read_csv(self.__file, names=["Name","Birth","Death"])

    __headerRegex = re.compile(r"\-?[0-9]+\.?[0-9]*.\-?[0-9]+\.?[0-9]*")

    def hasHeader(self):
        self.__file.seek(0,0)
        headerPresent = self.__headerRegex.search(self.__file.readline()) == None
        self.__file.seek(0,0)
        return headerPresent
    
    def __repr__(self):
        return repr(self.__database)