#!/usr/bin/env python
# coding:utf-8

# 该代码源自yanpanlau的Keras-FlappyBird，陈晓理做出Keras调用上的相应更新，以便在最新版本上使用
# 申明调包
from __future__ import print_function

import pygame
import argparse
import skimage as skimage # pip install scikit-image
from skimage import transform, color, exposure
from skimage.transform import rotate
from skimage.viewer import ImageViewer
import sys
# sys.path.append("game/")
import wrapped_flappy_bird as game
import random
import numpy as np
from collections import deque #做experience learning/replay
from sys import exit #引入sys中exit函数
from pygame.locals import *

import json
from keras import initializers  # keras 包调用，最新版的名称有变动
from keras.initializers import normal, identity
from keras.models import model_from_json
from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Activation, Flatten
from keras.layers.convolutional import Convolution2D, MaxPooling2D
from keras.optimizers import SGD , Adam
import tensorflow as tf

GAME = 'wanmen_flappy_bird' # 日志文件中游戏的名称
CONFIG = 'nothreshold'
ACTIONS = 2 # 有效动作的数量, fly upward or downward
GAMMA = 0.99 # 衰减速度
OBSERVATION = 5000. # 开始训练前的观测时长 timesteps to observe before training
EXPLORE = 3000000. # frames over which to anneal epsilon
	# 在3000000 loops 之内，把epsilon从initial降到final值 （see section f2.2 in this code)
FINAL_EPSILON = 0.0001 # epsilon的最终值
INITIAL_EPSILON = 0.1 # epsilon的initial值 (note： epsilon usually gradually drops from 1 -> 0, here we initialize it as 0.1, and drop to min 0.0001)
#EPSILON meaning: see notebook section 2. Model-free control -> "Epsilon meaning" section

REPLAY_MEMORY = 50000 # 过往的状态转移数量 for DQN's experience replay
	#here we defined a max length of replay queue size, see section f2.3 in this code.
BATCH = 32 # minibatch批处理的大小 -> for CNN
FRAME_PER_ACTION = 1
LEARNING_RATE = 1e-4

img_rows , img_cols = 80, 80
#Convert image into Black and white
img_channels = 4 # 4幅画面叠在一起进行学习, just an arbitrary number, you can try 5 or 6 or whatever to see which one performs better

######################################
# f1 搭建卷积神经网
def buildmodel():
    # 以下利用卷积神经网
    print("Now we build the model")
    model = Sequential()
    model.add(Convolution2D(32, 8, 8, subsample=(4, 4), border_mode='same',input_shape=(img_rows,img_cols,img_channels)))  #80*80*4
    model.add(Activation('relu')) # ReLU 激活函数
    model.add(Convolution2D(64, 4, 4, subsample=(2, 2), border_mode='same'))
    model.add(Activation('relu')) # ReLU 激活函数
    model.add(Convolution2D(64, 3, 3, subsample=(1, 1), border_mode='same'))
    model.add(Activation('relu')) # ReLU激活函数
    model.add(Flatten())
    model.add(Dense(512))     # fully connected 隐式层
    model.add(Activation('relu')) # ReLU激活函数
    model.add(Dense(2))    # 输出值有两个，向上的动作价值，和向下的动作价值
   
    adam = Adam(lr=LEARNING_RATE) # 优化方法， Adam
    model.compile(loss='mse',optimizer=adam) # Loss function 定义，MSE (误差平方和），使用ADAM进行优化
    print("We finish building the model")
    return model


