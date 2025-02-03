import pygame as pg
from pygame.locals import *
import numpy as np
from nodes import *
from math import sqrt, sin, cos, radians, pi
import copy
import random as rd

#Debug mode
debugMode = False

#init declarations
pg.init()
screenSize = (1200,800)
clock = pg.time.Clock()
screen = pg.display.set_mode(screenSize)
pg.display.set_caption('NETSCAPE: BATTLEFRONT')
fpsClock = pg.time.Clock()

# Main Menu declarations #
# ====================== #
startGameButton = pg.Rect(0,0,screen.get_width() * 0.4, screen.get_height() * 0.2)
startGameButton.center = (screen.get_width() * 0.5, screen.get_height() * 0.85)

startGameButtonColor = (40,150,40)

menuFont = pg.font.Font('freesansbold.ttf', 34)
startGameButtonText = menuFont.render("Start Game", False, 'black')
startGameButtonTextRect = startGameButtonText.get_rect()
startGameButtonTextRect.center = startGameButton.center
# ====================== #

invadersOnMap = []

listOfAllProjectiles = []

GameState = 0
Victory = 0
controlPointLocations = {"PLAYERBASE": pg.Vector2(1990, 1625), "INVADERBASE": pg.Vector2(3040, 1090), "CONTESTEDPOINT_A": pg.Vector2(2300, 1130), "CONTESTEDPOINT_B": pg.Vector2(2860, 1490)}
controlPointSize = 150

gameFont = pg.font.Font('freesansbold.ttf', 12)
uiFont = pg.font.Font('freesansbold.ttf', 28)

invader_resources = dict()
invader_color_uuid = dict()
invader_resourcebar_color = 0xFFCC00 # **THE** orange color <==
resource_gen_tick = 0
resource_gen_speed = 1 #measured in resource/s
unitTypeCost = {"Zergling": 10, "Roach": 15, "Hydralisk": 20, "Ultralisk": 30}
#Keeps cursor in window
pg.event.set_grab(True)

#Math Inits for LOS
allWallEdgesMatrix = np.array(allWallEdgesList)
allWallEdgeMatrixMathPreCalcA = np.subtract(allWallEdgesMatrix[1,:,0],allWallEdgesMatrix[0,:,0])
allWallEdgeMatrixMathPreCalcB = np.subtract(np.multiply(allWallEdgesMatrix[0,:,1],allWallEdgesMatrix[1,:,0]),np.multiply(allWallEdgesMatrix[1,:,1],allWallEdgesMatrix[0,:,0]))
allWallEdgeMatrixMathPreCalcC = np.subtract(allWallEdgesMatrix[1,:,1],allWallEdgesMatrix[0,:,1])


#Loading Map Image, some Surface inits
MainMenuBackground = pg.image.load("MainMenuBackground.png").convert()
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

def indexOfInvaderAtPoint(target):
    indexOfInvaderInRange=[]
    distToInvaderInRange=[]
    for invader in invadersOnMap:
        if target[0]>(invader.position[0]-(invader.size[0])/2) and target[0]<(invader.position[0]+(invader.size[0])/2) and target[1]>(invader.position[1]-(invader.size[1])) and target[1]<invader.position[1]:
            distanceToInvader = pg.Vector2(invader.position[0],invader.position[1]-(invader.size[1])/2)-pg.Vector2(target)
            indexOfInvaderInRange.append(invadersOnMap.index(invader))
            distToInvaderInRange.append(distanceToInvader.length_squared())
    if len(indexOfInvaderInRange) == 0:
        return None
    elif len(indexOfInvaderInRange) == 1:
        return indexOfInvaderInRange[0]
    else:
        return indexOfInvaderInRange[distToInvaderInRange.index(min(distToInvaderInRange))]

def pointToPointDist(origin,target):
    return sqrt((target[0]-origin[0])*(target[0]-origin[0])+(target[1]-origin[1])*(target[1]-origin[1]))
             
