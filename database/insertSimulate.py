import sys, copy, datetime, csv
import math, random
import MySQLdb

compileOnly = False
dataRoot='./database/default'
employeeCount = 1000
projectCount = 200

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
                        employment = random.choice([row['Name']
                            for row in types if row['Name'] != 'Intern'
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

                timeSkip = random.randint(1, duration)
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
                row.append(p[2])
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

def randProjects(count, positions):
    names = f'{dataRoot}/ProjectNames.csv'
    departments = f'{dataRoot}/Departments.csv'
    status = f'{dataRoot}/ProjectStatus.csv'
    roles = f'{dataRoot}/ProjectRoles.csv'

    with open(names, 'r') as file:
        names = csv.DictReader(file)
        names = [row for row in names]
    with open(departments, 'r') as file:
        departments = csv.DictReader(file)
        departments = [row for row in departments]
    with open(status, 'r') as file:
        status = csv.DictReader(file)
        status = [row for row in status]
    with open(roles, 'r') as file:
        roles = csv.DictReader(file)
        roles = [row for row in roles]

    today = datetime.datetime.today()
    employedDates = [[row[0],
        datetime.datetime.strptime(row[1], '%Y-%m-%d'),
        datetime.datetime.strptime(row[2], '%Y-%m-%d') \
            if row[2] else today
    ] for row in positions]

    data = []
    for i in range(count):
        project = [i+1,
            random.choice(names)['Name'],
            random.choice(departments)['Name'],
        ] # See schema: Projects

        timeline = [] # FirstDay, LastDay
        timeline.append(random.randint(0, max(
            [row[0] for row in [[
                (today - row[1]).days,
                (today - row[2]).days
            ] for row in employedDates]]
        ))) # Random upto day of first employee.
        timeline.append(random.randint(0, timeline[0]))
        if random.randint(0, 99) > 90: timeline[1] = 0
        timeline = [ # Converts to actual date.
            today - datetime.timedelta(days=row)
        for row in timeline]

        project.append(random.choice([row['Name']
            for row in status if row['Name'] != 'Closed'
        ]) if timeline[1] == today else 'Closed')

        leaders = []
        t = timeline[0]
        while t < timeline[1]:
            candidates = [row for row in employedDates
                if row[1] <= t <= row[2]
            ] # Candidates for leaders.

            if leaders:
                extend = [row for row in candidates
                    if row[0] == leaders[-1][0]
                ] # Finds if leader can be continued.
                if extend and random.randint(0, 1):
                    leadEnd = min(timeline[1], extend[0][2])
                    t = leaders[-1][2] = leadEnd
                    t += datetime.timedelta(days=1)
                    continue

                candidates = [row for row in candidates
                    if row[0] != leaders[-1][0]
                ] # Excludes same records.

            if candidates:
                lead = random.choice(candidates)
                leadEnd = min(timeline[1], lead[2])
            else:
                lead = None
                futureDates = [row[1]
                    for row in employedDates if row[1] > t
                ] # Finds the earliest date with employee.
                if futureDates:
                    leadEnd = min(timeline[1],
                        min(futureDates) - datetime.timedelta(days=1)
                    ) # EndDate always precede by a day!
                else: leadEnd = timeline[1]
            lead = lead[0] if lead else None
            leaders.append([lead, t, leadEnd])
            t = leadEnd + datetime.timedelta(days=1)

        while not leaders[0][0]:
            leaders.pop(0)
            if not leaders: break
            timeline[0] = leaders[0][1]

        members = []
        t = timeline[0]
        while t < timeline[1]:
            maxMemberCount = random.randint(1, 10)
            currentMembers = [row[0] for row in members
                if row[1] <= t <= row[2]
            ] + [row[0] for row in leaders
                if row[1] <= t <= row[2]
            ]; memberCount = len(currentMembers)

            while memberCount < maxMemberCount:
                candidates = [row for row in employedDates
                    if row[1] <= t <= row[2] and
                       row[0] not in currentMembers
                ] # Candidates for members.

                if candidates:
                    member = random.choice(candidates)
                    memberEnd = min(timeline[1], member[2])
                    members.append([member[0], t, memberEnd,
                        random.choice(roles)['Name']
                    ]) # See schema: EmployeeRoles
                    currentMembers.append(member[0])
                    memberCount += 1
                else: break

            futureDates = [row[2] for row in members if row[2] > t]
            t = random.choice(futureDates) if futureDates else timeline[1]
            t += datetime.timedelta(days=1)

        data.append([project,
            [[row[0],
              row[1].strftime('%Y-%m-%d'),
              row[2].strftime('%Y-%m-%d')
            ] for row in leaders],
            [[row[0], i+1,
              row[1].strftime('%Y-%m-%d'),
              row[2].strftime('%Y-%m-%d'), row[3]
            ] for row in members]
        ])
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
    else: [print(row) for row in employees]

    print("Compiling EmployeePositions...")
    positions = randPositions(employees)
    print("Inserting EmployeePositions...")
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
            })', batch)
        if not compileOnly and endDates:
            cursor.executemany(f'CALL RetireFromPosition({
                ", ".join(["%s" for x in endDates[0]])
            })', endDates)
    if compileOnly: [
        print(row)
    for row in positions]
    else: db.commit()

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
            })', batch)
        if not compileOnly and endDates:
            cursor.executemany(f'CALL LeaveDepartment({
                ", ".join(["%s" for x in endDates[0]])
            })', endDates)
    if compileOnly: [
        print(row)
    for row in departments]
    else: db.commit()

    print("Compiling EmployeeBenefits...")
    benefits = randBenefits(activeEmployees)
    print("Inserting EmployeeBenefits...")
    if not compileOnly and benefits:
        cursor.executemany(f'INSERT INTO EmployeeBenefits VALUES({
            ", ".join(["%s" for x in benefits[0]])
        })', benefits); db.commit()
    if compileOnly: [
        print(row)
    for row in benefits]

    print("Compiling Projects and Teams...")
    projects = randProjects(projectCount, positions)
    print("Inserting Projects and Teams...")
    for p in projects:
        if not p[1]:
            continue

        if not compileOnly:
            cursor.execute('CALL CreateProject(%s, %s, %s, %s)',
                [p[0][1], p[0][2], p[1][0][0], p[1][0][1]])

        active = True
        for row in p[1][1:]:
            match ([compileOnly, active, row[0]]):
                case [False, True, None]:
                    cursor.execute('CALL CloseProject(%s, %s)',
                        [p[0][0], row[1]])
                    active = False
                case [False, False, _]:
                    cursor.execute('CALL ReviveProject(%s, %s, %s)',
                        [p[0][0], row[1], row[0]])
                    active = True
                case [False, True, _]:
                    cursor.execute('CALL ChangeProjectLeader(%s, %s, %s)',
                        [p[0][0], row[0], row[1]])

        if not compileOnly and p[0][3] != 'Closed':
            cursor.execute('''UPDATE Projects
                SET Status = %s WHERE ID = %s
            ''', [p[0][3], p[0][0]])

        today = datetime.datetime.today()
        processing = copy.deepcopy(p[2])
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
                eDate = row.pop(3)
                if p[0][3] == 'Closed' \
                   or eDate != today.strftime('%Y-%m-%d'):
                    endDates.append([row[0], row[1], eDate])

            if not compileOnly:
                cursor.executemany(f'INSERT INTO EmployeeRoles VALUES({
                    ", ".join(["%s" for x in batch[0]])
                })', batch)
            if not compileOnly and endDates:
                cursor.executemany(f'CALL RetireFromRole({
                    ", ".join(["%s" for x in endDates[0]])
                })', endDates)

        if compileOnly:
            print(p[0])
            [print(row) for row in p[1]]
            [print(row) for row in p[2]]
        else: db.commit()
