#This is editted based on pygame_10.py from Chapter 31

# 基本的元素, declare several path to pre-downloaded images for use later.
BACKGROUND_PATH = './assets/sprites/background-black.png' #image of the background
PIPE_PATH = './assets/sprites/pipe-green.png'      #image of the pipe
BASE_PATH = './assets/sprites/base.png'            #image of the ground
PLAYER_PATH = (                                    #bird has 3 types of form, 1. wing flap upwards; 2. wing flag downwards; 3. wing at middle horizontally
        './assets/sprites/redbird-upflap.png',
        './assets/sprites/redbird-midflap.png',
        './assets/sprites/redbird-downflap.png'
) 
GAMEOVER_PATH='./assets/sprites/GameOver.PNG' 

#set up game interface size
SCREENWIDTH  = 288
SCREENHEIGHT = 512
BaseY=SCREENHEIGHT*0.9 #Ground Level where pipe stands
PipeGapSize=150 #Vertical distance between two pipes

#declare a dictionary to store all kinds of images to be loaded by pygame.
IMAGES = {}

#declare a dictionary to store all kinds of sounds
SOUNDS = {}

import pygame
from pygame.locals import *
import sys
from sys import exit #引入sys中exit函数
import random
import numpy as np
import pygame.surfarray as surfarray

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

# numbers sprites for score display
IMAGES['numbers'] = (
    pygame.image.load('assets/sprites/0.png').convert_alpha(),
    pygame.image.load('assets/sprites/1.png').convert_alpha(),
    pygame.image.load('assets/sprites/2.png').convert_alpha(),
    pygame.image.load('assets/sprites/3.png').convert_alpha(),
    pygame.image.load('assets/sprites/4.png').convert_alpha(),
    pygame.image.load('assets/sprites/5.png').convert_alpha(),
    pygame.image.load('assets/sprites/6.png').convert_alpha(),
    pygame.image.load('assets/sprites/7.png').convert_alpha(),
    pygame.image.load('assets/sprites/8.png').convert_alpha(),
    pygame.image.load('assets/sprites/9.png').convert_alpha()
)

# game over image
IMAGES['GameOver']=pygame.image.load(GAMEOVER_PATH).convert_alpha()


# sounds
if 'win' in sys.platform:
    soundExt = '.wav'
else:
    soundExt = '.ogg'

SOUNDS['die']    = pygame.mixer.Sound('assets/audio/die' + soundExt)
SOUNDS['hit']    = pygame.mixer.Sound('assets/audio/hit' + soundExt)
SOUNDS['point']  = pygame.mixer.Sound('assets/audio/point' + soundExt)
SOUNDS['swoosh'] = pygame.mixer.Sound('assets/audio/swoosh' + soundExt)
SOUNDS['wing']   = pygame.mixer.Sound('assets/audio/wing' + soundExt)



#get pipe's width and height information for later use.
PIPE_WIDTH = IMAGES['pipe'][0].get_width()
PIPE_HEIGHT = IMAGES['pipe'][0].get_height()

#get player(bird)'s height and width info for later use.
PLAYER_HEIGHT=IMAGES['bird'][0].get_height()
PLAYER_WIDTH=IMAGES['bird'][0].get_width()

flap=0

#Game interface (x,y):
'''(note: (0,0) is at top left corner of the game interface, x increased-> means to the right; y increased -> to downside)
'''

def initiate():
	#Initialize score = 0
	score=0
	#Initialize isCrash=False
	isCrash=False
	#Initiate game sound
	SOUNDS['swoosh'].play()
	#Player position:
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

	playerFlapped = False	#True when player flaps

	return score,isCrash,playerx,playery,upperPipes,lowerPipes,playerFlapped

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


#displays score in center of screen
def showScore(score):
	scoreDigits=[int(x) for x in list(str(score))] #e.g. 12 will be [1,2]
	totalWidth=0 #total width of all numbers to be printed on screen, initialize as 0

	for digit in scoreDigits:
		totalWidth+=IMAGES['numbers'][digit].get_width() #update total width, e.g. 12 will have total width on display as width of picture number 1 + width of picture number 2

	Xoffset = (SCREENWIDTH - totalWidth)/2 #x position of where the score picture will be inserted on screen display

	for digit in scoreDigits:
		SCREEN.blit(IMAGES['numbers'][digit],(Xoffset,SCREENHEIGHT*0.1))
		Xoffset+=IMAGES['numbers'][digit].get_width()