class Projectile:
    def __init__(self,typeOf,damage,origin,target,speed,life,sizeOf):
        self.typeOfProjectile = typeOf
        self.damageOfProjectile = damage
        self.size = sizeOf
        self.hitbox = pg.Rect(origin[0],origin[1],self.size[0],self.size[1])
        self.position = pg.Vector2(origin[0]+self.size[0]/2, origin[1]+self.size[1]/2)
        self.lifeInTicks = life
        self.deleteMeFlag = False
        

        self.stepVector = pg.Vector2((pg.Vector2(target) - pg.Vector2(origin)).normalize() * speed * isoMoveScaleFactor(origin,target))
        
        
    def deleteProjectile(self):
        self.deleteMeFlag = True
        
    def projectileTick(self):
        if self.typeOfProjectile == "playerPrimary":
            #check if collide with invader <<---------------------------------------------------------
                #deal damage and delete

            #Life Tick Down
            if self.lifeInTicks <= 0:
                self.deleteProjectile()
            else:
                self.lifeInTicks-=1
            
            #move 1 step ()
            nextPos=self.position+self.stepVector
            isInLos, losCollidePoint = lineOfSight(self.position,nextPos)
            
            if not isInLos:
                #adding small value to losCollidePoint so that its not in a wall
                losCollidePoint=pg.Vector2(losCollidePoint)

                if losCollidePoint[0] > nextPos[0]:
                    losCollidePoint[0]=losCollidePoint[0] + 0.1
                if losCollidePoint[0] < nextPos[0]:
                    losCollidePoint[0]=losCollidePoint[0] - 0.1
                
                if losCollidePoint[1] > nextPos[1]:
                    losCollidePoint[1]=losCollidePoint[1] + 0.1
                if losCollidePoint[1] < nextPos[1]:
                    losCollidePoint[1]=losCollidePoint[1] - 0.1

                # draw a poof at losCollidePoint?
                self.deleteProjectile()
            else:
                self.position += self.stepVector
                self.hitbox.x = self.position[0]-self.size[0]/2
                self.hitbox.y = self.position[1]-self.size[1]/2


        if self.typeOfProjectile == "playerQ":
            #check if collide with invader <<---------------------------------------------------------
                #deal damage and delete

            #Life Tick Down
            if self.lifeInTicks <= 0:
                self.deleteProjectile()
            else:
                self.lifeInTicks-=1
            
            #move 1 step ()
            nextPos=self.position+self.stepVector
            isInLos, losCollidePoint = lineOfSight(self.position,nextPos)
            
            if not isInLos:
                #adding small value to losCollidePoint so that its not in a wall
                losCollidePoint=pg.Vector2(losCollidePoint)

                # if losCollidePoint[0] > nextPos[0]:
                #     losCollidePoint[0]=losCollidePoint[0] + 0.1
                # if losCollidePoint[0] < nextPos[0]:
                #     losCollidePoint[0]=losCollidePoint[0] - 0.1
                
                # if losCollidePoint[1] > nextPos[1]:
                #     losCollidePoint[1]=losCollidePoint[1] + 0.1
                # if losCollidePoint[1] < nextPos[1]:
                #     losCollidePoint[1]=losCollidePoint[1] - 0.1

                # draw a poof at losCollidePoint?
                #self.deleteProjectile()


                ######
                dist1ToLosCollidePoint = (pg.Vector2(self.position) - pg.Vector2(losCollidePoint)).length()
                self.position = losCollidePoint

                isoScaleFactorOG=isoMoveScaleFactor((0,0),self.stepVector)

                
                isInLos, _ = lineOfSight(self.position+pg.Vector2(0,0.0001),self.position+pg.Vector2(0.0002,0))

                if isInLos:
                    self.stepVector=self.stepVector.reflect((1,-1))*-1
                else:
                    self.stepVector=self.stepVector.reflect((1,1))*-1

                self.stepVector = pg.Vector2(self.stepVector[0],self.stepVector[1]/4).normalize()*self.stepVector.length()

                nextPos=self.position+self.stepVector.normalize()*(self.stepVector.length() - dist1ToLosCollidePoint)
                isInLos, losCollidePoint = lineOfSight(self.position + self.stepVector*0.001, nextPos)
                if not isInLos:
                    #self.deleteProjectile()
                    
                    dist2toLosCollidePoint = (pg.Vector2(self.position) - pg.Vector2(losCollidePoint)).length()
                    self.position = losCollidePoint
                    
                    isInLos, _ = lineOfSight(self.position+pg.Vector2(0,0.0001),self.position+pg.Vector2(0.0002,0))

                    if isInLos:
                        self.stepVector=self.stepVector.reflect((1,-1))*-1
                    else:
                        self.stepVector=self.stepVector.reflect((1,1))*-1

                    self.stepVector = pg.Vector2(self.stepVector[0],self.stepVector[1]/4).normalize()*self.stepVector.length()



                    self.position += self.stepVector.normalize()*(self.stepVector.length() - dist1ToLosCollidePoint-dist2toLosCollidePoint)
                    self.stepVector = self.stepVector * isoMoveScaleFactor((0,0), self.stepVector) / isoScaleFactorOG
                    self.hitbox.x = round(self.position[0]-self.size[0]/2)
                    self.hitbox.y = round(self.position[1]-self.size[1]/2)



                else:
                    self.position += self.stepVector.normalize()*(self.stepVector.length() - dist1ToLosCollidePoint)
                    self.stepVector = self.stepVector * isoMoveScaleFactor((0,0), self.stepVector) / isoScaleFactorOG
                    self.hitbox.x = round(self.position[0]-self.size[0]/2)
                    self.hitbox.y = round(self.position[1]-self.size[1]/2)




                
                    

                ######



            
            else:
                self.position += self.stepVector
                self.hitbox.x = self.position[0]-self.size[0]/2
                self.hitbox.y = self.position[1]-self.size[1]/2



    def draw(self):
        if self.typeOfProjectile == "playerPrimary":
            pg.draw.ellipse(world, (255, 0, 0), self.hitbox)
        if self.typeOfProjectile == "playerQ":
            pg.draw.ellipse(world, (255, 0, 0), self.hitbox)

