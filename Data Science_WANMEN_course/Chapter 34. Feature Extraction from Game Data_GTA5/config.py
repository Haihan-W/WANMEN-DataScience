# -*- coding: utf-8; -*-

""" all configuration in one file
Contributor: Angelapper
Python Version: 3.6+
---------

"""

import numpy as np
#game windows size (input of the snapshot)
TOP=400
GAME_WIDTH=800
GAME_HEIGHT=600+25
DELTA_TIME_CONTROL=0.4

#game screenshot size (output: the saved file, here we compressed the input size 800*600 to smaller output size)
WIDTH=480
HEIGHT=270

#training configuration
LR=1e-3
EPOCHS=30

#image recognition
ANGLE_THRESHOLD=45 #unit is degree