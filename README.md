## A Geometric Heuristic for Determining Node Placement in Community Networks
A Python script that finds the node combination (and their locations) that serves the most number of people in a community network given a CSV file containing the node and road coordinates.



## Requirements
This script was created in Python 2.7.

Requirements can be found in *requirements.txt*. Simply use `pip install -r requirements.txt` to install them.
Because this script requires the __Shapely__ package, Windows users would have to manually download it (from [here](https://www.lfd.uci.edu/~gohlke/pythonlibs/#shapely)) and install it via `pip install <wheel>`

The CSV file to be used requires a certain format which can be generated using this [Network Node Picker](https://networknodepicker.github.io).



## Usage
Simply do `python geometricHeuristic.py` in the directory containing `geometricHeuristic.py`. 

You will be prompted to input the following:
1. filename of the __CSV file containing the node and road coordinates__
2. filename of the __CSV file in which to save the coordinates of the "optimal" node combination__, along with the coordinates of the stations (people) it covers
3. filename of the __CSV file in which to save the coordinates of all the other node combinations__ (used in the network simulations)
4. filename of the __CSV file in which to save the coordinates of all the stations (people)__ that fill the roads (used in the network simulations)
5. the __number of nodes__ to choose from
6. the __radius (in meters) of the circle that represents a station (person)__. this represents the personal space a person maintains and is used to determine how many people will fill the roads. the default is 0.6 meters

Once you have entered all of those, it will take some time for the script to go through all possible node combinations and return the combination that covers the most number of people. When it's done, the script will display the graph created with Shapely that shows the chosen nodes. You can save the graph using the options provided by the Shapely GUI. 