# def showgameover(): #make it print at center of screen (left-right center)
# 	totalWidth=IMAGES['GameOver'].get_width()
# 	Xoffset=(SCREENWIDTH - totalWidth)/2
# 	SCREEN.blit(IMAGES['GameOver'],(Xoffset,SCREENHEIGHT*0.5))

# CHECK crash - return True or False
def checkCrash(playerx,playery,PLAYER_WIDTH,PLAYER_HEIGHT,upperPipes,lowerPipes,PIPE_WIDTH,PIPE_HEIGHT,BaseY):

	#check if player has fallen onto ground level, i.e. BaseY
	if playery+PLAYER_HEIGHT>=BaseY:
		return True
	else:
		#check if player has collide with any of the upper/lower pipe
		#how to check: pygame has a Rect function to store an object's coordinate (x,y) with object's width/height, then it can store the pixel that the object occupied
		#User Defined pixelCollision function can check if any of two or more Rect (pixel occupied) has overlapped, if overlapped, then return True
		playerRect= pygame.Rect(playerx,playery,PLAYER_WIDTH,PLAYER_HEIGHT) # player's Rect

		for uPipe,lPipe in zip(upperPipes,lowerPipes):
			#upper and lower pipe rects:
			uPipeRect=pygame.Rect(uPipe['x'],uPipe['y'],PIPE_WIDTH,PIPE_HEIGHT)
			lPipeRect=pygame.Rect(lPipe['x'],lPipe['y'],PIPE_WIDTH,PIPE_HEIGHT)

			#check pixel collision
			uCollide=pixelCollision(playerRect,uPipeRect) #check pixel collision for player and upper pipe
			lCollide=pixelCollision(playerRect,lPipeRect) #check pixel collision for player and lower pipe

			if uCollide or lCollide:
				return True
	return False


def pixelCollision(rect1,rect2):
	#check if two rects have pixel overlapped
	rect_intersect=rect1.clip(rect2) #Returns a new rectangle that is cropped to be completely inside the argument Rect. If the two rectangles do not overlap to begin with, a Rect with 0 size is returned.

	if rect_intersect.width == 0 or rect_intersect.height == 0: # size of intersection is 0: means no overlap
		return False
	return True


