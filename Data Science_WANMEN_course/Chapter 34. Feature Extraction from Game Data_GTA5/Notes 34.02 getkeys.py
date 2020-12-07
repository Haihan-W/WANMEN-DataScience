#Purpose of this code:
# Detect what key you press on keyboard when this code is running
# And convert it to user defined Matrix in key_map as output of this code.


# Citation: Box Of Hats (https://github.com/Box-Of-Hats )

import win32api as wapi
from ctypes import *

import time

key_map = {
    'W': [1, 0, 0, 0, 0, 0, 0, 0, 0],
    'S': [0, 1, 0, 0, 0, 0, 0, 0, 0],
    'A': [0, 0, 1, 0, 0, 0, 0, 0, 0],
    'D': [0, 0, 0, 1, 0, 0, 0, 0, 0],
    'WA': [0, 0, 0, 0, 1, 0, 0, 0, 0],
    'WD': [0, 0, 0, 0, 0, 1, 0, 0, 0],
    'SA': [0, 0, 0, 0, 0, 0, 1, 0, 0],
    'SD': [0, 0, 0, 0, 0, 0, 0, 1, 0],
    'NK': [0, 0, 0, 0, 0, 0, 0, 0, 1],
    'default': [0, 0, 0, 0, 0, 0, 0, 0, 0],
}

keyList = ["\b"]
for char in "ABCDEFGHIJKLMNOPQRSTUVWXYZ 123456789,.'£$/\\":
    keyList.append(char)

def keys_to_output(keys):
    '''
    Convert keys to a ...multi-hot... array
     0  1  2  3  4   5   6   7    8
    [W, S, A, D, WA, WD, SA, SD, NOKEY] boolean values.
    improve: we will drop some keys to increse label
    by only check first two input
    '''
    keys_input = ''.join(keys)
    if len(keys_input) > 2:
        keys_input = keys_input[0:2]

    if keys_input in key_map:
        return key_map[keys_input]
    return key_map['default']

def key_check():
    """windows just return latest status in order
    we need to reverse it to make more sense
    """
    keys = []
    for key in keyList:
        if wapi.GetAsyncKeyState(ord(key)):
            keys.append(key)            
    return sorted(keys,reverse=True)  

class POINT(Structure):
    _fields_ = [("x", c_ulong),("y", c_ulong)]

def query_mouse_position():
    pt = POINT()
    windll.user32.GetCursorPos(byref(pt))
    return { "x": pt.x, "y": pt.y} 

def test_key_check():
    while True:
        keys=key_check()
        output=keys_to_output(keys)
        if "T" in keys: #when press "T", then end this code
            print ('Break!',keys)
            print('Break Out!', output)
            break
        else:
            print('Input!',keys)
            print('Input Out!', output)
            time.sleep(1)

if __name__=="__main__":
    test_key_check()