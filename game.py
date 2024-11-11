import pygame as pg
from math import sqrt

class Player:

    size = (75,75)
    reticlesize = (10, 10)

    health = 100
    damage = 20
    speed = 3

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
    def process_user_input(self):
        pg.event.pump()
        Mouse_L, Mouse_M, Mouse_R = pg.mouse.get_pressed()
        Mouse_Pos = pg.mouse.get_pos()

        if Mouse_R:
            self.target = pg.Vector2(Mouse_Pos)
            self.reticle.center = Mouse_Pos
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

    
def drawterrain(terrain, surface):
    for elem in terrain:
        pg.draw.rect(surface, "green", elem)

def read_student_input():
    with open('student_input.txt', 'r+') as f:
        for line in f:
            print(line)
        f.seek(0)
        f.truncate()


exampleMapGraph = {(0,0): ((2,4),(4,2),(8,1)), (2,4): ((0,0), (4,2)), (4,2): ((0,0), (2,4), (9,5)), (8,1): ((0,0), (9,5)), (9,5): ((4,2), (8,1))}

def dijkstra_pathfinding(start, end):

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
        for elem in exampleMapGraph.get(currentNode):

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





#finds cheapest node within a list of options (formatted as: {n1: 0.0, n2: 0.0, n3: 0.0, ...})
def findCheapestOption(optionsList):
    cheapestCost = min(optionsList.values())

    for key in optionsList.keys():
        if optionsList.get(key) == cheapestCost:
            return key




#====================================================================================================================================================================================
#Testing functions

maybe = dijkstra_pathfinding((0,0), (9,5))
print("\nShortest Path:")
print(maybe)