def allProjectileTick():
    for projectile in listOfAllProjectiles:
        projectile.projectileTick()
        if projectile.deleteMeFlag:
            listOfAllProjectiles.remove(projectile)

def allProjectileDraw():
    for projectile in listOfAllProjectiles:
        projectile.draw()

        

class Player:

    size = (10,20)
    speed = 1

    maxHealth = 100
    health = maxHealth
    #lists waypoint vectors where the player moves towards the first element of the list at all times
    path = []
    

    autoAtkCooldown = 2 #frames
    autoAtkMousePos = ()

    autoAtkDmg = 10
    autoAtkSpeed = 5
    autoAtkLife = 30
    autoAtkSize = (2,2)

    autoAtkRemainingCooldownFrames = 0
    
    primaryFireAlternateFlag = False


    qAtkCooldown = 2 #frames
    qAtkMousePos = ()

    qAtkDmg = 2
    qAtkSpeed = 6
    qAtkLife = 200
    qAtkSize = (4,4)

    qAtkRemainingCooldownFrames = 0


    dashCooldown = 120 #frames
    dashDuration = 6 #frames
    dashMousePos = ()

    dashDistance = 80 #px

    dashRemainingFrames = 0
    dashRemainingCooldownFrames = 0

    
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
        self.Mouse_L_Last=self.Mouse_L
        self.Mouse_M_Last=self.Mouse_M
        self.Mouse_R_Last=self.Mouse_R
        self.Mouse_L, self.Mouse_M, self.Mouse_R = pg.mouse.get_pressed()
        self.Mouse_Rel_Pos = pg.mouse.get_rel()
        #self.mouseWheel is set outside
        self.keysLast = self.keys
        self.keys=pg.key.get_pressed()

    def damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.position = controlPointLocations["PLAYERBASE"]
            self.health = self.maxHealth
            #also reset cooldowns on death here?



    
    # def leftClickAbilityTick(self):
    #     if self.autoAtkRemainingCooldownFrames <= 0:
    #         if self.keys[pg.K_e] and not self.keysLast[pg.K_e]:
    #             #Put here anything that should happen on first press
    #             self.path=[]
    #             self.autoAtkRemainingCooldownFrames=self.autoAtkCooldown
    #             self.autoAtkRemainingFrames=self.autoAtkDuration
    #             self.autoAtkMousePos = self.World_Mouse_Pos
    #             self.eAbilityNormalVector = pg.Vector2(self.dashMousePos[0] - self.position[0], self.dashMousePos[1] - self.position[1]).normalize()
                
    #     else:
    #         self.autoAtkRemainingCooldownFrames-=1
        
    #     if self.autoAtkRemainingFrames>0:
    #         #Put here anything that should happen on every tick the ability is active
            
    #         #At the end:
    #         self.dashRemainingFrames-=1
    #     else:
    #         #Put here anything that should happen on every tick the ability is not active
    #         pass



    def leftClickAbilityTick(self):
        if self.autoAtkRemainingCooldownFrames <= 0:
            if self.Mouse_L and not self.keys[pg.K_q]:
                #Put here anything that should happen on first press
                self.autoAtkRemainingCooldownFrames=self.autoAtkCooldown
                self.autoAtkMousePos = self.World_Mouse_Pos
                atkOrigin = (pg.Vector2(self.autoAtkMousePos) - pg.Vector2(self.position[0],self.position[1]-self.size[1]/2)).normalize()*self.size[0]/2
                
                if self.primaryFireAlternateFlag:
                    atkOrigin = pg.Vector2(-atkOrigin[1],atkOrigin[0])
                    atkOrigin = atkOrigin*isoMoveScaleFactor((0,0),atkOrigin)
                    atkOrigin += pg.Vector2(self.position[0],self.position[1]-self.size[1]/2)
                else:
                    atkOrigin = pg.Vector2(atkOrigin[1],-atkOrigin[0])
                    atkOrigin = atkOrigin*isoMoveScaleFactor((0,0),atkOrigin)
                    atkOrigin += pg.Vector2(self.position[0],self.position[1]-self.size[1]/2)
                self.primaryFireAlternateFlag = not self.primaryFireAlternateFlag

                listOfAllProjectiles.append(Projectile("playerPrimary",self.autoAtkDmg,atkOrigin,self.World_Mouse_Pos,self.autoAtkSpeed,self.autoAtkLife,self.autoAtkSize))
                
        else:
            self.autoAtkRemainingCooldownFrames-=1




    def qAbilityTick(self):
        if self.qAtkRemainingCooldownFrames <= 0:
            if self.Mouse_L and self.keys[pg.K_q]:
                #Put here anything that should happen on first press
                self.qAtkRemainingCooldownFrames=self.qAtkCooldown
                self.qAtkMousePos = self.World_Mouse_Pos
                atkOrigin = (self.position[0],self.position[1]-self.size[1]/2)

                self.primaryFireAlternateFlag = not self.primaryFireAlternateFlag

                listOfAllProjectiles.append(Projectile("playerQ",self.qAtkDmg,atkOrigin,self.World_Mouse_Pos,self.qAtkSpeed,self.qAtkLife,self.qAtkSize))
                
        else:
            self.qAtkRemainingCooldownFrames-=1







    def eAbilityTick(self):        
        if self.dashRemainingCooldownFrames <= 0:
            if self.keys[pg.K_e] and not self.keysLast[pg.K_e]:
                self.path=[]
                self.dashRemainingCooldownFrames=self.dashCooldown
                self.dashRemainingFrames=self.dashDuration
                self.dashMousePos = self.World_Mouse_Pos
                self.eAbilityNormalVector = pg.Vector2(self.dashMousePos[0] - self.position[0], self.dashMousePos[1] - self.position[1]).normalize()
                #Put here anything that should happen on first press
                #distance=self.dashDistance/self.dashDuration

        else:
            self.dashRemainingCooldownFrames-=1
        
        if self.dashRemainingFrames>0:
            #Put here anything that should happen on every tick the ability is active
            
            nextPoint = self.position + (self.eAbilityNormalVector * self.dashDistance * isoMoveScaleFactor(self.position,self.dashMousePos) / self.dashDuration)
            
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
            self.dashRemainingFrames-=1
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
                if self.keys[pg.K_LSHIFT] and self.path != []:
                    self.path.extend(generatePath(self.path[-1], self.World_Mouse_Pos))

                else:
                    self.path = generatePath(self.position, self.World_Mouse_Pos)
            self.mouseRightPressFlagLast=True
        else:
            self.mouseRightPressFlagLast=False


    def updatePos(self):
        if self.disableWalking == False:
            if not len(self.path) == 0:
                currSpeed = self.speed*isoMoveScaleFactor(self.position,self.path[0])
                remainingPathSegment = pg.Vector2(self.path[0][0] - self.position[0], self.path[0][1] - self.position[1])
                if not self.path[0] == self.position:
                    direction = pg.Vector2(self.path[0][0] - self.position[0], self.path[0][1] - self.position[1]).normalize()
                    
                else:
                    direction = pg.Vector2((0,0))

                #this if/else stops jittering when arriving at any waypoint
                
                if (remainingPathSegment.magnitude() > currSpeed):
                    self.position += currSpeed * direction
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

