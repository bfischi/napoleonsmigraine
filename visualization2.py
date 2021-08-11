import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sqlite3 as sql

conn = sql.connect('barometer.sqlite')

df = pd.read_sql_query('''SELECT * FROM v_migraine_data''', conn)
conn.close()
print(df.head())


y1 = df['pressurestart'].to_numpy(dtype=float)
y2 = df['pressureend'].to_numpy(dtype=float)
delta = y2-y1
delta_list = delta.tolist()
outcome = df['outcome'].tolist()
battledates = (df['battle_date']).tolist()

# Create a color if the y axis value is equal or greater than 0
my_color = np.where(delta >= 0, 'orange', 'skyblue')

# The vertical plot is made using the vline function
plt.vlines(x=battledates, ymin=0, ymax=delta, color=my_color, alpha=0.8)
plt.scatter(battledates, delta, color=my_color, s=1, alpha=1, label="Blue = lower ending pressure, Orange = higher")


# Add title and axis names
plt.title("Starting and ending barometric pressure for each Napoleonic battle", loc='left')
plt.xlabel('Start date of Napoleonic battle (yyyy-mm-dd)')
plt.ylabel('Barometric pressure delta (in mbar) at start of battle vs end of battle')
plt.xticks(rotation=65)
plt.legend()

# get series list of the string labels for each "defeat" outcome
string_label = df[df['outcome'] == -1]['battle_date'].values

for i in range(5):
    # find out which x-axis tick corresponds to the label
    label_index = battledates.index(string_label[i])
    # find out which y-axis number corresponds to the label
    y_index = delta_list[label_index]
    plt.annotate('defeat', xy=(label_index, y_index))

# Show the graph
plt.show()
