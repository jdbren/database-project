import sys, copy, datetime, csv
import math, random
import MySQLdb

dataRoot='./database/default'
employeeCount = 1000
compileOnly = False

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
        while internal > 0: # Random scheduling.
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


def randDepartments(positions):
    departments = f'{dataRoot}/Departments.csv'

    with open(departments, 'r') as file:
        departments = csv.DictReader(file)
        departments = [row for row in departments]

    data = []
    for p in positions:
        d = datetime.datetime.strptime(p[1], '%Y-%m-%d')
        duration = (
            datetime.datetime.today() - d if not p[2] else \
            datetime.datetime.strptime(p[2], '%Y-%m-%d') - d
        ).days // 7

        active = []; dataForP = []
        choices = [row['Name'] for row in departments]
        while True:
            if active and random.randint(0, 99) < len(active) * 25:
                team = random.choice(active)

                # See schema: EmployeeDepartments
                dataForP[team[0]].append(d.strftime('%Y-%m-%d'))
                choices.append(team[1])
                active.remove(team)

                timeSkip = random.randint(0, duration)
                d += datetime.timedelta(weeks=timeSkip)
                duration -= timeSkip
            else:
                team = random.choice(choices)

                choices.remove(team)
                active.append([len(dataForP), team])
                dataForP.append([p[0], team, d.strftime('%Y-%m-%d')])
                # See schema: EmployeeDepartments

                timeSkip = 27 if duration < 27 else \
                    random.randint(27, duration)
                d += datetime.timedelta(weeks=timeSkip)
                duration -= timeSkip

            if duration < 27: break

        for row in dataForP:
            if len(row) < 4:
                row.append(None if not p[2] else \
                    datetime.datetime.strptime(p[2],'%Y-%m-%d')
                ) # Or remove departments, randomly?
        data.extend(dataForP)
    return data

def randBenefits(activeEmployees):
    benefits = f'{dataRoot}/Benefits.csv'

    with open(benefits, 'r') as file:
        benefits = csv.DictReader(file)
        benefits = [row for row in benefits]

    data = []
    for e in activeEmployees:
        choices = [row['Name'] for row in benefits]
        while random.randint(0, 1) and choices:
            b = random.choice(choices)
            choices.remove(b)

            benefitStart = max(
                datetime.datetime.strptime(e[1],'%Y-%m-%d'),
                datetime.datetime.today()
                - datetime.timedelta(weeks=random.randint(0, 13))
            ) # Within six months or position StartDate.
            if 'Insurance' in b:
                benefitEnd = (benefitStart
                    + datetime.timedelta(weeks=52)
                ).strftime('%Y-%m-%d')
            else: benefitEnd = None

            benefitStart = benefitStart.strftime('%Y-%m-%d')
            data.append([e[0], b, benefitStart, benefitEnd])
            # See schema: EmployeeBenefits
    return data

if __name__ == '__main__':
    if len(sys.argv) > 1:
        print('Usage: python insertSimulate.py')
        sys.exit(1) # Disables command-line arguments.

    activeEmployees = []

    print("Compiling Employees...")
    employees = randEmployees(employeeCount)
    print("Inserting Employees...")
    if not compileOnly:
        cursor.executemany(f'INSERT INTO Employees VALUES({
            ", ".join(["%s" for x in employees[0]])
        })', employees); db.commit()

    print("Compiling EmployeePositionsHistory...")
    positions = randPositions(employees)
    print("Inserting EmployeePositionsHistory...")
    processing = copy.deepcopy(positions)
    while processing:
        batch = []
        encountered = set()
        for row in processing:
            if row[0] not in encountered:
                encountered.add(row[0])
                batch.append(row)

        endDates = []
        for row in batch:
            processing.remove(row)
            eDate = row.pop(2)
            if eDate: endDates.append([row[0], eDate])
            else: activeEmployees.append([row[0], row[1]])

        if not compileOnly:
            cursor.executemany(f'INSERT INTO EmployeePositions VALUES({
                ", ".join(["%s" for x in batch[0]])
            })', batch); db.commit()
        if not compileOnly and endDates:
            cursor.executemany(f'CALL RetireFromPosition({
                ", ".join(["%s" for x in endDates[0]])
            })', endDates); db.commit()

    print("Compiling EmployeeDepartments...")
    departments = randDepartments(positions)
    print("Inserting EmployeeDepartments...")
    processing = copy.deepcopy(departments)
    while processing:
        batch = []
        encountered = set()
        for row in processing:
            if tuple([row[0], row[1]]) not in encountered:
                encountered.add(tuple([row[0], row[1]]))
                batch.append(row)

        endDates = []
        for row in batch:
            processing.remove(row)
            eDate = row.pop(3)
            if eDate: endDates.append([row[0], row[1], eDate])

        if not compileOnly:
            cursor.executemany(f'INSERT INTO EmployeeDepartments VALUES({
                ", ".join(["%s" for x in batch[0]])
            })', batch); db.commit()
        if not compileOnly and endDates:
            cursor.executemany(f'CALL LeaveDepartment({
                ", ".join(["%s" for x in endDates[0]])
            })', endDates); db.commit()

    print("Compiling EmployeeBenefits...")
    benefits = randBenefits(activeEmployees)
    print("Inserting EmployeeBenefits...")
    if not compileOnly and benefits:
        cursor.executemany(f'INSERT INTO EmployeeBenefits VALUES({
            ", ".join(["%s" for x in benefits[0]])
        })', benefits); db.commit()