class controlPoint:

    takeover_progress = 0
    takeover_duration = 300  #measured in ticks


    def __init__(self, position, alignment, name):
        self.position = position
        self.name = name
        #alignment: 0 --> player controlled | 1 --> neutral, no control | 2 --> invader controlled 
        self.alignment = alignment

        if alignment == 0:
            self.takeover_progress = -self.takeover_duration
        if alignment == 2:
            self.takeover_progress = self.takeover_duration

    def update(self):
        player_on_point = entityIsOnControlPoint(player, self.position)
        invaders_on_point = checkForInvadersOnPoint(self.position)

        #takeover progress
        if player_on_point and invaders_on_point:
            pass
        
        elif not (player_on_point or invaders_on_point) and self.alignment == 1:
            if self.takeover_progress > 0:
                self.takeover_progress -= 1
            elif self.takeover_progress < 0:
                self.takeover_progress += 1

        elif player_on_point and self.takeover_progress > -self.takeover_duration:
            self.takeover_progress -= 1

        elif invaders_on_point and self.takeover_progress < self.takeover_duration:
            self.takeover_progress += 1
        
        if abs(self.takeover_progress) == self.takeover_duration:
            if self.takeover_progress < 0:
                self.alignment = 0
            else:
                self.alignment = 2

        elif self.takeover_progress == 0:
            self.alignment = 1

    def draw(self):
        visible_object = pg.Rect(0, 0, controlPointSize,round(controlPointSize / 2))
        visible_object.center = self.position
        if self.alignment == 0:
            colour = "green"
        elif self.alignment == 1:
            colour = "cyan"
        elif self.alignment == 2:
            colour = "red"
        
        pg.draw.ellipse(world, colour, visible_object, 3)
        
        if self.takeover_progress != 0:
            takeover_bar = pg.Rect(self.position[0] - (controlPointSize / 4), self.position[1] - int(controlPointSize / 8), round((controlPointSize / 2) * abs(self.takeover_progress / self.takeover_duration)), int(controlPointSize / 15))
            pg.draw.rect(world, "gray", takeover_bar)
            
            text = gameFont.render(str(int(abs(self.takeover_progress / self.takeover_duration)*100)) + '%', True, "black")

            world.blit(text, (self.position[0] - int(text.get_rect().w / 2), takeover_bar.y - 15))

