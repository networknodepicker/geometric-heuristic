from matplotlib import pyplot
from shapely.geometry import MultiPolygon, Polygon, Point
from descartes.patch import PolygonPatch
from csv import reader, writer
from numpy import linspace
from itertools import combinations
import math

def runMain():
	accessPoints	   = []	 	#list of coordinates of all possible APs
	roads              = []  	#list of coordinates of roads 
	people             = []  	#for shapely graph and getting max people served
	insidePeople	   = []  	#for shapely graph, all of the people that will be served
	maxWired	       = []  	#list of wired APs that serves max number of people
	maxWireless	       = []  	#list of wireless APs that serves max number of people
	maxAPs			   = []	 	#list of APs that serve max number of people
	meshWired		   = []	 	#the wired AP that the first wireless AP will connect to
	minPointX          = 0   	#x-coordinate of minimum point 
	minPointY          = 0   	#y-coordinate of minimum point 
	maxPointX          = 0   	#x-coordinate of maximum point
	maxPointY          = 0   	#y-coordinate of maximum point
	maxPeople          = 0   	#maximum number of people to be served
	numAPs      	   = 0   	#number of APs to choose
	systemLoss		   = 10	 	#for range, default at 10
	normalFrequency    = 2.412  #for range, freq used for AP acting as AP
	meshingFrequency   = 5.18   #for range, freq used for AP meshing with other AP
	normalTxPower	   = 20	 	#for range, txpower used for AP on 2.4GHz channel
	meshingTxPower	   = 23	 	#for range, txpower used for AP on 5GHz channel
	antennaGain		   = 5 	 	#for range, default at 5
	LogDistanceExp	   = 4.5	#for range, default at 4.5 or 6

	csvFile   		 = raw_input("CSV file to use: ")
	saveOptimalFile  = raw_input("CSV file to save optimal in: ")
	saveOthersFile   = raw_input("CSV file to save others in: ")
	saveSTAsFile	 = raw_input("CSV file to save STA coordinates in: ")
	numAPs 			 = input("Number of access points to choose: ")
	personalDistance = input("Personal distance to use: ") #default is 0.6

	with open(saveOthersFile, "w") as f:
		csvWriter = writer(f)
		f.close()

	print "*** Reading coordinates from coordinates file"
	with open(csvFile, "rb") as f:
		r = reader(f)
		addToList = 0 #0 default, 1 add to AP list, 2 add to roads list
		lineSet = []
		for row in r:
			if(row[0] == "long"):
				addToList = 1
			elif(row[0] == "linelong"):
				addToList = 2
			elif(row[0] == "wiredlong"):
				addToList = 3
			elif(row[0] == "" and addToList == 2):
				roads.append(lineSet)
				lineSet = []
			elif(row[0] != "" and addToList == 2):
				x = float(row[0])
				y = float(row[1])
				lineSet.append([x,y])
			elif(row[0] == "" and addToList == 1):
				pass
			elif(row[0] == "" and addToList == 3):
				pass
			elif(addToList == 1):
				x = float(row[0])
				y = float(row[1])
				accessPoints.append([x,y,"wireless"])
			elif(addToList == 3):
				x = float(row[0])
				y = float(row[1])
				accessPoints.append([x,y,"wired"])
		f.close()

	print "*** Getting min/max X/Y graph coordinates"
	
	minRoadX = []
	minRoadY = []
	maxRoadX = []
	maxRoadY = []
	for road in roads:
		minRoadX.append(min(road, key=lambda x: x[0]))
		minRoadY.append(min(road, key=lambda x: x[1]))
		maxRoadX.append(max(road, key=lambda x: x[0]))
		maxRoadY.append(max(road, key=lambda x: x[1]))
	minRoadX   =  min(minRoadX, key=lambda x: x[0])
	minRoadY   =  min(minRoadY, key=lambda x: x[1])
	maxRoadX   =  max(maxRoadX, key=lambda x: x[0])
	maxRoadY   =  max(maxRoadY, key=lambda x: x[1])
	
	minPointX  = min(min(accessPoints, key=lambda x: x[0]), minRoadX)[0]
	minPointY  = min(min(accessPoints, key=lambda x: x[1]), minRoadY)[1]
	maxPointX  = max(max(accessPoints, key=lambda x: x[0]), maxRoadX)[0]
	maxPointY  = max(max(accessPoints, key=lambda x: x[1]), maxRoadY)[1]

	for i in range(0,len(accessPoints)):
		accessPoints[i][0] = accessPoints[i][0] - minPointX
		accessPoints[i][1] = accessPoints[i][1] - minPointY

	for i in range(0,len(roads)):
		for j in range(0,len(roads[i])):
			roads[i][j][0] = roads[i][j][0] - minPointX
			roads[i][j][1] = roads[i][j][1] - minPointY
	

	print "*** Getting range for AP use"
	peopleRange  = int(getRange(systemLoss, normalFrequency, normalTxPower, antennaGain, LogDistanceExp))
	meshingRange = int(getRange(systemLoss, meshingFrequency, meshingTxPower, antennaGain, LogDistanceExp))
	print peopleRange, meshingRange

	print "*** Getting best APs"

	fig, ax = pyplot.subplots()
	
	for road in roads:
		poly = Polygon(road)
		patch = PolygonPatch(poly, facecolor='#6699cc', edgecolor='#000000', alpha=0.5)
		ax.add_patch(patch)
		fillWithPeople(poly,people,personalDistance)

	accessPointCombis = list(combinations(accessPoints,numAPs))

	for i in range(0,len(accessPointCombis)):
		accessPointCombis[i] = list(accessPointCombis[i])

		if(checkWirelessConnections(accessPointCombis[i], meshingRange)):
			potentialMax = getMaxPeople(accessPointCombis[i], people, peopleRange)

			with open(saveOthersFile, "a") as f:
				csvWriter = writer(f)
				csvWriter.writerow(["APs"])
				for accessPoint in accessPointCombis[i]:
					csvWriter.writerow([accessPoint[0],accessPoint[1],accessPoint[2]])
				csvWriter.writerow(["Serve",potentialMax[0],"out of",len(people)])
				csvWriter.writerow(" ")
				f.close()
			
			if(potentialMax[0] >= maxPeople):
				maxPeople 	 = potentialMax[0]
				maxAPs		 = accessPointCombis[i]
				insidePeople = potentialMax[1]
	
	with open(saveOptimalFile, "w") as f:
		csvWriter = writer(f)
		csvWriter.writerow(["APs"])
		for accessPoint in maxAPs:
			csvWriter.writerow([accessPoint[0],accessPoint[1],accessPoint[2]])
		csvWriter.writerow(["Serve",len(insidePeople),"out of",len(people)])
		csvWriter.writerow(" ")
		csvWriter.writerow(["STAs"])
		for person in insidePeople:
			csvWriter.writerow([person[0],person[1]])
		f.close()

	with open(saveSTAsFile, "w") as f:
		csvWriter = writer(f)
		for person in people:
			csvWriter.writerow([person[0],person[1]])
		csvWriter.writerow(" ")
		csvWriter.writerow(" ")
		f.close()


	print "*** Plotting shapely graph"

	for accessPoint in accessPoints:
		ax.plot(accessPoint[0],accessPoint[1], 'o', color='#000000', alpha=0.5)
		circ = Point(accessPoint[0],accessPoint[1]).buffer(peopleRange)
		if(accessPoint[2] == "wired"):
			#green for wired APs, darker green for chosen ones
			if(accessPoint in maxAPs):
				patch = PolygonPatch(circ, facecolor='#1aff1a', edgecolor='#000000', alpha=0.7)
			else:
				patch = PolygonPatch(circ, facecolor='#1aff1a', edgecolor='#000000', alpha=0.2)
		else:
			#purple for wireless APs, darker purple for chosen ones 
			if(accessPoint in maxAPs):
				patch = PolygonPatch(circ, facecolor='#1a1aff', edgecolor='#000000', alpha=0.7)
			else:
				patch = PolygonPatch(circ, facecolor='#1a1aff', edgecolor='#000000', alpha=0.2)
		ax.add_patch(patch)

	for person in people:
		if(person in insidePeople):
			p = Point(person[0],person[1]).buffer(personalDistance)
			patch = PolygonPatch(p, facecolor='#ff00ff', edgecolor='#000000', alpha=1.0)
			ax.add_patch(patch)
		else:
			p = Point(person[0],person[1]).buffer(personalDistance)
			patch = PolygonPatch(p, facecolor='#ffffff', edgecolor='#000000', alpha=1.0)
			ax.add_patch(patch)

	xRange = [-50, maxPointX-minPointX+50]
	yRange = [-50, maxPointY-minPointY+50]
	ax.set_xlim(*xRange)
	ax.set_ylim(*yRange)
	ax.set_aspect('equal')
	
	print "Optimal AP combination covers " + str(len(insidePeople)) + " people out of " + str(len(people)) + " people."

	print "*** Showing shapely graph"
	pyplot.show()
	pyplot.close()

	
