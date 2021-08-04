import sqlite3
from datetime import datetime


conn = sqlite3.connect('barometer.sqlite')
cur = conn.cursor()

cur.execute('DELETE FROM Barometer WHERE month = 0')
conn.commit()

cur.execute('''SELECT battle_date1, battle_date2 FROM Battles''')
dateslist = cur.fetchall()

for datepair in dateslist:
    datestart = datetime.strptime(datepair[0], '%Y-%m-%d').date()
    dateend = datetime.strptime(datepair[1], '%Y-%m-%d').date()

    # update Correlation.readings for cases 1 and 2, where the battle lasted a few days or less within the same month
    if (dateend.year == 1111) or ((datestart.year, datestart.month) == (dateend.year, dateend.month)):
        print('case1 - only one month or day', datestart.year, dateend.year, datestart.month, dateend.month)
        # calculate the previous year-month
        # select the station_id for that battle and look up the reading for
        # the matching station_id + year + month and previous month
        # store in Correlation.pressurestart, Correlation.pressureend, Correlation.battles_id
        previousmonth = datestart.month - 1
        if previousmonth < 1:
            previousmonth = 12

        #cur.execute(('''SELECT id FROM Battles'''))
        cur.execute('''SELECT station_id FROM Battles WHERE battle_date1 = (?)''', (datepair[0],))
        battle_station_id = cur.fetchone()[0]
        print('battlestationid:', battle_station_id)
        endmonth = int(datestart.month)
        print(endmonth)

        # get barometric reading for the month before the battle started
        cur.execute('''SELECT reading FROM Barometer WHERE (station_id, year, month) = 
                       (?, ?, ?)''', (battle_station_id, datestart.year, previousmonth))
        barometerreadstart = cur.fetchone()[0]
        print('barometerreadingstart:', barometerreadstart)

        # get barometric reading for the month the battle ended
        cur.execute('''SELECT reading FROM Barometer WHERE (station_id, year, month) = 
                       (?, ?, ?)''', (battle_station_id, datestart.year, endmonth))
        barometerreadend = cur.fetchone()[0]
        print('barometerreadingend:', barometerreadend)

        cur.execute('''INSERT OR IGNORE INTO Correlation (pressurestart, pressureend) VALUES (?, ?) ''',
                    (barometerreadstart, barometerreadend))
        conn.commit()

    # update Correlation.readings for case 3, where the battle spanned from one year to another,
    # or for case 4, where the battle spanned months within the same year.
    elif (datestart.year < dateend.year) or ((datestart.year == dateend.year) and (dateend.month > datestart.month)):
        print('case3 - spans years', datestart.year, dateend.year)
        previousmonth = datestart.month - 1
        if previousmonth < 1:
            previousmonth = 12

        cur.execute('''SELECT station_id FROM Battles WHERE (battle_date1, battle_date2) = (?, ?)''',
                    (datepair[0], datepair[1]))
        battle_station_id = cur.fetchone()[0]
        endmonth = int(dateend.month)

        # get barometric reading for the month before the battle started
        cur.execute('''SELECT reading FROM Barometer WHERE (station_id, year, month) = 
                       (?, ?, ?)''', (battle_station_id, datestart.year, previousmonth))
        barometerreadstart = cur.fetchone()[0]
        print('barometerreadstart:', barometerreadstart)

        # get barometric reading for the month the battle ended
        cur.execute('''SELECT reading FROM Barometer WHERE (station_id, year, month) = 
                       (?, ?, ?)''', (battle_station_id, dateend.year, endmonth))
        barometerreadend = cur.fetchone()[0]
        print('barometerreadend:', barometerreadend)

        cur.execute('''INSERT OR IGNORE INTO Correlation (pressurestart, pressureend) 
                    VALUES (?, ?) ''',
                    (barometerreadstart, barometerreadend))
        conn.commit()

    else:
        print('unhandled use case', datestart.year, dateend.year, datestart.month, dateend.month)
        continue


cur.close()
# TODO: JOIN Battles.id and Correlation.pressurestart and Correlation.pressureend