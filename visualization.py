import matplotlib.pyplot as plt
import pandas as pd
import sqlite3 as sql


conn = sql.connect('barometer.sqlite')

migraine = pd.read_sql_query('''SELECT * FROM v_migraine_data''', conn)
conn.close()
print(migraine.head())

value1 = migraine['pressurestart']
value2 = migraine['pressureend']
outcome = migraine['outcome']
battledate = migraine['battle_date'] + ' - ' + migraine['battlename']


df = pd.DataFrame({'group': battledate, 'value1': value1, 'value2': value2, 'outcome': outcome})
ordered_df = df.sort_values(by=['group', 'outcome'], ascending=False)
my_range = range(1, len(df.index)+1)

# The horizontal plot is made using the hline function
# TODO: for x in outcome where outcome == -1 marker = 'x', color ='red'

plt.figure(figsize=(10,7))

plt.hlines(y=my_range, xmin=ordered_df['value1'], xmax=ordered_df['value2'], color='grey', alpha=0.4)
plt.scatter(ordered_df['value1'], my_range, color='lightskyblue', alpha=1, label='Start Pressure')
plt.scatter(ordered_df['value2'], my_range, color='lightslategrey', alpha=0.4, label='End Pressure')
plt.legend()
#
# df['compare'] = np.where(migraine['pressurestart'][1].item() > migraine['pressureend'][1].item())
# compare = df['compare']
# print(df['compare'])
#
#
# if compare == True:
#     plt.hlines(y=my_range, xmin=ordered_df['value1'], xmax=ordered_df['value2'], color='red', alpha=0.4)
# else:
#     plt.hlines(y=my_range, xmin=ordered_df['value1'], xmax=ordered_df['value2'], color='grey', alpha=0.4)
# plt.scatter(ordered_df['value1'], my_range, color='lightskyblue', alpha=1, label='Start Pressure')
# plt.scatter(ordered_df['value2'], my_range, color='lightslategrey', alpha=0.4, label='End Pressure')
# plt.legend()

# Add title and axis names
plt.yticks(my_range, ordered_df['group'])
plt.title("Starting and Ending Barometric Pressure for Each Napoleonic Battle", loc='left')
plt.xlabel('Barometric Pressure (mbar) - start of battle and end of battle')
plt.ylabel('Start Date of Napoleonic Battle (yyyy-mm-dd)')

# Show the graph
plt.show()


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
