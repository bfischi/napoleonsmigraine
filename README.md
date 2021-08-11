# Napoleon's Migraine
![Altered painting of Napoleon by Deroche showing lightning symbols and 'mon dieu' to indicate migraine](MigraineNapoleon.jpg)

It's said that the French statesman and military leader Napoleon Bonaparte [suffered from terrible migraines](https://www.washingtonpost.com/archive/lifestyle/wellness/1994/12/20/migraines-torment-the-worst-in-the-world/581d8895-11c0-4484-959a-30713ec325e7/) during his military campaigns. The cause of these migraines has never been determined.

This program asks the question: What if Napoleon suffered from barometric pressure migraines - that is, migraines that are triggered with barometric pressure changes? Is it possible that such migraines could have contributed to his rare defeats? On this basis, the program compares Napoleon's battle outcomes with barometric pressure changes in the battle region at the time of the battle to see if his losses can be correlated with migraine weather. 

This program was intended as a fun Python learning project for me, and it's [wickedly unscientific](#Caveats).

## Prerequisites
To run this program, you will need to install the following:
* Python 3 (testing was done on Python 3.9.5)
* sqlite3
* ssl
* bs4 (BeautifulSoup)
* matplotlib
* numpy
* pandas

## To run Napoleon's Migraine
1. Run napoleonsmigraine.py
1. Run haversine.py
1. Run correlation.py
1. Run visualization2.py

## <a name="Caveats"></a>Caveats
As mentioned, this is just a fun project with no scientific validity. Here are some of the ways the methodology is, shall we say, questionable:
* Online sources say Napoleon suffered from headaches. However, we do not know what kind of headaches they were. This program assumes they might have been barometric pressure migraines - that is, migraines that occur when the barometric pressure changes. Napoleon may well have not suffered from these types of headaches.
* Barometric pressure tends to change day by day, and hence barometric pressure migraines would tend to be affected by daily weather, not monthly. However, the availability of daily barometric readings for the dates and areas covered by Napoleonic battles is scant. The program therefore uses monthly mean pressure historical reconstructions. Not only is the pressure data on a scale of months rather than days, as would typically affect a barometric pressure migraineur, but that monthly pressure data represents the average, so it's rather suspect on an individual health scale.
* The program assumes that Napoleon was solely responsible for the battles listed as part of his campaigns on Wikipedia. However, other generals were sometimes in command or involved. Therefore, the likelihood that Napoleon having a headache during the planning of any particular battle would affect its outcome is probably pretty low.
* The program approximates the closest barometric pressure readings ("stations" as they're called in this program) to battle sites. The scale of the data is such that these stations can sometimes be pretty far from the site of a battle. They do not take into account local weather patterns or even the elevation at which a battle took place - if it was high in the mountains, the pressure might be lower than at sea level.

## Data Sources
### Historically reconstructed mean barometric pressure data for Europe (1780-1980)
Jones P D ; Wigley T M L ; Briffa K R (2018): Monthly Mean Pressure Reconstructions for Europe (1780-1980) and North America (1858-1980) (1987) (NDP-025). Carbon Dioxide Information Analysis Center (CDIAC), Oak Ridge National Laboratory (ORNL), Oak Ridge, TN (United States). doi:10.3334/CDIAC/CLI.NDP025

### Wikipedia
En.wikipedia.org. 2021. Military career of Napoleon Bonaparte - Wikipedia. [online] Available at: <https://en.wikipedia.org/wiki/Military_career_of_Napoleon_Bonaparte#Battle_record_summary> [Accessed 11 August 2021].
