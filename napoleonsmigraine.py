import sqlite3
import ssl
import urllib.request, urllib.parse, urllib.error
from bs4 import BeautifulSoup
import datetime as dt

def dmstodd(dms_string):
    '''
    Returns an integer converted from Degree Minutes Seconds (DMS) format to Decimal Degrees (DD).
    DD is the format used in geolocation calculations and haversine.py.
    Important: This formula is specific to the purpose used in this program only. It is not for
    more standard degree-minute-second calculations.

    :param dms_string: a string in DMS format  similar to "degrees(N/S/E/W)" - for example: 70N or 20W
    :return: int
    '''

    dd_string = dms_string.strip('N').strip('S').strip('E').strip('W')
    dd_string = int(dd_string)
    return dd_string

# Pull reconstructed barometric data for time period from CDIAC site
#
url = "https://cdiac.ess-dive.lbl.gov/ftp/ndp025/ndp025.eur"
print('Retrieving', url)

# open and read the data at the url, store as text file
# for further processing
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
    jan REAL, feb REAL, mar REAL, apr REAL, may REAL, jun REAL,
    jul REAL, aug REAL, sep REAL, oct_m REAL, nov REAL, dec REAL,
    station_id INTEGER)''')
#
cur.execute('''CREATE TABLE IF NOT EXISTS Battles
    (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE, battle_date1 TEXT,
    battle_date2 TEXT, battle_url TEXT, outcome TEXT,
    batlat REAL, batlong REAL, station_id INTEGER)''')

# Process barometric lat, long, and readings from CDAIC page and put into Station, Barometer tables
for line in linelist:
    r = 0
    # extract lat & long from GRID-POINT lines
    if line.find('GRID-POINT') != -1:
        barlat = line[38:42]
        barlong = line[43:47]
        # convert lat and long into DD format
        barlat = dmstodd(barlat)
        barlong = dmstodd(barlong)
        r = 0
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
        year = int(newbarlist[0])
        jan = newbarlist[1]
        feb = newbarlist[2]
        mar = newbarlist[3]
        apr = newbarlist[4]
        may = newbarlist[5]
        jun = newbarlist[6]
        jul = newbarlist[7]
        aug = newbarlist[8]
        sep = newbarlist[9]
        oct_m = newbarlist[10]
        nov = newbarlist[11]
        dec = newbarlist[12]

        # Insert items from readingslist into the DB
        cur.execute('''INSERT OR IGNORE INTO Barometer (year, jan, feb, mar,
                    apr, may, jun, jul, aug, sep, oct_m, nov, dec, station_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                    (year, jan, feb, mar, apr, may, jun, jul, aug, sep, oct_m, nov, dec, station_id))
        conn.commit()

# Pull Napoleonic battle data from Wikipedia
starturl = 'https://en.wikipedia.org/wiki/Military_career_of_Napoleon_Bonaparte'
html = urllib.request.urlopen(starturl, context=ctx).read().decode()
soup = BeautifulSoup(html, 'html.parser')

#table = soup.find("table", class_='wikitable sortable')
table = soup.find('table', {'class':'wikitable sortable'})

for tr in table.find_all('tr'):
    tds = tr.find_all('td')
    if not tds: continue
    # get battle date
    battle_date = tds[1].string

    # get battle name title
    try:
        battle_name = tds[2].find('a')['title']
        battle_url = 'https://en.wikipedia.org/wiki/' + battle_name
    except:
        battle_url = battle_name
    # get battle outcome
    outcome = tds[-1].string.strip()

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
                battle_url, outcome) VALUES (?, ?, ?, ?)''',
                (battle_date1, battle_date2, battle_url, outcome))
    conn.commit()

cur.execute('''SELECT battle_url FROM Battles''')
battle_names = [item[0] for item in cur.fetchall()]
print(battle_names)

for battle in battle_names:
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
        # To grab DMS (Degree Minute Second data) data - not needed
        # batlat = souploc.find(class_='latitude').get_text()
        # batlong = souploc.find(class_='longitude').get_text()
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