def getRange(sysLoss, freq, txPower, antGain, exp):
	#from logDistance model in distanceByPropagationModel in mininet-wifi/mininet/wifi/propgationModels.py
	#ref_dist is always set to 1
	#noise_threshold is always set to -91

	refDist = 1
	noiseThreshold = -91
	f = freq * 10 ** 9  # Convert Ghz to Hz
	c = 299792458.0
	lmbd = c / f  # lambda: wavelength (m)
	denominator = lmbd ** 2
	numerator = (4 * math.pi * refDist) ** 2 * sysLoss
	pl = 10 * math.log10(numerator / denominator)
	gains = txPower + (antGain * 2)

	dist = math.pow(10, ((-noiseThreshold - pl + gains) / (10 * exp))) * refDist

	return dist

def checkWirelessConnections(accessPoints, meshingRange):
	#checks if a wireless node to be added is in range of other nodes

	wirelessAPs = []

	for accessPoint in accessPoints:
		if(accessPoint[2] == "wireless"):
			wirelessAPs.append(accessPoint)

	if(len(wirelessAPs) > 0):
		wirelessChecker = ["not connected"]*len(wirelessAPs)

		for i in range(0,len(wirelessAPs)):
			wirelessPoint  = Point(wirelessAPs[i][0],wirelessAPs[i][1])
			wirelessCircle = Point(wirelessAPs[i][0],wirelessAPs[i][1]).buffer(meshingRange)
			for accessPoint in accessPoints:
				apPoint  = Point(accessPoint[0],accessPoint[1])
				apCircle = Point(accessPoint[0],accessPoint[1]).buffer(meshingRange)
				if(wirelessPoint.within(apCircle) and apPoint.within(wirelessCircle)):
					wirelessChecker[i] = "connected"

		if(len(set(wirelessChecker)) == 1 and wirelessChecker[0] == "connected"):
			return True
		else:
			return False
	else:
		return True

