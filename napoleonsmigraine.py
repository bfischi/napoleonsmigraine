import sqlite3
import ssl
from operator import itemgetter
import urllib.request, urllib.parse, urllib.error

url = "https://cdiac.ess-dive.lbl.gov/ftp/ndp025/ndp025.eur"
print('Retrieving', url)

# open and read the data at the url, store as text file
# for further processing
# page = urllib.request.urlopen(url)
# file = open('barometer.txt', 'w')
# content = str(page.read())
# content = content.strip('\n')
# content = content.lstrip('b\'').rstrip('\'')
# file.write(content)
# file.close()

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

cur.execute('''DROP TABLE IF EXISTS Stations ''')
cur.execute('''DROP TABLE IF EXISTS Barometer ''')
cur.execute('''DROP TABLE IF EXISTS Battles ''')

# reading the reconstructed barometric data from CDAIC for that year, lat, long
cur.execute('''CREATE TABLE IF NOT EXISTS Stations
    (id INTEGER PRIMARY KEY, barlat TEXT, barlong TEXT,
     year INTEGER, month INTEGER, reading INTEGER)''')

cur.execute('''CREATE TABLE IF NOT EXISTS Barometer
    (id INTEGER PRIMARY KEY, year INTEGER, 
    jan_read REAL, feb_read REAL, mar_read REAL, 
    apr_read REAL, may_read REAL, jun_read REAL, 
    jul_read REAL, aug_read REAL, sep_read REAL, 
    oct_read REAL, nov_read REAL, dec_read REAL,
    stations_id INTEGER)''')

cur.execute('''CREATE TABLE IF NOT EXISTS Battles 
    (id INTEGER PRIMARY KEY, start_year INTEGER, 
    start_month INTEGER, start_day INTEGER, end_year INTEGER, 
    end_month INTEGER, end_day INTEGER, battle_name TEXT, 
    outcome INTEGER, batlat TEXT, batlong TEXT, stations_id INTEGER)''')

# process strings and put into db
for line in linelist:
    r = 0
    # extract lat & long from GRID-POINT lines
    if line.find('GRID-POINT') != -1:
        barlat = line[38:42]
        barlong = line[43:47]
        r = 0
        print('Barlat, barlong:', barlat, barlong)
        # commit lat and long to db
        cur.execute('''INSERT OR IGNORE INTO Stations (barlat, barlong) VALUES (?, ?)''', (barlat, barlong))

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
        jan_read = newbarlist[1]
        feb_read = newbarlist[2]
        mar_read = newbarlist[3]
        apr_read = newbarlist[4]
        may_read = newbarlist[5]
        jun_read = newbarlist[6]
        jul_read = newbarlist[7]
        aug_read = newbarlist[8]
        sep_read = newbarlist[9]
        oct_read = newbarlist[10]
        nov_read = newbarlist[11]
        dec_read = newbarlist[12]

        # Insert items from readingslist into the DB
        cur.execute('''INSERT OR IGNORE INTO Barometer (year, jan_read, feb_read, mar_read,
                    apr_read, may_read, jun_read, jul_read, aug_read, sep_read, oct_read,
                    nov_read, dec_read)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (year, jan_read, feb_read, mar_read,
                    apr_read, may_read, jun_read, jul_read, aug_read, sep_read, oct_read,
                    nov_read, dec_read))
        conn.commit()

cur.close()
