import pygame as pg
import numpy as np
from nodes import *
from math import sqrt, cos, radians
import copy

#FIX THE DAMN PATHFINDING SO THAT IT'S CONSISTENT


#init declarations
pg.init()
screenSize = (1200,800)
clock = pg.time.Clock()
screen = pg.display.set_mode(screenSize)
pg.display.set_caption('NETSCAPE: BATTLEFRONT')
fpsClock = pg.time.Clock()
controlPointLocations = {"PLAYERBASE": pg.Vector2(1990, 1625), "INVADERBASE": pg.Vector2(3040, 1090), "CONTESTEDPOINT_A": pg.Vector2(2300, 1130), "CONTESTEDPOINT_B": pg.Vector2(2860, 1490)}
controlPointSize = 150
invadersOnMap = []



#Keeps cursor in window
pg.event.set_grab(True)

#Math Inits for LOS
allWallEdgesMatrix = np.array(allWallEdgesList)
allWallEdgeMatrixMathPreCalcA = np.subtract(allWallEdgesMatrix[1,:,0],allWallEdgesMatrix[0,:,0])
allWallEdgeMatrixMathPreCalcB = np.subtract(np.multiply(allWallEdgesMatrix[0,:,1],allWallEdgesMatrix[1,:,0]),np.multiply(allWallEdgesMatrix[1,:,1],allWallEdgesMatrix[0,:,0]))
allWallEdgeMatrixMathPreCalcC = np.subtract(allWallEdgesMatrix[1,:,1],allWallEdgesMatrix[0,:,1])


#Loading Map Image, some Surface inits
worldMap = pg.image.load("Map - Iso.png").convert()
worldCroppedScaled=pg.Surface(screenSize)
world=pg.Surface((5080,2660))#size of the PNG must never change


#Params
startingCameraWorldCoords = [2540,1340]#<--Change Starting Camera Coords Here
startingZoomScale = 1#<--------------------Change Starting Zoom Scale Here

cameraCoords = startingCameraWorldCoords
zoomScale = startingZoomScale

def cropWorldView():
    worldCropped=pg.Surface((screenSize[0]/zoomScale,screenSize[1]/zoomScale))
    worldCropped.blit(world,(0,0),((cameraCoords[0])-screenSize[0]/(2*zoomScale),(cameraCoords[1])-screenSize[1]/(2*zoomScale),screenSize[0]/zoomScale,screenSize[1]/zoomScale))
    worldCroppedScaled = pg.transform.scale(worldCropped,screenSize)#can use smoothscale under certain zoomScale value
    screen.blit(worldCroppedScaled, (0,0))

def screenToWorldCoords(screenCoord):
    return (cameraCoords[0]-(screenSize[0]/2-screenCoord[0])/zoomScale,cameraCoords[1]-(screenSize[1]/2-screenCoord[1])/zoomScale)

def worldToScreenCoords(worldCoord):
    return ((worldCoord[0]-cameraCoords[0])*zoomScale+screenSize[0]/2,(worldCoord[1]-cameraCoords[1])*zoomScale+screenSize[1]/2)