#Yes this is a bit backwards, but honestly it's working and not being inefficient at runtime
controlPoints = {"PLAYERBASE": controlPoint(controlPointLocations["PLAYERBASE"], 0, "PLAYERBASE"), "INVADERBASE": controlPoint(controlPointLocations["INVADERBASE"], 2, "INVADERBASE"), "CONTESTEDPOINT_A": controlPoint(controlPointLocations["CONTESTEDPOINT_A"], 1, "CONTESTEDPOINT_A"), "CONTESTEDPOINT_B": controlPoint(controlPointLocations["CONTESTEDPOINT_B"], 1, "CONTESTEDPOINT_B")}

class Invader:
    size = (1,1)

    health = 1
    maxHealth = 1

    damage = 1
    
    speed = 1
    aggro_range = 400

    attacking_player = False

    PermanentTargetDestination = (0,0)

    #lists waypoint vectors where the entity moves towards the first element of the list at all times
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
            self.speed = 1

        elif invaderType == "Roach":
            self.health = 15
            self.maxHealth = self.health
            self.damage = 1
            self.size = (12,12)
            self.speed = 0.5

        elif invaderType == "Hydralisk":
            self.health = 12
            self.maxHealth = self.health
            self.damage = 3
            self.size = (14,14)
            self.speed = 0.4
        elif invaderType == "Ultralisk":
            self.health = 25
            self.maxHealth = self.health
            self.damage = 1
            self.size = (20,20)
            self.speed = 0.25

        self.healthbarSize = (round(self.size[0] * 1.5), round(self.size[1] * 0.2))
        
        self.hitbox = pg.Rect(0,0,self.size[0],self.size[1])
        self.healthbar = pg.Rect(round(self.position[0] - (self.size[0] * 0.75)), round(self.position[1] - (self.size[1] * 1.5)), self.healthbarSize[0], self.healthbarSize[1])
        self.hitbox.center = (spawnLoc[0], spawnLoc[1]-self.size[1]/2)



    #All Invaders still need to:
    # be able to target player when nearby and chase them

    def draw(self, surface):

        health_percent_factor_colour = pg.math.lerp(0,255, self.health / self.maxHealth)
        health_percent_size = pg.math.lerp(0,self.healthbarSize[0], self.health / self.maxHealth)
        colour = (255 - health_percent_factor_colour, health_percent_factor_colour, 0)
        self.healthbar.w = health_percent_size

        pg.draw.ellipse(surface, "red", self.hitbox)
        pg.draw.rect(surface, colour, self.healthbar)

    def damage(self, amount):
        self.health -= amount

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
            currSpeed = self.speed*isoMoveScaleFactor(self.position,self.path[0])
            remainingPathSegment = pg.Vector2(self.path[0][0] - self.position[0], self.path[0][1] - self.position[1])
            if not self.path[0] == self.position:
                direction = pg.Vector2(self.path[0][0] - self.position[0], self.path[0][1] - self.position[1]).normalize()
                
            else:
                direction = pg.Vector2((0,0))

            #this if/else stops jittering when arriving at any waypoint
            if (remainingPathSegment.magnitude() > currSpeed):
                self.position += currSpeed * direction
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

