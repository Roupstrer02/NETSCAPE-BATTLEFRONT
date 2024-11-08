import pygame as pg

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
        _, _, Mouse_R = pg.mouse.get_pressed()
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

    
    
    

