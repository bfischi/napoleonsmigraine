import sqlite3
from datetime import datetime

conn = sqlite3.connect('barometer.sqlite')
cur = conn.cursor()

cur.execute('DELETE FROM Barometer WHERE month = 0')
conn.commit()

cur.execute('''DROP TABLE IF EXISTS Correlation ''')

cur.execute('''CREATE TABLE IF NOT EXISTS Correlation
    (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    pressurestart REAL, pressureend REAL, battles_id INTEGER)''')

cur.execute('''SELECT battle_date1, battle_date2, id FROM Battles''')
dateslist = cur.fetchall()

for datetriplet in dateslist:
    datestart = datetime.strptime(datetriplet[0], '%Y-%m-%d').date()
    dateend = datetime.strptime(datetriplet[1], '%Y-%m-%d').date()
    battle_id = datetriplet[2]  # id of individual battle
    print(datetriplet)

    # update Correlation.readings for cases 1 and 2, where the battle lasted a few days or less within the same month
    if (dateend.year == 1111) or ((datestart.year, datestart.month) == (dateend.year, dateend.month)):
        print('case1 - only one month or day', datestart.year, dateend.year, datestart.month, dateend.month)
        previousmonth = datestart.month - 1
        if previousmonth < 1:
            previousmonth = 12

        # cur.execute(('''SELECT id FROM Battles'''))
        cur.execute('''SELECT station_id FROM Battles WHERE battle_date1 = (?)''', (datetriplet[0],))
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

        cur.execute('''INSERT OR IGNORE INTO Correlation (pressurestart, pressureend, battles_id) VALUES (?, ?, ?) ''',
                    (barometerreadstart, barometerreadend, battle_id))
        conn.commit()

    # update Correlation.readings for case 3, where the battle spanned from one year to another,
    # or for case 4, where the battle spanned months within the same year.
    elif (datestart.year < dateend.year) or ((datestart.year == dateend.year) and (dateend.month > datestart.month)):
        print('case3 - spans years', datestart.year, dateend.year)
        previousmonth = datestart.month - 1
        if previousmonth < 1:
            previousmonth = 12

        cur.execute('''SELECT station_id FROM Battles WHERE (battle_date1, battle_date2) = (?, ?)''',
                    (datetriplet[0], datetriplet[1]))
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

        cur.execute('''INSERT OR IGNORE INTO Correlation (pressurestart, pressureend, battles_id) 
                    VALUES (?, ?, ?) ''',
                    (barometerreadstart, barometerreadend, battle_id))
        conn.commit()

    else:
        print('unhandled use case', datestart.year, dateend.year, datestart.month, dateend.month)
        continue

cur.close()

# NapoleonsMigraine draws on reconstructed barometric pressure data and historical records
# of Napoleon Bonaparte's battles to see if there is any correlation between pressure
# changes and his battle outcomes. It is just a fun project with no scientific validity.
#
# Copyright (C) 2021 Beth Fischi
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# Contact information: Beth Fischi at https://www.linkedin.com/in/bethfischi/.
