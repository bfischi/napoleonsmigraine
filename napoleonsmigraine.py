import sqlite3
import ssl
import urllib.request, urllib.parse, urllib.error
from bs4 import BeautifulSoup
import datetime as dt


def dmstodd(dms_string):
    '''
    Returns an integer converted from Degree Minutes Seconds (DMS) format to Decimal Degrees (DD).
    DD is the format used in geolocation calculations and haversine.py.
    Important: This simple formula is specific to the purpose used in this program only. It is not for
    more standard degree-minute-second calculations and doesn't handle Minute and Second
    conversions.

    :param dms_string: a string in DMS format  similar to "degrees(N/S/E/W)" - for example: 70N or 20W
    :return: int
    '''

    if 'S' in dms_string or 'W' in dms_string:
        dd_string = '-' + dms_string.strip().removesuffix('S').removesuffix('W')
    else:
        dd_string = dms_string.strip().strip('N').strip('E')
    dd_string = int(dd_string)
    return dd_string


# Pull reconstructed barometric data for time period from CDIAC site
url = "https://cdiac.ess-dive.lbl.gov/ftp/ndp025/ndp025.eur"
print('Retrieving', url)

# open and read the data at the url, store as text file for further processing
page = urllib.request.urlopen(url)
file = open('barometer.txt', 'w')
content = str(page.read())
content = content.strip('\n')
content = content.lstrip('b\'').rstrip('\'')
file.write(content)
file.close()

# process the barometric data text file if url not being used
barreadings = open('barometer.txt', 'r')
readings = barreadings.readlines()

linelist = list()
for lines in readings:
    linelist = lines.split('\\n')

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

conn = sqlite3.connect('barometer.sqlite')
cur = conn.cursor()

cur.execute('''DROP TABLE IF EXISTS Station ''')
cur.execute('''DROP TABLE IF EXISTS Barometer ''')
cur.execute('''DROP TABLE IF EXISTS Battles ''')

# Create fresh tables in barometer.sqlite
cur.execute('''CREATE TABLE IF NOT EXISTS Station
    (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE, barlat INTEGER, barlong INTEGER)''')

cur.execute('''CREATE TABLE IF NOT EXISTS Barometer
    (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE, year INTEGER,
    month INTEGER, reading REAL,
    station_id INTEGER, CONSTRAINT fk_station FOREIGN KEY (station_id) REFERENCES Station (id))''')

# TODO: Battles.station_id might be a confusing name. It is actually the id
# TODO: of the closest barometric station to the Battle, not the Station.id itself.
# TODO: But how to change?

cur.execute('''CREATE TABLE IF NOT EXISTS Battles
    (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE, battle_date1 TEXT,
    battle_date2 TEXT, battle_url TEXT, battlename TEXT, outcome INTEGER,
    batlat REAL, batlong REAL, station_id INTEGER)''')

cur.execute('''CREATE TABLE IF NOT EXISTS Correlation
    (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    pressurestart REAL, pressureend REAL, battles_id INTEGER)''')

# Process barometric lat, long, and readings from CDAIC page and put into Station, Barometer tables
for line in linelist:
    # extract lat & long from GRID-POINT lines
    if line.find('GRID-POINT') != -1:
        barlat = line[38:42]
        barlong = line[43:47]
        # convert lat and long into DD format
        barlat = dmstodd(barlat)
        barlong = dmstodd(barlong)
        print('Barlat, barlong:', barlat, barlong)
        # commit lat and long to db as integers
        cur.execute('''INSERT OR IGNORE INTO Station (barlat, barlong) VALUES (?, ?)''', (barlat, barlong))
        cur.execute('SELECT id FROM Station WHERE (barlat, barlong) = (?, ?) ', (barlat, barlong))
        station_id = cur.fetchone()[0]

    # process line and remove unneeded mean value for year (last item in list)
    else:
        pieces = line.strip(' ')
        pieces = pieces.split(' ')
        pieces.pop(-1)
        pieces = filter(None, pieces)

        newbarlist = list()
        for piece in pieces:
            if piece.find('/'):
                head, sep, tail = piece.partition('/')
                newbarlist.append(float(head))
        print('Newbarlist:', newbarlist)
        if newbarlist == []: break

        # Assign list items to vars to prepare for insertion into db
        for i in range(0, len(newbarlist)):
            year = int(newbarlist[0])
            if year > 1815:
                continue
            else:
                month = int(i)
                reading = newbarlist[i]

                # Insert items from readingslist into the DB
                cur.execute('''INSERT OR IGNORE INTO Barometer (year, month, reading, station_id)
                            VALUES (?, ?, ?, ?)''',
                            (year, month, reading, station_id))
                conn.commit()

# Pull Napoleonic battle data from Wikipedia
starturl = 'https://en.wikipedia.org/wiki/Military_career_of_Napoleon_Bonaparte'
html = urllib.request.urlopen(starturl, context=ctx).read().decode()
soup = BeautifulSoup(html, 'html.parser')

table = soup.find('table', {'class':'wikitable sortable'})

