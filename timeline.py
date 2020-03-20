import argparse

parser = argparse.ArgumentParser(
    description="A simple python tool for creating time-based charts based on multiple types of data"
)
parser.add_argument(
    "-b",
    "--biographical-data",
    nargs="+",
    help="One or more files containing biographical data",
    dest="bioFiles",
    metavar="filename.csv"
)
parser.add_argument(
    "-d",
    "--numerical-data",
    nargs="+",
    help="One or more files containing numerical data",
    dest="numFiles",
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

bioFiles = parser.parse_args().bioFiles
numFiles = parser.parse_args().numFiles
eventFiles = parser.parse_args().eventFiles

if bioFiles == None and numFiles == None and eventFiles == None:
    print("You must specify at least one file")
    exit(0)

if bioFiles != None:
    for fileName in bioFiles:
        file = open(fileName, "r")
        print(file)
        print(file.read())
        file.close()

if numFiles != None:
    for fileName in numFiles:
        file = open(fileName, "r")
        print(file)
        print(file.read())
        file.close()

if eventFiles != None:
    for fileName in eventFiles:
        file = open(fileName, "r")
        print(file)
        print(file.read())
        file.close()

# for bioSequence in BiographicalData.sequences():
#     for segment, color in zip(bioSequence.segments(), RandomColors.colors()):
#         #add segment with the random color