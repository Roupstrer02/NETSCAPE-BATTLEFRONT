import pygame as pg
import numpy as np
from nodes import *
from math import sqrt
import copy

controlPointLocations = {"PLAYERBASE": (1990, 1625), "INVADERBASE": (3040, 1090), "CONTESTEDPOINT_A": (2300, 1130), "CONTESTEDPOINT_B": (2860, 1490)}
invadersOnMap = []
class Player:

    size = (15,15)
    reticlesize = (3, 3)

    health = 100
    damage = 20
    speed = 1

    #lists waypoint vectors where the player moves towards the first element of the list at all times
    path = []
    
    def __init__(self, x, y):
        self.hitbox = pg.Rect(x, y, self.size[0], self.size[1])
        self.reticle = pg.Rect(x, y, self.reticlesize[0], self.reticlesize[1])
        
        #we store position separately
        self.position = pg.Vector2(self.hitbox.center)
        self.target = pg.Vector2(self.hitbox.center)

    def draw(self, surface):
        pg.draw.ellipse(surface, "cyan", self.hitbox)

        if not self.reticle.colliderect(self.hitbox):
            pg.draw.ellipse(surface, "darkred", self.reticle)

    #user input
    def process_user_input(self, mouse_screen_coords):
        pg.event.pump()
        Mouse_L, Mouse_M, Mouse_R = pg.mouse.get_pressed()
        

        if Mouse_R:
            self.target = pg.Vector2(mouse_screen_coords)
            self.reticle.center = mouse_screen_coords
            self.path = self.pathfind()
    
    #will simply target location, unless in wall, will target nearest possible location
    def pathfind(self):

        #if i'm going to put in proper pathfinding, it would go here
        return [self.target]

    def update(self):
        if not len(self.path) == 0:
            if not self.path[0] == self.position:
                direction = pg.Vector2(self.path[0][0] - self.position[0], self.path[0][1] - self.position[1]).normalize()
            else:
                direction = pg.Vector2((0,0))

            #this if/else stops jittering when arriving at any waypoint
            if ((self.path[0] - self.position).magnitude() > self.speed):
                self.position += self.speed * direction
            else:
                self.position = self.path[0]


                #remove completed waypoint from path
                del self.path[0]
            self.hitbox.center = (round(self.position[0]), round(self.position[1]))

class Invader:
    size = (1,1)

    health = 1
    damage = 1
    

    speed = 1
    aggro_range = 1

    #lists waypoint vectors where the entity moves towards the first element of the list at all times
    PermanentTargetDestination = (0,0)
    path = []

    def __init__(self, invaderType, spawnLoc, destinationLoc):
        self.position = pg.Vector2(spawnLoc[0], spawnLoc[1])
        self.PermanentTargetDestination = destinationLoc
        self.path = generatePath(self.PermanentTargetDestination, self.position)[0]
        print(self.path)

        #change the unit's stats, range, etc. based on invaderType ("zergling", "roach", "hydralisk", "ultralisk", etc.)
        if invaderType == "Zergling":
            self.health = 10
            self.damage = 2
            self.size = (10,10)
        
        self.hitbox = pg.Rect(0,0,self.size[0],self.size[1])
        self.hitbox.center = (spawnLoc[0], spawnLoc[1])

    #All Invaders still need to:
    # be able to target player when nearby and chase them

    def draw(self, surface):
        pg.draw.ellipse(surface, "red", self.hitbox)

    def checkForAggro(self):
        pass

    def move(self):
        if not len(self.path) == 0:
            remainingPathSegment = pg.Vector2(self.path[0][0] - self.position[0], self.path[0][1] - self.position[1])
            if not self.path[0] == self.position:
                direction = pg.Vector2(self.path[0][0] - self.position[0], self.path[0][1] - self.position[1]).normalize()
                
            else:
                direction = pg.Vector2((0,0))

            #this if/else stops jittering when arriving at any waypoint
            if (remainingPathSegment.magnitude() > self.speed):
                self.position += self.speed * direction
            else:
                self.position = self.path[0]


                #remove completed waypoint from path
                del self.path[0]
            self.hitbox.center = (round(self.position[0]), round(self.position[1]))

    def update(self):
        self.move()

def read_student_input():
    with open('student_input.txt', 'r+') as f:
        for line in f:
            spawninfo = line.split(' ')
            invadersOnMap.append(Invader(spawninfo[0], controlPointLocations[spawninfo[1]], controlPointLocations[spawninfo[2]]))
        f.seek(0)
        f.truncate()