class Player:

    size = (10,20)
    speed = 1

    #lists waypoint vectors where the player moves towards the first element of the list at all times
    path = []
    
    eAbilityCooldown = 120 #frames
    eAbilityDuration = 5 #frames
    eAbilityMousePos = ()

    eAbilityDistance = 100 #px

    eAbilityRemainingFrames = 0
    eAbilityRemainingCooldownFrames = 0

    
    def __init__(self, x, y):
        #we store position separately
        self.position = pg.Vector2(x,y)
        
        self.hitbox = pg.Rect(x-self.size[0]/2, y-self.size[1], self.size[0], self.size[1])
        
        pg.event.pump()
        self.Screen_Mouse_Pos = pg.mouse.get_pos()
        self.World_Mouse_Pos = screenToWorldCoords(self.Screen_Mouse_Pos)
        self.Mouse_L, self.Mouse_M, self.Mouse_R = pg.mouse.get_pressed()
        self.mouseRightPressFlagLast = self.Mouse_R
        self.mouseWheel = 0
        self.keys=pg.key.get_pressed()
        self.keysLast = self.keys

    
        self.disableWalking = False
        
        
    #user input
    def process_user_input(self):
        
        pg.event.pump()
        self.Screen_Mouse_Pos = pg.mouse.get_pos()
        self.World_Mouse_Pos = screenToWorldCoords(self.Screen_Mouse_Pos)
        self.Mouse_L, self.Mouse_M, self.Mouse_R = pg.mouse.get_pressed()
        self.Mouse_Rel_Pos = pg.mouse.get_rel()
        #self.mouseWheel is set outside
        self.keysLast = self.keys
        self.keys=pg.key.get_pressed()

    def eAbilityTick(self):
        if self.eAbilityRemainingCooldownFrames <= 0:
            if self.keys[pg.K_e] and not self.keysLast[pg.K_e]:
                self.path=[]
                self.eAbilityRemainingCooldownFrames=self.eAbilityCooldown
                self.eAbilityRemainingFrames=self.eAbilityDuration
                self.eAbilityMousePos = self.World_Mouse_Pos
                self.eAbilityNormalVector = pg.Vector2(self.eAbilityMousePos[0] - self.position[0], self.eAbilityMousePos[1] - self.position[1]).normalize()
                #Put here anything that should happen on first press
                #distance=self.eAbilityDistance/self.eAbilityDuration


        else:
            self.eAbilityRemainingCooldownFrames-=1
        
        if self.eAbilityRemainingFrames>0:
            #Put here anything that should happen on every tick the ability is active
            
            nextPoint=self.position + (self.eAbilityNormalVector * self.eAbilityDistance / self.eAbilityDuration)
            isInLos, losCollidePoint = lineOfSight(self.position,nextPoint)
            
            if not isInLos:
                #adding small value to losCollidePoint so that its not in a wall
                losCollidePoint=pg.Vector2(losCollidePoint)

                if losCollidePoint[0] > nextPoint[0]:
                    losCollidePoint[0]=losCollidePoint[0] + 0.1
                if losCollidePoint[0] < nextPoint[0]:
                    losCollidePoint[0]=losCollidePoint[0] - 0.1
                
                if losCollidePoint[1] > nextPoint[1]:
                    losCollidePoint[1]=losCollidePoint[1] + 0.1
                if losCollidePoint[1] < nextPoint[1]:
                    losCollidePoint[1]=losCollidePoint[1] - 0.1

                nextPoint=losCollidePoint

            self.position = nextPoint
            self.eAbilityRemainingFrames-=1
        else:
            #Put here anything that should happen on every tick the ability is not active
            pass


            

        

    def updatePlayerCamera(self):
        global zoomScale, cameraCoords
        
        if self.Screen_Mouse_Pos[0]<2:
            cameraCoords[0]-=20/zoomScale
        if self.Screen_Mouse_Pos[0]>screenSize[0]-2:
            cameraCoords[0]+=20/zoomScale
        if self.Screen_Mouse_Pos[1]<2:
            cameraCoords[1]-=20/zoomScale
        if self.Screen_Mouse_Pos[1]>screenSize[1]-2:
            cameraCoords[1]+=20/zoomScale

        if self.Mouse_M:
            cameraCoords[0]-=self.Mouse_Rel_Pos[0]/zoomScale
            cameraCoords[1]-=self.Mouse_Rel_Pos[1]/zoomScale

        if (self.mouseWheel > 0 and zoomScale < 14) or (self.mouseWheel < 0 and zoomScale > 0.2):
            zoomScaleLast=zoomScale
            zoomScale=zoomScale*pow(1.08,self.mouseWheel)
            screenSizeLast=(screenSize[0]/zoomScaleLast,screenSize[1]/zoomScaleLast)
            screenSizeCurr=(screenSize[0]/zoomScale,screenSize[1]/zoomScale)
            cameraCoords[0]+=(screenSizeLast[0]-screenSizeCurr[0])*(self.Screen_Mouse_Pos[0]/screenSize[0])+(screenSizeCurr[0]-screenSizeLast[0])/2
            cameraCoords[1]+=(screenSizeLast[1]-screenSizeCurr[1])*(self.Screen_Mouse_Pos[1]/screenSize[1])+(screenSizeCurr[1]-screenSizeLast[1])/2
            
            self.mouseWheel=0

        if self.keys[pg.K_SPACE]:
            cameraCoords = copy.deepcopy(self.position)
        
        # if self.keys[pg.K_SPACE]:
        #     while(keys[pg.K_SPACE]):
        #         pg.event.pump()
        #         keys=pg.key.get_pressed()
        #     pass

    
    def pathfind(self):
        
        if self.Mouse_R:
            if self.mouseRightPressFlagLast == False:
                self.path = generatePath(self.position, self.World_Mouse_Pos)
            self.mouseRightPressFlagLast=True
        else:
            self.mouseRightPressFlagLast=False


    def updatePos(self):
        if self.disableWalking == False:
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
                        self.position = pg.Vector2(self.path[0])


                        #remove completed waypoint from path
                        del self.path[0]
        self.hitbox.x = self.position[0]-self.size[0]/2
        self.hitbox.y = self.position[1]-self.size[1]
    
    def drawOnWorld(self):
        pg.draw.rect(world, "cyan", self.hitbox)
        pg.draw.circle(world, "red", self.position,1)

    
    def drawOnScreen(self):
        
        pass

#Creating the instance of the player so that it can be used inside of Invader.checkForAggro()
player = Player(2000, 1600)