#Reward for RL (reinforcement learning), check-crash, update image...:
def frame_step(input_actions,playerx,playery,PLAYER_WIDTH,PLAYER_HEIGHT,upperPipes,lowerPipes,PIPE_WIDTH,PIPE_HEIGHT,BaseY,score,playerVelY,playerFlapped,flap):
	pygame.event.pump()
	reward=0.0
	score+=0
	terminal=False

	if input_actions == 1: #upward movement
		playerVelY=playerFlapAcc
		playerFlapped=True
		SOUNDS['wing'].play()

	#calculate reward
	playerMidx=playerx+PLAYER_WIDTH/2 # x position of middle point of bird
	for pipe in upperPipes:
		pipeMidx=pipe['x']+PIPE_WIDTH/2 # x position of middle point of each pipe of all current pipes in the set
		if pipeMidx<=playerMidx<pipeMidx+pipeVelX*(-1): #Each loop, pipe moves to left of (-pipeVelX) pixel, (1 sec = FPS times of loops)
														#>=pipeMidx means that: bird must pass current pipe
														#<pipeMidx+pipeVelX*(-1) means that: the score is not added multiple times for each loop in FPS
															#--> If score is added for 1 in current loop, in the next loop, the pipe moves to left for (-pipeVelX) pixel, so the middle point x position will be <=playerMidx, i.e. score will not be added in the next Loop
			score+=1
			reward=1
			SOUNDS['point'].play()


	#Bird(player)'s movement, update player x, y position

	if playerVelY<playerMaxVelY and not playerFlapped:
		playerVelY += playerAccY
	if playerFlapped:
		playerFlapped=False

	playery += min(playerVelY,BaseY-playery-PLAYER_HEIGHT)

	if playery<0:
		playery=0


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


	# RL5. Update delta_x, delta_y
	# 1. check if the first pipe is to the left or to the right of the bird, if first pipe's middle "x" point is to the left of the bird, then pick the second pipe as reference pipe
	if len(lowerPipes)==1:
		tem_p = 0 #pick first pipe in the list
	elif len(lowerPipes)>1 and lowerPipes[0]['x'] > playerx - PIPE_WIDTH/2: 
		tem_p = 0 #pick first pipe in the list
	else:
		tem_p = 1 #pick second pipe in the list

	refer_pipe_x = lowerPipes[tem_p]['x']+PIPE_WIDTH/2
	refer_pipe_y = lowerPipes[tem_p]['y'] - int(1/2*PipeGapSize)
	delta_x = max(0,refer_pipe_x - playerx) #if negative, then pick 0
	delta_y = playery - refer_pipe_y


	#check if bird crashes to floor or pipe:
	isCrash = checkCrash(playerx,playery,PLAYER_WIDTH,PLAYER_HEIGHT,upperPipes,lowerPipes,PIPE_WIDTH,PIPE_HEIGHT,BaseY)
	
	if isCrash:
		SOUNDS['hit'].play()
		SOUNDS['die'].play()
		terminal=True
		#reset the following parameters
		score,isCrash,playerx,playery,upperPipes,lowerPipes,playerFlapped = initiate()
		reward=-1


	''' --------Printing Picture on screen display---------------------'''

	#record current score before crash (for use later in crash events - since in crash events, we don't want the score to be updated)
	# score_beforecrash=score
	# background (BACKGROUND MUST BE DISPLAYED FIRST!!! Otherwise, the black color will overlap (on top of) all other things that are printed before it)
	SCREEN.blit(IMAGES['background'], (0,0)) # insert background at (0,0) position of game interface.

	# place Pipes on screen
	for uPipe,lPipe in zip(upperPipes,lowerPipes):
		SCREEN.blit(IMAGES['pipe'][0], (uPipe['x'],uPipe['y'])) # upper pipe 
		SCREEN.blit(IMAGES['pipe'][1], (lPipe['x'],lPipe['y'])) # pipe without rotation, inserted at (0,SCREENHEIGHT-PIPE_HEIGHT) position of game interface.
	
	# print base (print base after printing pipe because I want the base image on top of the lower pipe, i.e. not showing lower pipe that is embedded into the ground)
	SCREEN.blit(IMAGES['base'], (0,BaseY)) # insert at y=BaseY position, where birds will crash if it hits BaseY position.

	# place bird on screen
	SCREEN.blit(IMAGES['bird'][flap],(playerx,playery))

	flap=flap+1

	if flap%3==0:
		flap=0


	#display score on screen
	print(score)
	showScore(score)

	#save screen image to output
	image_data = pygame.surfarray.array3d(pygame.display.get_surface())

	#刷新一下画面
	pygame.display.update()
	FPSCLOCK.tick(FPS)


	return image_data, reward, terminal, [delta_x,delta_y], score, playerFlapped,flap,upperPipes,lowerPipes,playerx,playery,playerVelY





#Define the moving speed of pipe
pipeVelX=-4 #for each "while True" loop below, pipe should move left for 4 unit distance

#Define player (bird) parameters
playerVelY=0 #Player's (bird's) default velocity along Y 0
playerMaxVelY=10 #max vel along Y, i.e. max vel downwards (+ is downwards, - is upwards)
playerMinVelY=-8 #min vel along Y, i.e. max vel upwards
playerAccY=1 # player downward acceleration due to gravity
playerFlapAcc=-3 #player upward acceleration when flapping

#Initiate:
score,isCrash,playerx,playery,upperPipes,lowerPipes,playerFlapped = initiate()



#RL1. Initialization + create discrete state (non-continuous), 10 pixels per state:

#relative x and y position between bird and central point of the pair of pipe to its right
delta_x=200 
delta_y=0

