# 基本的元素, declare several path to pre-downloaded images for use later.
BACKGROUND_PATH = './assets/sprites/background-black.png' #image of the background
PIPE_PATH = './assets/sprites/pipe-green.png'      #image of the pipe
BASE_PATH = './assets/sprites/base.png'            #image of the ground
PLAYER_PATH = (                                    #bird has 3 types of form, 1. wing flap upwards; 2. wing flag downwards; 3. wing at middle horizontally
        './assets/sprites/redbird-upflap.png',
        './assets/sprites/redbird-midflap.png',
        './assets/sprites/redbird-downflap.png'
) 

#set up game interface size
SCREENWIDTH  = 288
SCREENHEIGHT = 512

#declare a dictionary to store all kinds of images to be loaded by pygame.
IMAGES = {}



import pygame
from pygame.locals import *
from sys import exit #引入sys中exit函数

#初始化pygame,为使用硬件做准备
pygame.init()

#创建了窗口 - GAME INTERFACE
SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))

#设置窗口标题
pygame.display.set_caption("Flappy Bird")

#load图像，convert vs convert_alpha!
IMAGES['background'] = pygame.image.load(BACKGROUND_PATH).convert() #pygame.image.load().convert: convert whole image to pygame-type-of-image WITH IMAGE'S BACKGROUND (e.g. if background of a picture is black, pygame-type-of-image after conversion will have black background)
IMAGES['base'] = pygame.image.load(BASE_PATH).convert_alpha() #pygame.image.load().convert_alpha: convert whole image to pygame-type-of-image WITHOUT IMAGE'S BACKGROUND (e.g. if background of a picture is white, pygame-type-of-image after conversion will not have any background color)
IMAGES['bird'] = (
    pygame.image.load(PLAYER_PATH[0]).convert_alpha(),
    pygame.image.load(PLAYER_PATH[1]).convert_alpha(),
    pygame.image.load(PLAYER_PATH[2]).convert_alpha(),
)
IMAGES['pipe'] = (
    pygame.transform.rotate(pygame.image.load(PIPE_PATH).convert_alpha(), 180), #rotate pipe image upwards for 180 degrees.
    pygame.image.load(PIPE_PATH).convert_alpha()                                #pipe image without rotation.
)

#get pipe's width adn height information for later use.
PIPE_WIDTH = IMAGES['pipe'][0].get_width()
PIPE_HEIGHT = IMAGES['pipe'][0].get_height()

# check if QUIT type of event is triggered constantly, if so, then exit the game; if not, then update game interface (pygame.display) with updated background and pipe
  # e.g. if user close the window of game interface (click "X" at top right corner), for THIS ACTION, event.type=QUIT, then game will exit.
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            exit()

    # background
    SCREEN.blit(IMAGES['background'], (0,0)) # insert background at (0,0) position of game interface.
    SCREEN.blit(IMAGES['pipe'][0], (0,0)) # rotated pipe (180 degree, upside down), inserted at (0,0) position of game interface. (note: (0,0) is at top left of the game interface, x increased-> means to the right; y increased -> to downside)
    SCREEN.blit(IMAGES['pipe'][1], (0,SCREENHEIGHT-PIPE_HEIGHT)) # pipe without rotation, inserted at (0,SCREENHEIGHT-PIPE_HEIGHT) position of game interface.


    pygame.display.update()
    #刷新一下画面
