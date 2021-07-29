from math import radians, cos, sin, asin, sqrt
import sqlite3

def haversine(lat1, long1, lat2, long2):
    """
    Returns the great-circle distance in km between
    two points on a sphere, given their latitudes and
    longitudes.

    For consistency, use this practice:
    lat1, long1 is the battle latitude and longitude.
    lat2, long2 is the barometric station lat and long.

    """
    # get rid of Null results
    try:
        # Convert decimal degrees to radians
        lat1, long1, lat2, long2 = map(radians, [lat1, long1, lat2,
                                                 long2])

        # haversine formula
        dlon = long2 - long1
        dlat = lat2 - lat1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * asin(sqrt(a))

        # Radius of earth in kilometers is 6371
        km = 6371 * c
        return km
    except:
        return False  # handle Nulls in lat/long lists

conn = sqlite3.connect('barometer.sqlite')
cur = conn.cursor()

cur.execute('SELECT batlat, batlong FROM Battles')
battle_loc = cur.fetchall()
print(battle_loc, 'length:', len(battle_loc))

cur.execute('SELECT barlat, barlong, id FROM Station')
barometer_loc = cur.fetchall()
print(barometer_loc, 'length:', len(barometer_loc))

barlocs = list()
for battle in battle_loc:
    batlat = battle[0]
    batlong = battle[1]
    lowest_so_far = None
    # bar_id is used to track the barometric station id from the Station table
    bar_id = -1
    # for each battle, determine how far each barometric station is, find the smallest distance,
    # and capture that and the barometric station id in a list
    for loc in barometer_loc:
        barlat = loc[0]
        barlong = loc[1]
        id = loc[2]
        # handle Nulls in list
        if not haversine(batlat, batlong, barlat, barlong):
            distance = None  # TODO: Is setting this to none gonna cause issues when looking for lowest distance
            continue
        else:
            distance = haversine(batlat, batlong, barlat, barlong)
            if lowest_so_far is None:
                lowest_so_far = distance
                bar_id = id
            elif distance < lowest_so_far:
                lowest_so_far = distance
                bar_id = id
            else:
                continue
    barlocs.append((lowest_so_far, bar_id))

print('Kilometers:', barlocs, len(barlocs))