#we divide the whole game interface to grid, 10x10 pixels per grid. Bird's state/action changes only after exit current grid.
#initialization the state matrix of the whole game interface is height 60 grids, weight 30 grids, each grid can have two actions (fly upwards or do-nothing) therefore it is 2 dimensions
states=24*np.ones([60,30,2]) #note: 60, 30 are just some number I put, it can be changed; 
#24 is just a number I put to initialize the state-value of each state for each action

#change the state-value of action =1 to 8, because due to our setting, upward acceleration is 3 times higher than downward acceleration of gravity,
#therefore when initializing we want to put less weight to upward action, to balance upward and downward fly paths, to make converging faster
states[:,:,1]=8

#optional: If you have saved last time's training data of states matrix, you can load it and continue training from here:
# states = np.load('training/bird42.npy')

#i,j is position index of bird relative to states matrix.
i=int(delta_y//10+30) #10 pixels per grid, +30 means: I normalize the negative index to positive index, e.g. if bird is below pipe, the lowest y index is -30
						# but to reference matrix, the minimum index is 0, therefore, +30 to all y index to normalize
j=int(delta_x//10)
###VIP: we relate delta_x and delta_y with state matrix, because we think there are strong relationships between these two variables and actions, to results in max state value.


#RL3. Use a List to store bird's fly path:
fly_path=[]
terminal=False
gamma = 0.95
count = 0


#Constantly check if QUIT type of event is triggered, if so, then exit the game; if not, then update game interface (pygame.display) with updated e.g. background, bird and pipe
  # e.g. if user close the window of game interface (click "X" at top right corner), for THIS ACTION, event.type=QUIT, then game will exit.
while True:
	for event in pygame.event.get():
		if event.type == QUIT:
			exit()

#RL2. 飞行动作根据状态环境而定: (update policy(action) using state-value)
	i=int(delta_y//10+30)
	j=int(delta_x//10)

	ratio= states[i,j,1]/(states[i,j,0]+states[i,j,1]) #this ratio is state-value of action 1 vs. total state-value of action 1 + xxx of action 0

	#use a random number between [0, 1), if the number is between [0,ratio), then do action 1, otherwise, do action 0
		#this method will ensure if action 1 has larger state value, the probability of taking action 1 is larger, vise-versa
	if random.random()<ratio:
		action=1
	else:
		action=0

#RL3. Use a List to store bird's fly path:
	if terminal==False:
		fly_path.append([i,j,action])

	image_data,reward,terminal,[delta_x,delta_y],score,playerFlapped,flap,upperPipes,lowerPipes,playerx,playery,playerVelY = frame_step(action,playerx,playery,PLAYER_WIDTH,PLAYER_HEIGHT,upperPipes,lowerPipes,PIPE_WIDTH,PIPE_HEIGHT,BaseY,score,playerVelY,playerFlapped,flap)

#RL4. 根据reward和terminal状态更新fly_path内的q(s,a):
	if terminal==True or reward==1: #每过一根柱子，or gameover
		for iter,index in enumerate(fly_path):
			i_index = index[0]
			j_index = index[1]
			a_index = index[2]

			#q(s,a) = reward (t) + gamma*reward (t') + gamma^2*reward (t'') + ... where t, t', t'',... corresponding to the time step satisfying the if condition above
				#note: #In definition, t' and t'' should be future time step.
					# But here we apply reward reversely based on lecture notes, i.e. t is current time, t' happens before t, t'' happens before t'.
			states[i_index,j_index,a_index] += reward * pow(gamma,(len(fly_path)-iter-1))


			#safety factor, make all state-value of each action > 0, because we used ratio to determine action=1 or 0 above, and state-value is used to calculate ratio
				#therefore, positive state-value is needed to calculate that ratio
				#therefore, whenever state-value of an action < 0, we can use a small positive number to replace

			if states[i_index,j_index,a_index]<0:
				states[i_index,j_index,a_index]=0.1

		fly_path=[]
		count+=1


	#save states matrix to np file. It can be loaded later on when you want to continue to train RL based on current training results.
	if count%100==99:
		name='training/bird%d.npy'%(count//100)
		np.save(name,states)


	


	
