import pygame
from time import sleep
from pygame.locals import *
import sys

WHITE = (255, 255, 255)
BALL_COLOR = (255, 0, 0)

pygame.init()

#joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
joystick = pygame.joystick.Joystick(0)
joystick.init()

print "Number of axes for joystick:"
print joystick.get_numaxes()

screen = pygame.display.set_mode((500, 500))

ball_x = 250
ball_y = 250

buf_len = 10
buf_i = 0
read_buffer = [0] * buf_len

def drawScreen():
    screen.fill(WHITE)
    
    pygame.draw.circle(screen, BALL_COLOR, (ball_x, ball_y), 10, 0)

    pygame.display.flip()

def getPosfromRead(joy_pos):
    return int(((joy_pos + 1) * 500)/2)

def insertToBuffer(new_read):
    global buf_i, read_buffer
    
    read_buffer[buf_i] = new_read

    buf_i += 1
    if buf_i == buf_len:
        buf_i = 0

def getAverageReading():
    return sum(read_buffer) / buf_len

def handleInput():
    global ball_x

    for event in pygame.event.get():
        if event.type == QUIT:
            sys.exit(1)

    read_pos = joystick.get_axis(0)
    print read_pos
    insertToBuffer(read_pos)

    ball_x = getPosfromRead(getAverageReading())
    print getAverageReading()
    print ball_x
    #if read_pos > -0.95 and read_pos < 0.95:
    #    ball_x = getPosfromRead(read_pos)

while True:
    drawScreen()
    handleInput()

    sleep(0.017)