########################################
# f2 定义训练过程
def trainNetwork(model,args): # 训练强化学习模型

    # 1. 从游戏模拟器中识别游戏状态
    game_state = game.GameState() #flappy bird小游戏的状态

    # 2. 将过去的观察记录保存至队列，用于DQN experience replay
    D = deque()

    #初始化首幅图片，将大小调整为 80x80x4
    	# img_channels = 4 (pre-defined)，so here we need to stack 4 image together as the input to DQN, each image is 80*80 pixel, so input dim is 80x80x4
    do_nothing = np.zeros(ACTIONS)
    do_nothing[0] = 1
    x_t, r_0, terminal = game_state.frame_step(do_nothing)
    	#x_t is image of the game interface

    x_t = skimage.color.rgb2gray(x_t)
    x_t = skimage.transform.resize(x_t,(80,80))
    x_t = skimage.exposure.rescale_intensity(x_t,out_range=(0,255))

    s_t = np.stack((x_t, x_t, x_t, x_t), axis=2) #stack 4 images together
    #print (s_t.shape)

    # 在Keras中，需要注意的是输入张量的形状和维度大小 
    s_t = s_t.reshape(1, s_t.shape[0], s_t.shape[1], s_t.shape[2])  #1*80*80*4

    
    ##############################
    # f0 定义进行(RUN)模式的参数和训练(Train）模式的参数
    if args['mode'] == 'Run':
        OBSERVE = 999999999    # 观测，跑，不训练模型
        epsilon = FINAL_EPSILON
        print ("Now we load weight")
        model.load_weights("model.h5") #if Mode = Run, then use pretrained model to run the program.
        adam = Adam(lr=LEARNING_RATE)
        model.compile(loss='mse',optimizer=adam)
        print ("Weight load successfully")    
    else:                       # Otherwise, training from scratch
        OBSERVE = OBSERVATION  # 如果需要训练模型，那么在观测了OBSERVATION次之后，进行训练
        epsilon = INITIAL_EPSILON

    t = 0

    ################################
    # f2.1游戏控制与强化学习参数更新
    while (True):
        
        for event in pygame.event.get():
            if event.type == QUIT:
                exit()
    	# Initialization for RL
        reward = 0
        loss = 0
        Q_sa = 0 #state-action value
        action_index = 0
        r_t = 0 #reward
        a_t = np.zeros([ACTIONS]) #action
        ################################
        # f2.2 经典的epsilon贪心策略
        if t % FRAME_PER_ACTION == 0:
            if random.random() <= epsilon: #EXPLORE (random)
                print("----------Random Action----------")

                action_index = random.randrange(ACTIONS)
                a_t[action_index] = 1
            else:                         #EXPLOITATION (Greedy)
                q = model.predict(s_t)  # 输入四幅图，出结果
                max_Q = np.argmax(q)
                action_index = max_Q
                a_t[max_Q] = 1

        # After OBSERVE, then 逐渐将epsilon缩小，以求得最大Q 
        	# (please note: we set OBSERVE=5000 which means first 5000 loop, we did not change epsilon, 
        	# to let model observe enough before experience replay and adjusting epsilon)
        if epsilon > FINAL_EPSILON and t > OBSERVE:
            epsilon -= (INITIAL_EPSILON - FINAL_EPSILON) / EXPLORE

        #run the selected action and observed next state and reward
        x_t1_colored, r_t, terminal = game_state.frame_step(a_t)
        	#x_t1_colored is a colored screenshot of game interface

        x_t1 = skimage.color.rgb2gray(x_t1_colored)
        x_t1 = skimage.transform.resize(x_t1,(80,80)) #变换维度大小
        x_t1 = skimage.exposure.rescale_intensity(x_t1, out_range=(0, 255))#

        x_t1 = x_t1.reshape(1, x_t1.shape[0], x_t1.shape[1], 1) #1x80x80x1
        s_t1 = np.append(x_t1, s_t[:, :, :, :3], axis=3) #t=t+1

        # f2.3 积累experience replay, 将状态转移储存到D队列中
        D.append((s_t, action_index, r_t, s_t1, terminal))
        if len(D) > REPLAY_MEMORY:
            D.popleft() #if replay queue's length larger than pre-defined limit, then pop the oldest replay memory to maintain size, i.e. popleft()

        # 观测足够之后，开始训练
        if t > OBSERVE:
            #############################
            # f2.4 minibatch训练
            # sample a minibatch to train on
            minibatch = random.sample(D, BATCH) #从D queue 中随机选取 32 （batch) 个 samples as minibatch, for CNN input
            inputs = np.zeros((BATCH, s_t.shape[1], s_t.shape[2], s_t.shape[3]))   #32, 80, 80, 4; BATCH=32 (pre-defined)
            print (inputs.shape)
            targets = np.zeros((inputs.shape[0], ACTIONS))                         #32, 2

            #Now we do the experience replay
            for i in range(0, len(minibatch)):
                state_t = minibatch[i][0]
                action_t = minibatch[i][1]   #This is action index
                reward_t = minibatch[i][2]
                state_t1 = minibatch[i][3]
                terminal = minibatch[i][4]
                # if terminated, only equals reward

                inputs[i:i + 1] = state_t    #I saved down s_t

                targets[i] = model.predict(state_t)  # Hitting each buttom probability
                Q_sa = model.predict(state_t1)

                if terminal:
                    targets[i, action_t] = reward_t
                else:
                    targets[i, action_t] = reward_t + GAMMA * np.max(Q_sa) #Q-learning formula to update q(s,a), 
                    											# see notebook section 2. Model-free control -> "Summary" section
                    											# Please note: here we did not set alpha, meaning it is 1 here.

            # targets2 = normalize(targets)
            #####################################3
            # f2.5 更新卷积神经网参数，让loss function 最小
            loss += model.train_on_batch(inputs, targets)

        s_t = s_t1
        t = t + 1

        # 每1000次保存训练结果
        if t % 1000 == 0:
            print("Now we save model")
            model.save_weights("model.h5", overwrite=True)
            with open("model.json", "w") as outfile:
                json.dump(model.to_json(), outfile)

        # 输出信息
        state = ""
        if t <= OBSERVE:
            state = "observe"
        elif t > OBSERVE and t <= OBSERVE + EXPLORE:
            state = "explore"
        else:
            state = "train"

        print("TIMESTEPS", t, "/ STATE", state, \
            "/ EPSILON", epsilon, "/ ACTION", action_index, "/ REWARD", r_t, \
            "/ Q_MAX " , np.max(Q_sa), "/ Loss ", loss)

    print("Episode finished!")
    print("************************")

def playGame(args):
    model = buildmodel()
    trainNetwork(model,args)



###############################
# f0 区分训练模式与应用模式
def main():
    parser = argparse.ArgumentParser(description='小游戏')
    parser.add_argument('-m','--mode', help='Train / Run', required=True) 
    	# To run the game, use python qlearn.py -m 'Train' or -m 'Run'
    args = vars(parser.parse_args())
    playGame(args)

if __name__ == "__main__":
    config = tf.compat.v1.ConfigProto()
    config.gpu_options.allow_growth = True
    from tensorflow.python.keras import backend as K
    K.set_session(tf.compat.v1.Session(config=config))
    main()