allWallEdgesMatrix = np.array(allWallEdgesList)
allWallEdgeMatrixMathPreCalcA = np.subtract(allWallEdgesMatrix[1,:,0],allWallEdgesMatrix[0,:,0])
allWallEdgeMatrixMathPreCalcB = np.subtract(np.multiply(allWallEdgesMatrix[0,:,1],allWallEdgesMatrix[1,:,0]),np.multiply(allWallEdgesMatrix[1,:,1],allWallEdgesMatrix[0,:,0]))
allWallEdgeMatrixMathPreCalcC = np.subtract(allWallEdgesMatrix[1,:,1],allWallEdgesMatrix[0,:,1])

# WARNING!!!!!!   Line indicated below can not detect wall when target and origin are horizontal
#                    v v both are (x,y)
def lineOfSight(origin,target):
    
    
    if (target[0]==origin[0]):
        target=(target[0]+0.001,target[1])
    
    deltaXIntermediate = target[0]-origin[0]
    #vvThis line is at fault
    xThresh = np.divide(np.subtract(np.multiply(deltaXIntermediate,allWallEdgeMatrixMathPreCalcB),np.multiply(allWallEdgeMatrixMathPreCalcA,(origin[1]*target[0]-origin[0]*target[1]))),np.subtract(   np.multiply(allWallEdgeMatrixMathPreCalcA,(target[1]-origin[1]))    ,    np.multiply(allWallEdgeMatrixMathPreCalcC,deltaXIntermediate)     ))
    
    isNotInLineOfSight = 0 != np.add(np.multiply(np.full((len(xThresh)),origin[0])<xThresh, np.full((len(xThresh)),target[0])>xThresh), np.multiply(np.full((len(xThresh)),origin[0])>xThresh, np.full((len(xThresh)),target[0])<xThresh))                                   &                                np.add(          np.multiply(allWallEdgesMatrix[0,:,0]<=xThresh , allWallEdgesMatrix[1,:,0]>=xThresh)      ,      np.multiply(allWallEdgesMatrix[0,:,0]>=xThresh, allWallEdgesMatrix[1,:,0]<=xThresh)         )    
    
    isAnyNotInLineOfSignt = isNotInLineOfSight.any()
    contactCoord=(0,0)

    isAnyInLineOfSignt = not(isAnyNotInLineOfSignt)

    if isAnyNotInLineOfSignt:
        distToAllActiveXThresh=np.divide(1,np.add(1,np.multiply(np.multiply(np.subtract(xThresh,target[0]),np.subtract(xThresh,target[0])),isNotInLineOfSight)))
        indexOfHitWall = np.argmin(distToAllActiveXThresh)
        yOfxThresh = ((target[1]-origin[1])/(target[0]-origin[0])) * (xThresh[indexOfHitWall]-origin[0])+origin[1]
        contactCoord = (float(xThresh[indexOfHitWall]),float(yOfxThresh))

        #vv Bool of if in LOS        v Coords if in LOS
    return isAnyInLineOfSignt , contactCoord #, indexOfHitWall 

#finds cheapest node within a list of options (formatted as: {n1: 0.0, n2: 0.0, n3: 0.0, ...})
def findCheapestOption(optionsList):
    cheapestCost = min(optionsList.values())

    for key in optionsList.keys():
        if optionsList.get(key) == cheapestCost:
            return key

def dijkstra_pathfinding(start, end, mapGraph):

    start=tuple(start)
    end=tuple(end)

    #check if player is already at destination
    if start == end:
        return []

    visitableNodes = {start: 0.0}
    visitedNodes = set()
    pathsToNodes = {start: ([start], 0.0)}

    while len(visitableNodes) > 0:
        
        #pick new node to look through
        currentNode = findCheapestOption(visitableNodes)
        
        #mark this node as visited
        visitedNodes.add(currentNode)
        
        #add all this node's connections to the visitable node list with their weight from currentNode
        for elem in mapGraph.get(currentNode):

            pathSoFar = pathsToNodes.get(currentNode)
            
            if not elem in visitedNodes:
                newDistance = sqrt((elem[0] - currentNode[0])**2 + (elem[1] - currentNode[1])**2)
                
                visitableNodes[elem] = newDistance

                if currentNode == start:
                    pathsToNodes[elem] = ([currentNode], newDistance)
                
                else:
                    alreadyHasPath = elem in pathsToNodes.keys()
                    
                    if not alreadyHasPath:
                        pathsToNodes[elem] = (pathSoFar[0] + [currentNode], pathSoFar[1] + newDistance)

                    #WHEN ADDING PATHS TO THE DICT, I NEED TO KEEP TRACK OF HOW LONG THEY ARE AND NOT UPDATE THEM IF THEY'RE STRAIGHT UP WORSE
                    elif alreadyHasPath and pathsToNodes.get(elem)[1] > pathSoFar[1] + newDistance:
                        pathsToNodes[elem] = (pathSoFar[0] + [currentNode], pathSoFar[1] + newDistance)

        #mark current node as no longer visitable
        visitableNodes.pop(currentNode)

    #returns None if no path can be found
    return pathsToNodes.get(end)

