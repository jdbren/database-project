from pathlib import Path
import os, sys, csv

def generateFromCSV(dataName, scriptFile):
    with open(dataName, 'r') as dataFile:
        reader = csv.reader(dataFile)
        table = str(dataName.name).removesuffix('.csv')
        attributes = ', '.join(next(reader))

        scriptFile.write(f"-- Inserting from {table}.csv\n")
        scriptFile.write(f"INSERT IGNORE INTO {table}({attributes}) VALUES")

        row = next(reader)
        row = ', '.join(['"' + entry + '"' for entry in row])
        scriptFile.write(f"\n  ({row})")
        for row in reader:
            row = ', '.join(['"' + entry + '"' for entry in row])
            scriptFile.write(f",\n  ({row})")
        scriptFile.write(";\n")

def generateFromDataDirectory(directory):
    path = Path(directory + '/data')
    with open(directory + '/insertData.sql', 'w') as scriptFile:
        for dataName in path.glob("*.csv"):
            generateFromCSV(dataName, scriptFile)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print("Usage: python ./database/fromCSV.py")
        """ Aborts on command-line arguments. """
        sys.exit(1)
    if not (Path.cwd() / '.git').is_dir():
        print("Error: Executing outside of root.")
        """ Aborts if running in a subdirectory. """
        sys.exit(1)

    generateFromDataDirectory("./database")
