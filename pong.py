import pygame
from time import sleep
from pygame.locals import *
import sys
import math
import random

# colors
BACKGROUND = (44, 62, 80) # #4CD4B0
BALL = (236, 240, 241) # EDD834
PADDLE1_COLOR = (39, 174, 96) # 7D1424
PADDLE2_COLOR = (39, 174, 96)
TEXT = (231, 76, 60)

# screen and general constants
SCREEN_WIDTH = 800 
SCREEN_HEIGHT = 600 

# game objects constants
PADDLE_BOUNDARY_OFFSET = int(0.0625 * SCREEN_WIDTH) # how many pixels the paddle is away from the border of the screen
PADDLE_SPEED = int(0.01 * SCREEN_HEIGHT)
PADDLE_WIDTH = int(0.025 * SCREEN_WIDTH)
PADDLE_HEIGHT = int(0.2 * SCREEN_HEIGHT)
BALL_RADIUS = int(0.008 * (SCREEN_WIDTH + SCREEN_HEIGHT))
BALL_ACCEL = 1.
BALL_START_SPEED = 5.
BALL_MAX_SPEED = 20.

BUF_LEN = 10
BUF_I = [0] * 2
read_buffer = [[0.] * BUF_LEN, [0.] * BUF_LEN]

class Ball():
    def __init__(self):
        self.pos = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2)
        self.vel_x = 0.
        self.vel_y = 0.
        self.cur_speed = BALL_START_SPEED

    def moveBall(self):
        #if self.pos[0] + self.vel_x > SCREEN_WIDTH:
        #    self.vel_x = - self.vel_x
        #elif self.pos[0] + self.vel_x < 0:
        #    self.vel_x = - self.vel_x

        if self.pos[1] + self.vel_y > SCREEN_HEIGHT - BALL_RADIUS:  
            self.vel_y = - self.vel_y
        elif self.pos[1] + self.vel_y < BALL_RADIUS:
            self.vel_y = - self.vel_y

        self.pos = (int(self.pos[0] + self.vel_x), int(self.pos[1] + self.vel_y))

    def updateBall(self):
        self.moveBall()

class Paddle():
    def __init__(self, x_pos, cpu=False):
        self.width = PADDLE_WIDTH
        self.length = PADDLE_HEIGHT

        self.cpu = cpu

        self.speed = PADDLE_SPEED

        self.pos = (x_pos, SCREEN_HEIGHT/2)

    def moveUp(self):
        if not self.pos[1] - PADDLE_SPEED - self.length/2 <= 0:
            self.pos = (self.pos[0], self.pos[1] - PADDLE_SPEED)

    def moveDown(self):
        if not self.pos[1] + PADDLE_SPEED + self.length/2 >= SCREEN_HEIGHT:
            self.pos = (self.pos[0], self.pos[1] + PADDLE_SPEED)

    def getRekt(self):
        left = self.pos[0] - self.width/2
        top = self.pos[1] - self.length/2
        return pygame.Rect(left, top, self.width, self.length)

