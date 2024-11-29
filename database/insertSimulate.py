import sys, copy, datetime, csv
import math, random
import MySQLdb

dataRoot='./database/default'
employeeCount = 1000

db = MySQLdb.connect(
    host='localhost',
    user='GenericApplication',
    db='GenericCompany'
); cursor = db.cursor()

def randEmployees(count):
    names = f'{dataRoot}/Names.csv'
    addresses = f'{dataRoot}/Addresses.csv'
    genders = f'{dataRoot}/Genders.csv'
    degrees = f'{dataRoot}/Degrees.csv'

    with open(names, 'r') as file:
        names = csv.DictReader(file)
        names = [row for row in names]
    with open(addresses, 'r') as file:
        addresses = csv.DictReader(file)
        addresses = [row for row in addresses]
    with open(genders, 'r') as file:
        genders = csv.DictReader(file)
        genders = [row for row in genders]
    with open(degrees, 'r') as file:
        degrees = csv.DictReader(file)
        degrees = [row for row in degrees]

    data = []
    for i in range(count):
        row = [i+1] # Resets!

        age = random.randint(18, 65)
        birthDate = [datetime.date.today() - n for n in [
            datetime.timedelta(days=365 * (age+1)),
            datetime.timedelta(days=365 * age)
        ]] # Establishes bounds on the birthDates.
        birthDate = birthDate[0] + datetime.timedelta(
            random.randint(0,(birthDate[1]-birthDate[0]).days)
        ) # Computes a random birthDate.

        while True:
            socialSecurity = str(random.randint(1,999)).zfill(3) \
                + '-' + str(random.randint(1,99)).zfill(2) \
                + '-' + str(random.randint(1,9999)).zfill(4)
            if socialSecurity not in [row[4] for row in data]: break

        phoneNumber = str(random.randint(100,999)) \
            + ' ' + str(random.randint(100,999)) \
            + '-' + str(random.randint(0,9999)).zfill(4)
        address = random.choice(addresses)

        data.append([i+1,
            random.choice(names)['FirstName'],
            random.choice(names)['LastName'],
            random.choice(genders)['Name'],
            birthDate.strftime('%Y-%m-%d'),
            socialSecurity, phoneNumber,
            address['StreetAddress'], address['City'],
            address['State'], address['ZIPCode'],
            random.choice(degrees)['Name'],
            random.randint(max(0, age-48), age-18)
        ]) # See schema: Employees
    return data

def randPositions(employees):
    positions = f'{dataRoot}/Positions.csv'
    types = f'{dataRoot}/EmploymentTypes.csv'
    health = f'{dataRoot}/HealthInsurance.csv'

    with open(positions, 'r') as file:
        positions = csv.DictReader(file)
        positions = [row for row in positions]
    with open(types, 'r') as file:
        types = csv.DictReader(file)
        types = [row for row in types]
    with open(health, 'r') as file:
        health = csv.DictReader(file)
        health = [row for row in health]

    data = []
    for e in employees:
        experience = datetime.datetime.today() \
            - datetime.datetime.strptime(e[4], '%Y-%m-%d') \
            - datetime.timedelta(days=18 * 365) # Legal working age.
        internal = experience.days // 365 - e[12]
        external = e[12]

        group = []
        s = [1, 2, 3, 4, 5, 6]
        while internal > 0:
            if internal - sum(s) >= 0 and random.randint(0, 99) > 5:
                group.append(copy.deepcopy(s)); internal -= sum(s)
            elif sum(s) > 1: s.pop()
        random.shuffle(group)

        if not group: group.append([1])

        d = datetime.datetime.today() - experience
        for i, unit in enumerate(group):
            years = 0
            if external > 0:
                years = random.randint(1, external)
                d += datetime.timedelta(days=years * 365)
                external -= years # Random external experience.

            for j in range(0, len(unit)):
                duration = datetime.timedelta(
                    days=unit[j] * 365 + random.randint(-90, 0)
                ) # Random duration for the position.

                if j > 0: # Promotion or internal transfer.
                    p = [row for row in positions
                        if row['Name'] == unit[j-1][3]
                    ][0] # Retrieves the position.
                    if random.randint(0, unit[j]-1) \
                       and unit[j-1][5] * 1.10 < int(p['MaximumSalary']):
                        title = p['Name']; employment = 'Full-Time'
                        salary = random.randint(
                            int(unit[j-1][5] * 1.10),
                            int(p['MaximumSalary'])
                        ) # Salary increases by at least 10%.
                    else: # Internal transfer.
                        p = random.choice(positions); title = p['Name']
                        employment = random.choice([row['Name'] for row in
                            filter(lambda r: r['Name'] != 'Intern', types)
                        ]) # Random employment type, excluding internship.
                        salary = random.randint(
                            int(p['MinimumSalary']),
                            int(p['MaximumSalary'])
                        ) # Random salary based on employment.
                else:
                    p = random.choice(positions); title = p['Name']
                    employment = random.choice(types)['Name']
                    salary = random.randint(
                        int(p['MinimumSalary']),
                        int(p['MaximumSalary'])
                    ) # Random salary based on employment.

                if employment == 'Full-Time':
                    insurance = random.choice(health)['Name']
                    insuranceStart = d + datetime.timedelta(
                        days=random.randint(-180, 0)
                    ) # Random valid health insurance start date.
                    insuranceStart = insuranceStart.strftime('%Y-%m-%d')
                    insuranceEnd = d + duration + datetime.timedelta(
                        days=random.randint(0, 180)
                    ) # Random valid health insurance end date.
                    insuranceEnd = insuranceEnd.strftime('%Y-%m-%d')
                else: insurance = insuranceStart = insuranceEnd = None

                unit[j] = [e[0], d.strftime('%Y-%m-%d'),
                    (d + duration).strftime('%Y-%m-%d'),
                    title, employment, salary,
                    0 if j > 0 else 1, insurance,
                    insuranceStart, insuranceEnd
                ] # See schema: EmployeePositionsHistory
                d += duration + datetime.timedelta(days=1)

                if i+1 == len(group) and j+1 == len(unit) \
                   and external == 0: unit[j][2] = None
                if i == 0 or years > 0: unit[j][6] = 1
                data.append(unit[j])
    return data

if __name__ == '__main__':
    if len(sys.argv) > 1:
        print('Usage: python insertSimulate.py')
        sys.exit(1) # Disables command-line arguments.

    employees = randEmployees(employeeCount)
    cursor.executemany(f'INSERT INTO Employees VALUES({
        ", ".join(["%s" for x in employees[0]])
    })', employees); db.commit()

    positions = randPositions(employees)
    processing = copy.deepcopy(positions)
    while processing:
        batch = []
        encountered = set()
        for row in processing:
            if row[0] not in encountered:
                encountered.add(row[0])
                batch.append(row)

        processing = [row for row in
            filter(lambda x: x not in batch, processing)
        ] # Removes current batch from processing list.

        endDates = []
        for i, row in enumerate(batch):
            if row[2] != None: endDates.append([row[0], row[2]])
            batch[i] = [row[j] for j in range(len(row)) if j != 2]

        cursor.executemany(f'INSERT INTO EmployeePositions VALUES({
            ", ".join(["%s" for x in batch[0]])
        })', batch); db.commit()
        if endDates:
            cursor.executemany(f'CALL RetireFromPosition({
                ", ".join(["%s" for x in endDates[0]])
            })', endDates); db.commit()