def getMaxPeople(accessPoints, people, peopleRange):
	#gets the maximum people that can be found within a node combination

	maxPpl = 0
	insidePeople = []
	apCircles = []
	unionAPs = None

	for accessPoint in accessPoints:
		circ = Point(accessPoint[0],accessPoint[1]).buffer(peopleRange)
		apCircles.append(circ)

	if(len(apCircles) > 1):
		unionAPs = apCircles[0].union(apCircles[1])
		for i in range(2,len(apCircles)):
			unionAPs = unionAPs.union(apCircles[i])
	else:
		unionAPs = apCircles[0]

	for person in people:
		p = Point(person[0],person[1])
		if(p.within(unionAPs)):
			insidePeople.append(person)
			maxPpl += 1

	return maxPpl, insidePeople

def fillWithPeople(road,people,personalDistance):
	#fills a road with people given the interpersonal distance to be used

	bounding = road.bounds
	xDistance = abs(bounding[0]-bounding[2])
	yDistance = abs(bounding[1]-bounding[3])

	if(xDistance > yDistance):
		#horizontal road
		xRange = linspace(bounding[0],bounding[2],200)
		yRange = linspace(bounding[1],bounding[3],200)
	else:
		#vertical road
		xRange = linspace(bounding[0],bounding[2],200)
		yRange =  linspace(bounding[1],bounding[3],200)

	for xCoor in xRange:
		for yCoor in yRange:
			circle = Point(xCoor,yCoor).buffer(personalDistance)
			if(len(people) == 0 and road.contains(circle)):
				people.append([xCoor,yCoor])
			else:
				isValid = True
				for i in range(0,len(people)):
					if((circleCollision([xCoor,yCoor],people[i],personalDistance,personalDistance))):
						isValid = False
						break
				if(isValid and road.contains(circle)):
					people.append([xCoor,yCoor])


def circleCollision(circle1,circle2,radius1,radius2):
	#checks if people circles collide. no two circles should collide with each other

	diffRadius = (radius1 - radius2)**2
	sumRadius = (radius1 + radius2)**2
	centerDist = (circle1[0] - circle2[0])**2 + (circle1[1] - circle2[1])**2
	if(centerDist >= diffRadius and centerDist <= sumRadius):
		return True
	else:
		return False


if(__name__ == '__main__'):
	runMain()