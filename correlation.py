import sqlite3
from datetime import datetime

conn = sqlite3.connect('barometer.sqlite')
cur = conn.cursor()

cur.execute('''SELECT battle_date1, battle_date2 FROM Battles''')
dateslist = cur.fetchall()
#print(dateslist)

# TODO: Decide on data model (JOIN?) and construct SQL commands

for datepair in dateslist:
    dateend = datetime.strptime(datepair[1], '%Y-%m-%d').date()
    datestart = datetime.strptime(datepair[0], '%Y-%m-%d').date()
    delta = dateend - datestart
    if (datestart.year, datestart.month) == (dateend.year, dateend.month):
        print('case1 - only one month or day', datestart.year, dateend.year, datestart.month, dateend.month)
        # calculate the previous year-month
        # select the station_id for that battle and look up the reading for
        # the matching station_id + year + month and previous month
        # store in Correlation.pressurestart, Correlation.pressureend, Correlation.battles_id
        previous_month = datestart.month - 1
        #cur.execute('''SELECT station_id FROM Battles WHERE '''))



    elif dateend.year == 1111:
        print('case2 - single date', dateend.year)
    elif datestart.year < dateend.year:
        print('case3 - spans years', datestart.year, dateend.year)
    elif (datestart.year == dateend.year) and (dateend.month > datestart.month):
        print('case4 - spans months', datestart.year, dateend.year, datestart.month, dateend.month)
    else:
        print('unhandled use case', datestart.year, dateend.year, datestart.month, dateend.month)
        continue
    #print(datestart, dateend, delta)










cur.close()
