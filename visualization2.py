# Inspired by https://www.python-graph-gallery.com/185-lollipop-plot-with-conditional-color

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
import sqlite3 as sql


plt.style.use('seaborn-darkgrid')

# Get the data from the database that we're going to display
conn = sql.connect('barometer.sqlite')
df = pd.read_sql_query('''SELECT * FROM v_migraine_data''', conn)
conn.close()
print(df.head())

# Convert the Pandas dataframe into useful formats for further calculation
y1 = df['pressurestart'].to_numpy(dtype=float)
y2 = df['pressureend'].to_numpy(dtype=float)
delta = y2-y1  # calculate the delta between ending and starting barometric pressures
delta_list = delta.tolist()
battledates = (df['battle_date']).tolist()

# Create a color if the y axis value is equal or greater than 0
my_color = np.where(delta >= 0, 'indianred', 'midnightblue')

# Make vertical plotlines and scatter plot with x-axis as battle dates and y-axis as delta pressures
plt.vlines(x=battledates, ymin=0, ymax=delta, color=my_color, alpha=1)
plt.scatter(battledates, delta, color=my_color, s=7, alpha=1)

# Add title, axis names, and legend
plt.title("Starting and ending barometric pressure for each Napoleonic battle", loc='left')
plt.xlabel('Start date of Napoleonic battle (yyyy-mm-dd)')
plt.ylabel('Barometric pressure delta (in mbar) at start of battle vs end of battle')
plt.xticks(rotation=90)
pincrease = mpatches.Patch(color='indianred', label='Higher ending pressure')
pdecrease = mpatches.Patch(color='midnightblue', label='Lower ending pressure')
plt.legend(handles=[pincrease, pdecrease])

# Calculate x,y locations of 'defeat' annotations and annotate the scatter plot
# Get series list of the string labels for each "defeat" outcome
string_label = df[df['outcome'] == -1]['battle_date'].values
for i in range(5):
    # find out which x-axis tick corresponds to the label
    label_index = battledates.index(string_label[i])
    # find out which y-axis number corresponds to the label
    y_index = delta_list[label_index]
    plt.annotate('defeat', xy=(label_index-1, y_index-0.5), horizontalalignment='center', verticalalignment='top')

# Show the graph
plt.show()
