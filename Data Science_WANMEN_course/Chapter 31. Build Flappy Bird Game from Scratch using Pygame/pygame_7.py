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
BaseY=SCREENHEIGHT*0.79 #Ground Level where pipe stands
PipeGapSize=100 #Vertical distance between two pipes

#declare a dictionary to store all kinds of images to be loaded by pygame.
IMAGES = {}



import pygame
from pygame.locals import *
from sys import exit #引入sys中exit函数
import random

#FPS
FPS=30
FPSCLOCK=pygame.time.Clock()


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



#get pipe's width and height information for later use.
PIPE_WIDTH = IMAGES['pipe'][0].get_width()
PIPE_HEIGHT = IMAGES['pipe'][0].get_height()

#get player(bird)'s height and width info for later use.
PLAYER_HEIGHT=IMAGES['bird'][0].get_height()
PLAYER_WIDTH=IMAGES['bird'][0].get_width()

# x=1/2*SCREENWIDTH
# y=1/2*SCREENHEIGHT
# move_x=0
# move_y=0
flap=0

#Game interface (x,y):
'''(note: (0,0) is at top left corner of the game interface, x increased-> means to the right; y increased -> to downside)
'''

#Generate Random One Pair of Pipes (One upward-facing pipe = lower pipe, one downward-facing pipe = upper pipe)
def getRandomPipe():
		
	GapYs=[20,30,40,50,60,70,80,90] 
	index=random.randint(0,len(GapYs)-1) #random select from GapYs above
	gapY=GapYs[index]
	gapY=int(BaseY*0.2)+gapY #note: BaseY*0.2 is just a hypothetical ceiling base, when not include Base*0.2: the lower pipe bottom y position might be higher than the bottom of game interface. It does not matter it is *0.2,0.1, or 0.3, as long as the generated pipe generally look about right, then it is good.
	#This gapY is the Y position of the bottom of lower pipe.

	# the insert X position of pipe, outside (to the right) of game interface 
	pipeX=SCREENWIDTH+10

	#the insert Y position of upper pipe (insert position of a pipe is always top left corner of the pipe)
	upperPipeY=gapY-PIPE_HEIGHT #since gapY is bottom y position of pipe, therefore, top y position of this pipe is gapY-pipeheight
	#the insert Y position of lower pipe
	lowerPipeY=gapY+PipeGapSize #gapY(bottom y of upper pipe)+PipeGapSize(vertical distance between upper/lower pipe)=top y position of lower pipe

	return [
		{'x':pipeX,'y':upperPipeY}, #upper pipe
		{'x':pipeX,'y':lowerPipeY}  #lower pipe
	]




#Define the moving speed of pipe
pipeVelX=-4 #for each "while True" loop below, pipe should move left for 4 unit distance

#Define player (bird) parameters
playerVelY=0 #Player's (bird's) default velocity along Y 0
playerMaxVelY=10 #max vel along Y, i.e. max vel downwards (+ is downwards, - is upwards)
playerMinVelY=-8 #min vel along Y, i.e. max vel upwards
playerAccY=1 # player downward acceleration due to gravity
playerFlapAcc=-6 #player upward acceleration when flapping
playerFlapped = False	#True when player flaps
playerx=int(SCREENWIDTH*0.2)
playery=int((SCREENHEIGHT-PLAYER_HEIGHT)/2) #playery is the y position bird will show on screen, initiate value is this.

#random generate one pair of pipe
newPipe1=getRandomPipe()
upperPipes=[
			{'x':SCREENWIDTH,'y':newPipe1[0]['y']}
		]
lowerPipes=[
			{'x':SCREENWIDTH,'y':newPipe1[1]['y']}
		]


#Constantly check if QUIT type of event is triggered, if so, then exit the game; if not, then update game interface (pygame.display) with updated e.g. background, bird and pipe
  # e.g. if user close the window of game interface (click "X" at top right corner), for THIS ACTION, event.type=QUIT, then game will exit.
while True:
	for event in pygame.event.get():
		if event.type == QUIT:
			exit()
# human inputs.------------------------			
		elif event.type == KEYDOWN: #KEYDOWN: any button on keyboard get pressed down (key registered)
			# if event.key == K_LEFT: #left arrow key on keyboard
			# 	move_x = -3
			# elif event.key == K_RIGHT: #right arrow key
			# 	move_x = 3
			if event.key == K_UP: #upward arrow
				playerVelY=playerFlapAcc
				playerFlapped=True
			# elif event.key == K_DOWN: #downward arrow
			# 	move_y = 3
		# elif event.type == KEYUP: #KEYUP: any button on keyboard get released (key reset)
		# 	move_x = 0
		# 	move_y = 0

	# x=x+move_x
	# y=y+move_y

 # 	#constraint x,y to limit it inside display area on game interface(screen)
	# if x>SCREENWIDTH:
	# 	x=0
	# elif x<0:
	# 	x=SCREENWIDTH

	# if y>SCREENHEIGHT:
	# 	y=0
	# elif y<0:
	# 	y=SCREENHEIGHT
# ----------------------------------------

	# Move the pair of Pipes from RIGHT TO LEFT
	# upper and lower pipes
	for uPipe, lPipe in zip(upperPipes,lowerPipes):
		uPipe['x']+=pipeVelX
		lPipe['x']+=pipeVelX


	# 按需generate 新的pipe pair (upper+lower pipe), 添加在队列的末尾
	if 0<upperPipes[0]['x']<5: #define: generate new pipe when the the first pipe (leftmost pipe on screen) moved to position where x is within 5 distance units to left side (x=0) of screen 
		newPipe=getRandomPipe()
		#append newpipe to the end of the array
		upperPipes.append(newPipe[0]) 
		lowerPipes.append(newPipe[1])

	# 按需remove old pipe pair(upper+lower pipe), 从队列头部删除
	if upperPipes[0]['x']<-PIPE_WIDTH: #when the old pipe (left most pipe on screen) disappear on screen
		upperPipes.pop(0)
		lowerPipes.pop(0)

	# #Random Function to generate bird flap action
	# input_actions=random.randint(0,6) #return a random integer number between [0,6], including both ends
	# if input_actions%3 ==0:
	# 	playerVelY=playerFlapAcc
	# 	playerFlapped=True

	#Bird(player)'s movement

	if playerVelY<playerMaxVelY and not playerFlapped:
		playerVelY += playerAccY
	if playerFlapped:
		playerFlapped=False

	playery += min(playerVelY,BaseY-playery-PLAYER_HEIGHT)

	if playery<0:
		playery=0

	# x=0.5 * SCREENWIDTH




	# background
	SCREEN.blit(IMAGES['background'], (0,0)) # insert background at (0,0) position of game interface.
	
	# place Pipes on screen
	for uPipe,lPipe in zip(upperPipes,lowerPipes):
		SCREEN.blit(IMAGES['pipe'][0], (uPipe['x'],uPipe['y'])) # upper pipe 
		SCREEN.blit(IMAGES['pipe'][1], (lPipe['x'],lPipe['y'])) # pipe without rotation, inserted at (0,SCREENHEIGHT-PIPE_HEIGHT) position of game interface.


	# place bird on screen
	SCREEN.blit(IMAGES['bird'][flap],(playerx,playery))

	flap=flap+1

	if flap%3==0:
		flap=0


	pygame.display.update()
	FPSCLOCK.tick(FPS)
	#刷新一下画面