#this function can take any coords as inputs
def generatePath(target, origin):
    
    origin=tuple(origin)
    target=tuple(target)
    
    if origin == target:
        return ([origin, target], 0) ##############MAKE SURE THIS IS THE SAME STRUCTURS AS THE OTHER RETURN

    ###############
    #STEP0: IF ORIGIN AND TARGET ARE IN LOS, RETURN THEM
    ###############
    isInLos, _ = lineOfSight(origin,target)
    if isInLos:
        return ([origin, target], sqrt( (target[0]-origin[0])*(target[0]-origin[0]) + (target[1]-origin[1])*(target[1]-origin[1]) )) ##############MAKE SURE THIS IS THE SAME STRUCTURS AS THE OTHER RETURN

    ###############
    #STEP1: ADD ORIGIN AND TARGET TO THE PATHFINGING NETWORK
    ###############
    
    workingPathfindingNetwork = {}

    #workingPathfindingNetwork.clear()
    workingPathfindingNetwork = copy.deepcopy(pathfindingNetwork)
    
    workingPathfindingNetwork[origin]=[]
    for currNode in list(workingPathfindingNetwork.keys()):
        if origin != currNode:
            isInLos, _ = lineOfSight(origin,currNode)
            if isInLos:
                workingPathfindingNetwork[origin].append(currNode)
                workingPathfindingNetwork[currNode].append(origin)

    workingPathfindingNetwork[target]=[]            
    for currNode in list(workingPathfindingNetwork.keys()):
        if target != currNode:
            isInLos, _ = lineOfSight(target,currNode)
            if isInLos:
                workingPathfindingNetwork[target].append(currNode)
                workingPathfindingNetwork[currNode].append(target)
    
    
    
    
    
    #in case the target is offthe world map.
    if workingPathfindingNetwork[target] == []:
        workingPathfindingNetwork.pop(target)

        isInLos, losCollidePoint = lineOfSight(target,origin)
        
        #adding small value to losCollidePoint so that its not in a wall
        losCollidePoint=list(losCollidePoint)

        if losCollidePoint[0] > target[0]:
            losCollidePoint[0]=losCollidePoint[0] + 0.1
        if losCollidePoint[0] < target[0]:
            losCollidePoint[0]=losCollidePoint[0] - 0.1
        
        if losCollidePoint[1] > target[1]:
            losCollidePoint[1]=losCollidePoint[1] + 0.1
        if losCollidePoint[1] < target[1]:
            losCollidePoint[1]=losCollidePoint[1] - 0.1

        losCollidePoint=tuple(losCollidePoint)

        target = losCollidePoint
        workingPathfindingNetwork[target]=[]            
        for currNode in list(workingPathfindingNetwork.keys()):
            if target != currNode:
                isInLos, _ = lineOfSight(target,currNode)
                if isInLos:
                    workingPathfindingNetwork[target].append(currNode)
                    workingPathfindingNetwork[currNode].append(target)
    
    
    
    
    #in case the origin is offthe world map.
    if workingPathfindingNetwork[origin] == []:
        workingPathfindingNetwork.pop(origin)

        isInLos, losCollidePoint = lineOfSight(origin,target)
        
        #adding small value to losCollidePoint so that its not in a wall
        losCollidePoint=list(losCollidePoint)

        if losCollidePoint[0] > origin[0]:
            losCollidePoint[0]=losCollidePoint[0] + 0.1
        if losCollidePoint[0] < origin[0]:
            losCollidePoint[0]=losCollidePoint[0] - 0.1
        
        if losCollidePoint[1] > origin[1]:
            losCollidePoint[1]=losCollidePoint[1] + 0.1
        if losCollidePoint[1] < origin[1]:
            losCollidePoint[1]=losCollidePoint[1] - 0.1
        
        losCollidePoint=tuple(losCollidePoint)

        origin = losCollidePoint
        workingPathfindingNetwork[origin]=[]            
        for currNode in list(workingPathfindingNetwork.keys()):
            if origin != currNode:
                isInLos, _ = lineOfSight(origin,currNode)
                if isInLos:
                    workingPathfindingNetwork[origin].append(currNode)
                    workingPathfindingNetwork[currNode].append(origin)
            
    
    
    ###############
    #STEP2: RUN DIJKSTRA ON THE NEW NETWORK
    ###############
    final_path = dijkstra_pathfinding(origin, target, workingPathfindingNetwork)
    final_path[0].append(target)
    return final_path