def init_invader_control_points_file():
    with open("invader_control_points.txt", "w") as cPoints:
        cPoints.seek(0)
        cPoints.truncate()
        cPoints.write("INVADERBASE")

def update_invader_control_points_file():
    Invader_cPoints = list()
    File_cPoints = list()

    with open("invader_control_points.txt", 'r+') as cPoints:
        cPoint_data = cPoints.readline().split(' ')
        for word in cPoint_data:
            File_cPoints.append(word)

        for point in controlPoints:
            if controlPoints[point].alignment == 2:
                Invader_cPoints.append(point)
            
        if Invader_cPoints != File_cPoints:
            cPoints.seek(0)
            cPoints.truncate()
            cPoints.write(' '.join(Invader_cPoints))

def removeDeadInvaders():
    for invader in invadersOnMap:
        if invader.health <= 0:
            invadersOnMap.remove(invader)

def update_invader_resources():
    global resource_gen_tick
    if resource_gen_tick == resource_gen_speed * 60:
        for key in invader_resources:
            invader_resources[key] += 1
        resource_gen_tick = 0
    else:
        resource_gen_tick += 1
    

def read_student_input():
    with open('student_input.txt', 'r+') as f:
        for line in f:
            spawninfo = line.split(' ')
            
            if spawninfo[4] in invader_resources:
                S_Resources = invader_resources[spawninfo[4]]
            else:
                invader_resources[spawninfo[4]] = 50
                invader_color_uuid[spawninfo[4]] = (rd.randint(0,255), rd.randint(0,100), rd.randint(100,255))
                S_Resources = 50
            
            if GameState == 1 and controlPoints[spawninfo[1]].alignment == 2:
                for _ in range(0,int(spawninfo[3])):
                    unitCost = unitTypeCost[spawninfo[0]]
                    if S_Resources >= unitCost:
                        spawnpoint = copy.deepcopy(controlPointLocations[spawninfo[1]])
                        spawnX = int(controlPointSize * 0.8  / 2)
                        spawnY = round(spawnX * sin(rd.random() * (pi / 2)) / 2)
                        spawnpoint[0] += rd.randint(-spawnX, spawnX)
                        spawnpoint[1] += rd.randint(-spawnY, spawnY)

                        destination = copy.deepcopy(controlPointLocations[spawninfo[2]])
                        destX = int(controlPointSize * 0.8  / 2)
                        destY = round(destX * sin(rd.random() * (pi / 2)) / 2)
                        destination[0] += rd.randint(-destX, destX)
                        destination[1] += rd.randint(-destY, destY)
                        invadersOnMap.append(Invader(spawninfo[0], spawnpoint, destination))
                        S_Resources -= unitCost

                invader_resources[spawninfo[4]] = S_Resources
            

        f.seek(0)
        f.truncate()