for tr in table.find_all('tr'):
    tds = tr.find_all('td')
    if not tds: continue
    # get battle date
    battle_date = tds[1].string

    # get battle name title
    try:
        battlename = tds[2].find('a')['title']
        battle_url = 'https://en.wikipedia.org/wiki/' + battlename
    except:
        battle_url = battlename
    # get battle outcome
    outcome = tds[-1].string.strip()
    if outcome == 'Victory':
        outcome = 1
    elif outcome == 'Defeat':
        outcome = -1
    else:
        outcome = 0

    # clean up dates
    end_year = int(battle_date[-4:])
    str_end_mon = battle_date[-8:-5]
    end_mon = int(dt.datetime.strptime(str_end_mon, '%b').month)

    # grab anything in the str before the last mon and year, then process it
    battle_split = battle_date[:-8].split()

    for item in battle_split:
        # Handle battle dates formatted like dd-dd Mon yyyy or dd Mon yyyy
        # Note: (1111, 1, 1) indicates that the date() for this entry is irrelevant
        if len(battle_split) == 1:
            # Where battle_split looks like ['30'] as in 30 April, e.g.
            try:
                day = battle_split[0].split('-')
                if len(day) == 1:
                    start_day = int(day[0])
                    end_day = None
                    battle_date1 = dt.date(end_year, end_mon, start_day)
                    battle_date2 = dt.date(1111, 1, 1)

                # Where battle_split looks like ['3-4'] as in 3-4 April, e.g.
                else:
                    start_day = int(day[0])
                    end_day = int(day[1])
                    battle_date1 = dt.date(end_year, end_mon, start_day)
                    battle_date2 = dt.date(end_year, end_mon, end_day)
                start_mon = None
                start_year = None

            # where the battle date is a one-day battle (e.g., 30 Aug 1799)
            except:
                start_day = int(battle_split[0])
                start_mon = None
                start_year = None
                battle_date1 = dt.date(end_year, end_mon, start_day)
                battle_date2 = dt.date(1111, 1, 1)

        # Handle battle dates formatted like dd Mon-dd-Mon yyyy (e.g., 29 Aug-19 Dec 1793)
        # After doing battle_split, these look like ['24', 'Aug-19'] where 19 is the end_day
        elif len(battle_split) == 2:

            try:
                start_day = int(battle_split[0])
                # split up the Mon-dd (e.g., 'Aug-19')
                splitmore = battle_split[1].split('-')
                str_start_mon = splitmore[0]
                start_mon = int(dt.datetime.strptime(str_start_mon, '%b').month)
                end_day = int(splitmore[1])
                start_year = None
                battle_date1 = dt.date(end_year, start_mon, start_day)
                battle_date2 = dt.date(end_year, end_mon, end_day)

            except:
                print('exception')
                continue

        # Handle battle dates formatted like dd Mon yyyy dd-Mon yyyy (e.g., 24 Aug 1819-19 Dec 1820)
        # After doing battle_split, these look like ['24', 'Aug', '1819-19'] where 19 is the end_day
        else:
            start_day = int(battle_split[0])
            str_start_mon = battle_split[1]
            start_mon = int(dt.datetime.strptime(str_start_mon, '%b').month)
            splitmore = battle_split[2].split('-')
            start_year = int(splitmore[0])
            end_day = int(splitmore[1])
            battle_date1 = dt.date(start_year, start_mon, start_day)
            battle_date2 = dt.date(end_year, end_mon, end_day)

    # Insert data into DB
    cur.execute('''INSERT OR IGNORE INTO Battles (battle_date1, battle_date2,
                battle_url, battlename, outcome) VALUES (?, ?, ?, ?, ?)''',
                (battle_date1, battle_date2, battle_url, battlename, outcome))
    conn.commit()

cur.execute('''SELECT battle_url FROM Battles''')
battlenames = [item[0] for item in cur.fetchall()]
print(battlenames)

for battle in battlenames:
    try:
        battle_url = battle
        battle = urllib.parse.quote(battle, safe=':/')
        html_batloc = urllib.request.urlopen(battle, context=ctx).read()
        souploc = BeautifulSoup(html_batloc, 'html.parser')
        # Grab Decimal Degree (DD) location from wikipedia page, used in haversine.py
        dm_geo = souploc.find(class_='geo').get_text()
        dm_geo = dm_geo.split(";")
        batlat = dm_geo[0].strip()
        batlong = dm_geo[1].strip()

        print('Battle name, latitude, longitude: ', battle, batlat, batlong)

        # Insert data into DB
        cur.execute('''UPDATE Battles SET (batlat, batlong) = (?, ?)
                       WHERE (battle_url) = (?)''', (batlat, batlong, battle_url))
        conn.commit()
    except:
        print("Page or lat/long not found.")
        batlat = None
        batlong = None
        # Insert data into DB
        cur.execute('''UPDATE Battles SET (batlat, batlong) = (?, ?)
                       WHERE (battle_url) = (?)''', (batlat, batlong, battle_url))
        conn.commit()
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
