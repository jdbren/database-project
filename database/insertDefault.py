import sys, re, csv
import MySQLdb

databaseRoot='./database'

db = MySQLdb.connect(
    host='localhost',
    user='GenericAdministrator',
    db='GenericCompany'
); cursor = db.cursor()

def insertFromCSV(schema, dataFile):
    reader = csv.reader(dataFile)

    attributes = next(reader)
    values = ', '.join(['%s' for x in attributes])
    columns = ', '.join(attributes) # Converts to string.
    query = f'INSERT INTO {schema}({columns}) VALUES({values});'

    data = []
    for row in reader:
        if len(row) == len(attributes):
            data.append(tuple(row))
        else: print(f'Skipping: {row[0]}')

    cursor.executemany(query, data); db.commit()


if __name__ == '__main__':
    if len(sys.argv) > 1:
        print('Usage: python compileCSV.py')
        sys.exit(1) # Disables command-line arguments.

    pattern = re.compile(r'CREATE TABLE')
    with open(databaseRoot + '/schema.sql', 'r') as definitionFile:
        for line in definitionFile: # Scans each line for schema.
            if pattern.search(line): # Found schema definition.
                schemaName = line.split()[5]
                filePath = f'{databaseRoot}/default/{schemaName}.csv'
                try: # Inserts into database if file exists.
                    with open(filePath,'r') as dataFile:
                        print(f'Inserting from {schemaName}.csv.')
                        insertFromCSV(schemaName, dataFile)
                except FileNotFoundError:
                    continue # Skips.