# WARNING!!!!!!   Line indicated below can not detect wall when target and origin are horizontal
#                    v v both are (x,y)

def displayInvaderResources():
    s_width = screen.get_width()
    s_height = screen.get_height()
    
    all_drawn_resources = []
    for key in invader_resources:
        new_drawn_resource = uiFont.render(str(invader_resources[key]) + " food", False, invader_color_uuid[key])
        all_drawn_resources.append(new_drawn_resource)
        
    #shows invaders in menu
    if GameState == 0:
        
        pg.draw.rect(screen, invader_resourcebar_color, (0, 0, screen.get_width() / 5, screen.get_height()))
        pg.draw.rect(screen, invader_resourcebar_color, (4 * screen.get_width() / 5, 0, screen.get_width() / 5, screen.get_height()))

        for i in range(0,len(all_drawn_resources)):
            drawn_image_rect = all_drawn_resources[i].get_rect()
            drawn_image_rect.center = ((s_width / 10) + (s_width * 8 / 10) * (i % 2), s_height * ((3 + (2 * (i // 2))) / 10))
            screen.blit(all_drawn_resources[i], (drawn_image_rect.x, drawn_image_rect.y))

    #shows invaders in main game
    elif GameState == 1:

        #drawing background first
        pg.draw.rect(screen, invader_resourcebar_color, (0, 0, s_width, int(s_height / 10)))

        for i in range(0,len(all_drawn_resources)):
            drawn_image_rect = all_drawn_resources[i].get_rect()
            drawn_image_rect.center = ((s_width / 2) - (75 * (len(all_drawn_resources)-1)) + (150 * i), s_height / 20)
            screen.blit(all_drawn_resources[i], (drawn_image_rect.x, drawn_image_rect.y))


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
        final_path[0].pop(0)
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

def updateControlPoints():
    for C_Point in controlPoints:
        controlPoints[C_Point].update()

def drawControlPoints():
    for C_Point in controlPoints:
        controlPoints[C_Point].draw()
def isoMoveScaleFactor(currPos, targetPos):
    relativeVector = pg.Vector2(targetPos) - pg.Vector2(currPos) 
    relativeVectorAngle = abs(pg.Vector2((1,0)).angle_to(relativeVector))
    
    if relativeVectorAngle > 90:
        relativeVectorAngle = 180 - relativeVectorAngle
    
    
    relativeVectorAngle=radians(relativeVectorAngle)

    return sqrt(cos(relativeVectorAngle)*cos(relativeVectorAngle)+(sin(relativeVectorAngle)/2)*(sin(relativeVectorAngle)/2))

def drawHighlightOnMousedOverInvader(target):
    indexOfMouseOverInvader = indexOfInvaderAtPoint(target)
    if indexOfMouseOverInvader != None:
        pg.draw.rect(world,(200,40,40), invadersOnMap[indexOfMouseOverInvader].hitbox, 1)


def checkForVictory():
    global Victory, GameState
    Player_C_Points = 0
    Invader_C_Points = 0
    
    for C_Point in controlPoints:
        if C_Point.alignment == 0:
            Player_C_Points += 1
        elif C_Point.alignment == 2:
            Invader_C_Points += 1
    
    #Player Wins -> Victory is 1
    if Player_C_Points == 4:
        GameState = 2
        Victory = 1
    #Invaders Wins -> Victory is -1
    #yes i know that's the opposite of the alignments for control points but so be it...
    elif Invader_C_Points == 4:
        GameState = 2
        Victory = -1

def MainMenu():
    global GameState
    #play main menu music
    pg.event.pump()
    read_student_input()

    L, M, R = pg.mouse.get_pressed()
    mousePos = pg.mouse.get_pos()

    if startGameButton.collidepoint(mousePos) and L:
        GameState = 1

    screen.blit(MainMenuBackground, (0, 0))
    displayInvaderResources()
    pg.draw.rect(screen, startGameButtonColor, startGameButton)
    screen.blit(startGameButtonText, (startGameButtonTextRect.x, startGameButtonTextRect.y))

def playMainGame():
    
    read_student_input()
    update_invader_resources()
    update_invader_control_points_file()
    for event in pg.event.get():
        if event.type == QUIT:
            pg.quit()
        elif event.type == MOUSEWHEEL:
            player.mouseWheel = event.y

                

    player.process_user_input()
    player.updatePlayerCamera()

    player.qAbilityTick()
    player.eAbilityTick()#must happen before updatePOS()
    player.leftClickAbilityTick()






    allProjectileTick()

    updateControlPoints()

    #Drawing World Map
    world.blit(worldMap, (0,0))

    #DRAW HERE WORLD ELEMENTS HERE-------------------------------------------
    drawControlPoints()     
    
    
    player.drawOnWorld()
    allProjectileDraw()
    
    for invader in invadersOnMap:
        invader.update()
        invader.draw(world)

    #player update
    player.pathfind()
    player.updatePos()
    
    #pg.draw.rect(world,"red",(2120-1,1550-1,2,2))

    

            
    drawHighlightOnMousedOverInvader(player.World_Mouse_Pos)


    #------------------------------------------------------------------------

    #Cropping (to save on ram), Zooming, and Displaying World on "screen"
    cropWorldView()

    #DRAW HERE UI ELEMENTS HERE----------------------------------------------
    player.drawOnWorld()
    
    
    #TEMP: MOVE TO DEBUG MODE
    if player.path != []:
            waypoints = player.path
            pg.draw.aaline(screen,"red", worldToScreenCoords(player.position), worldToScreenCoords(waypoints[0]))

            for node in waypoints:
                pg.draw.circle(screen,"red", worldToScreenCoords(node), 6)
            for i in range(len(waypoints)-1):
                pg.draw.aaline(screen,"red", worldToScreenCoords(waypoints[i]), worldToScreenCoords(waypoints[i+1]))

    displayInvaderResources()
    #draw all nodes and network edges
    # for currNode in list(pathfindingNetwork.keys()):
    #         pg.draw.circle(screen,"grey", worldToScreenCoords(currNode), 4)
    #         for targetNode in pathfindingNetwork.get(currNode):
    #             pg.draw.aaline(screen,"grey", worldToScreenCoords(currNode), worldToScreenCoords(targetNode))
    
    
    #Shows Nodes in LOS of player
    # for node in list(pathfindingNetwork.keys()):
    #         isInLos, _ = lineOfSight(player.position,node)
    #         if isInLos:
    #             pg.draw.aaline(screen,"grey", worldToScreenCoords(player.position), worldToScreenCoords(node))
    
    #Shows Nodes in LOS of player's final waypoint
    # if player.path != []:
    #     for node in list(pathfindingNetwork.keys()):
    #             isInLos, _ = lineOfSight(player.path[-1],node)
    #             if isInLos:
    #                 pg.draw.aaline(screen,"grey", worldToScreenCoords(player.path[-1]), worldToScreenCoords(node))
    #------------------------------------------------------------------------

def GameEndScreen():
    global Victory
    if Victory == 1:
        #PLAYER WINS!!!
        pass
    elif Victory == -1:
        #INVADERS WIN!!!
        pass

    #add button here to go back to main menu
    pass



def Begin_Invasion():
    while True:
    
        if GameState == 0:
            MainMenu()
            
        elif GameState == 1:
            playMainGame()

        elif GameState == 2:
            GameEndScreen()
            

        #standard game loop
        pg.display.flip()
        clock.tick(60)
