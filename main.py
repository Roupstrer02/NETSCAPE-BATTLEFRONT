from game import *
from threading import Thread
from server import activate_server

#========================================================================================================================================
#   To do list:
#
#       - Continue standard game development
#
#========================================================================================================================================

#start up local server
game_server = Thread(target=activate_server)
game_server.start()

#init declarations
screensize = (1600, 900)
screen, clock = start(screensize)

#arena walls
testwall = pg.Rect(800,450,1,1)
testwall = testwall.inflate(500,200)

arena = [testwall]

#player declaration
player = Player(400, 400, arena)

while True:

    #user input
    player.process_user_input()
    read_student_input()

    #object updates
    player.update()

    #screen updates
    screen.fill("lightgray")
    drawterrain(arena, screen)
    player.draw(screen)

    #standard game loop
    pg.display.flip()
    clock.tick(60)