class Invader:
    size = (1,1)

    health = 1
    maxHealth = 1
    damage = 1
    

    speed = 1
    aggro_range = 400

    attacking_player = False

    #lists waypoint vectors where the entity moves towards the first element of the list at all times
    PermanentTargetDestination = (0,0)
    path = []

    def __init__(self, invaderType, spawnLoc, destinationLoc):
        self.position = pg.Vector2(spawnLoc[0], spawnLoc[1])
        self.PermanentTargetDestination = destinationLoc
        self.path = generatePath(self.position, self.PermanentTargetDestination)

        #change the unit's stats, range, etc. based on invaderType ("zergling", "roach", "hydralisk", "ultralisk", etc.)
        if invaderType == "Zergling":
            self.health = 10
            self.maxHealth = self.health
            self.damage = 2
            self.size = (10,10)

        self.hitbox = pg.Rect(0,0,self.size[0],self.size[1])
        self.healthbar = pg.Rect(round(self.position[0] - (self.size[0] * 0.75)), round(self.position[1] - (self.size[1] * 1.5)), round(self.size[0] * 1.5), round(self.size[1] * 0.2))
        self.hitbox.center = (spawnLoc[0], spawnLoc[1]-self.size[1]/2)

    #All Invaders still need to:
    # be able to target player when nearby and chase them

    def draw(self, surface):

        health_percent_factor_colour = pg.math.lerp(0,255, self.health / self.maxHealth)
        colour = (255 - health_percent_factor_colour, health_percent_factor_colour, 0)
        
        pg.draw.ellipse(surface, "red", self.hitbox)
        pg.draw.rect(surface, colour, self.healthbar)

    #retargets the path to go towards the player if they're in LOS and within aggro range
    def checkForAggro(self):
        LOS, _ = lineOfSight(self.position, player.position)

        if LOS and (player.position - self.position).magnitude() < self.aggro_range:
            self.path = [player.position]
            self.attacking_player = True
        elif self.attacking_player == True and not LOS:

            #In this case, Invaders won't retarget to the nearest objective, and will go to the original one they were given instead
            self.path = generatePath(self.position, self.PermanentTargetDestination)
            self.attacking_player = False

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
                self.position = pg.Vector2(self.path[0])


                #remove completed waypoint from path
                del self.path[0]

    def update(self):
        self.checkForAggro()
        self.move()
        
        self.hitbox.x = self.position[0]-self.size[0]/2
        self.hitbox.y = self.position[1]-self.size[1]

        self.healthbar.x = round(self.position[0] - (self.size[0] * 0.75))
        self.healthbar.y = round(self.position[1] - (self.size[1] * 1.5))

def read_student_input():
    with open('student_input.txt', 'r+') as f:
        for line in f:
            spawninfo = line.split(' ')
            invadersOnMap.append(Invader(spawninfo[0], controlPointLocations[spawninfo[1]], controlPointLocations[spawninfo[2]]))
        f.seek(0)
        f.truncate()

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


    visitableNodes = {start: 0.0}
    visitedNodes = set()
    pathsToNodes = {start: ([start], 0.0)}

    #check if player is already at destination
    if start == end:
        return pathsToNodes.get(start)
    
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
                
                if not elem in visitableNodes.keys() or visitableNodes[elem] > pathSoFar[1] + newDistance:
                    visitableNodes[elem] = pathSoFar[1] + newDistance

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
def generatePath(origin, target):
    
    origin=tuple(origin)
    target=tuple(target)
    
    if origin == target:
        return [origin, target]##############MAKE SURE THIS IS THE SAME STRUCTURS AS THE OTHER RETURN

    ###############
    #STEP0: IF ORIGIN AND TARGET ARE IN LOS, RETURN THEM
    ###############
    isInLos, _ = lineOfSight(origin,target)
    if isInLos:
        return [origin, target] ##############MAKE SURE THIS IS THE SAME STRUCTURS AS THE OTHER RETURN

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
    if not final_path == None: 
        final_path[0].append(target)
        return final_path[0]
    else:
        return []


def checkForInvadersOnPoint(c_point):
    for invader in invadersOnMap:
        
        if entityIsOnControlPoint(invader, c_point):
            return True
    return False

def entityIsOnControlPoint(entity, c_point):
    #distance is proportional to the angle at which you are checking
    relativeVector = (entity.position - c_point)
    relativeVectorAngle = radians(pg.Vector2((-1,0)).angle_to(relativeVector))
    
    a = round(controlPointSize / 4)
    b = round(controlPointSize / 2)
    c = relativeVectorAngle
    
    angledDistanceToCenter = a + ( ((b - a) * (cos(2*c) + 1)) / 2)
    
    if relativeVector.magnitude() <= angledDistanceToCenter:
        return True
    return False

def drawControlPoints():
    for C_Point in controlPointLocations:
        C_Point_Object = pg.Rect(0,0,controlPointSize,round(controlPointSize / 2))
        C_Point_Object.center = controlPointLocations[C_Point]
        colour = "cyan"
        if checkForInvadersOnPoint(C_Point_Object.center):
            colour = "red"
        elif entityIsOnControlPoint(player, C_Point_Object.center):
            colour = "green"
        
        pg.draw.ellipse(world, colour, C_Point_Object, 3)