class Pong():
    def __init__(self, sizeX, sizeY):
        pygame.init()

        self.font = pygame.font.Font(None, 80)

        self.state = False

        self.screen_size = (sizeX, sizeY)
        self.screen = pygame.display.set_mode(self.screen_size) # screen where shit is drawn onto

        self.clock = pygame.time.Clock()

        self.resetGame() # initializes all objects needed for the game to run
    
    def restartGame(self):
        # creates both paddles
        self.paddle1 = Paddle(0 + PADDLE_BOUNDARY_OFFSET)

        if self.two_players:
            self.paddle2 = Paddle(SCREEN_WIDTH - PADDLE_BOUNDARY_OFFSET, cpu=False)
        else:
            self.paddle2 = Paddle(SCREEN_WIDTH - PADDLE_BOUNDARY_OFFSET, cpu=True)

        # create ball
        self.ball = Ball()
        # give ball a random move vector
        self.ball.vel_x, self.ball.vel_y = self.newMoveVector(random.random())
        # randomly gives ball a direction, i.e., left or right
        if bool(random.getrandbits(1)):
            self.ball.vel_x = - self.ball.vel_x

    def resetGame(self):
        self.scores = [0] * 2 # set both player scores to 0

        pygame.joystick.quit()
        pygame.joystick.init()
        # get the number of joysticks connected
        n_joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
        print pygame.joystick.get_count()
        print len(n_joysticks)

        # both sensors are connected
        if len(n_joysticks) == 2:
            # first sensor
            self.joy_sensor1 = pygame.joystick.Joystick(0)
            self.joy_sensor1.init()

            # second sensor
            self.joy_sensor2 = pygame.joystick.Joystick(1)
            self.joy_sensor2.init()

            self.two_players = True
        elif len(n_joysticks) == 1:
            self.joy_sensor1 = pygame.joystick.Joystick(0)
            self.joy_sensor1.init()

            self.two_players = False
        else:
            print "No sensors connected!"
            sys.exit(1)

        # creates both paddles
        self.paddle1 = Paddle(0 + PADDLE_BOUNDARY_OFFSET)

        if self.two_players:
            self.paddle2 = Paddle(SCREEN_WIDTH - PADDLE_BOUNDARY_OFFSET, cpu=False)
        else:
            self.paddle2 = Paddle(SCREEN_WIDTH - PADDLE_BOUNDARY_OFFSET, cpu=True)

        # create ball
        self.ball = Ball()
        # give ball a random move vector
        self.ball.vel_x, self.ball.vel_y = self.newMoveVector(random.random())
        # randomly gives ball a direction, i.e., left or right
        if bool(random.getrandbits(1)):
            self.ball.vel_x = - self.ball.vel_x

    def handleSensors(self):
        # handle sensor 1
        read_pos = self.joy_sensor1.get_axis(0)
        insertToBuffer(read_pos, 0)

        self.paddle1.pos = (self.paddle1.pos[0], getPosfromRead(getAverageReading(0)))

        if self.joy_sensor1.get_button(1):
            self.resetGame()

        # if there are two sensors connected
        if self.two_players:
            # handle sensor 2
            read_pos = self.joy_sensor2.get_axis(0)
            insertToBuffer(read_pos, 1)

            self.paddle2.pos = (self.paddle2.pos[0], getPosfromRead(getAverageReading(1)))

            if self.joy_sensor2.get_button(1):
                self.resetGame()

    def handleInput(self):
        self.handleSensors()

        # handles key presses
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit(1)

        keys = pygame.key.get_pressed()
        if keys[K_s]:
            self.paddle1.moveDown()
        elif keys[K_w]:
            self.paddle1.moveUp()
        elif keys[K_r]:
            self.resetGame()

        if self.paddle2.cpu:
            if self.ball.pos[1] > self.paddle2.pos[1]:
                self.paddle2.moveDown()
            elif self.ball.pos[1] < self.paddle2.pos[1]:
                self.paddle2.moveUp()
            else:
                pass

    def checkCollision(self, paddle): # checks if ball has hit a paddle
        if abs(self.ball.pos[0] - paddle.pos[0]) < BALL_RADIUS + 1 + PADDLE_WIDTH/2 and\
           self.ball.pos[1] - BALL_RADIUS + 1 <= paddle.pos[1] + paddle.length/2 and\
           self.ball.pos[1] >= paddle.pos[1] - paddle.length/2 - BALL_RADIUS + 1:
            
            collision_height = self.ball.pos[1] - paddle.pos[1] + PADDLE_HEIGHT/2
            per = float(collision_height) / PADDLE_HEIGHT

            if per < 0.:
                per = 0.
            if per > 1.:
                per = 1.

            return per

        else: # no collision occured
            return None
    def madePoint(self):
        if self.ball.pos[0] < PADDLE_BOUNDARY_OFFSET:
            return 1
        elif self.ball.pos[0] > SCREEN_WIDTH - PADDLE_BOUNDARY_OFFSET:
            return 2
        else:
            return 0

    def newMoveVector(self, v):
        angle = + (math.pi/2 * v - math.pi/4)

        if not self.ball.cur_speed == BALL_MAX_SPEED:
            self.ball.cur_speed += BALL_ACCEL

        return (self.ball.cur_speed * math.cos(angle), self.ball.cur_speed * math.sin(angle))

    def updateGame(self):
        self.ball.updateBall() # updates ball position

        # checks if ball collided against paddles and calculates new direction
        v = self.checkCollision(self.paddle1)
        if v:
            self.ball.vel_x, self.ball.vel_y = self.newMoveVector(v)

        v = self.checkCollision(self.paddle2)
        if v: 
            self.ball.vel_x, self.ball.vel_y = self.newMoveVector(v)
            self.ball.vel_x = -self.ball.vel_x
               
        # checks if someone scored a point
        if self.madePoint() == 1:
            self.scores[1] += 1
            self.restartGame()
        elif self.madePoint() == 2:
            self.scores[0] += 1
            self.restartGame()

    def drawBall(self):
        pygame.draw.circle(self.screen, BALL, self.ball.pos, BALL_RADIUS, 0)

    def drawPaddles(self):
        pygame.draw.rect(self.screen, PADDLE1_COLOR, self.paddle1.getRekt())
        pygame.draw.rect(self.screen, PADDLE2_COLOR, self.paddle2.getRekt())

    def drawScore(self):
        p1_score_text = self.font.render(str(self.scores[0]), True, TEXT)
        rect_p1 = p1_score_text.get_rect(center=(int(float(SCREEN_WIDTH*0.075)), 40))

        p2_score_text = self.font.render(str(self.scores[1]), True, TEXT)
        rect_p2 = p2_score_text.get_rect(center=(int(float(SCREEN_WIDTH*0.925)), 40))

        self.screen.blit(p1_score_text, rect_p1)
        self.screen.blit(p2_score_text, rect_p2)


    def drawScreen(self):
        self.screen.fill(BACKGROUND)

        self.drawPaddles()
        self.drawBall()

        self.drawScore()

        pygame.display.flip()

    def run(self):
        self.state = True

        while self.state: # while game is running
            self.handleInput() # takes care of input
            self.updateGame() # updates the state of the game according to input
            self.drawScreen() # updates the screen

            #print self.scores

            self.clock.tick(60)

def calcDistance(p1, p2): # returns distance between two points
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

def getPosfromRead(joy_pos):
    leftMin = -1.0
    leftMax = 0.0

    leftSpan = leftMax - leftMin
    rightSpan = SCREEN_HEIGHT

    valueScaled = float(joy_pos - leftMin) / float(leftSpan)

    return valueScaled * rightSpan

def insertToBuffer(new_read, buf_id):
    global BUF_I, read_buffer
    
    read_buffer[buf_id][BUF_I[buf_id]] = new_read
    BUF_I[buf_id] += 1
    if BUF_I[buf_id] == BUF_LEN:
        BUF_I[buf_id] = 0

def getAverageReading(buf_id):
    return sum(read_buffer[buf_id]) / BUF_LEN

if __name__ == "__main__":
    #if len(sys.argv) != 2:
    #    print "Usage", sys.argv[0], "<screen_size>"
    #    sys.exit(1)
    #
    #size = int(sys.argv[1])

    game = Pong(SCREEN_WIDTH, SCREEN_HEIGHT)
    game.run()
