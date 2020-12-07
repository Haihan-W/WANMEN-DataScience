#Purpose of this code:
# Utilize snapshot .py and getkeys .py (import those two .py files below)
# and store snapshot and its corresponding keyboard inputs to np format data file
# Here we store 500 data points per file (For this chapter, files were saved at \data folder)

#Also we pre-defined the configuration parameters (e.g. height and width of the input and output snapshot size, ...), from config .py file (see import section below)

import os, time, cv2
import numpy as np
from snapshot import grab_screen
from getkeys import key_check, key_map, keys_to_output
import sys
from config import TOP,GAME_WIDTH, GAME_HEIGHT, WIDTH,HEIGHT,LR,EPOCHS



def get_file_idx(path):
    starting_value = 1
    while True:
        file_name = '{path}/training_data-{idx}.npy'.format(path=path, 
            idx=starting_value)
        if os.path.isfile(file_name):
            print('File exists, moving along', starting_value)
            starting_value += 1
        else:
            print('File does not exist, starting fresh!', starting_value)
            break
    return starting_value 

def main(path):
    print('Please Press T to Start ....!!!')
    while True:
        keys = key_check()
        if 'T' in keys:
            break
        else:
            time.sleep(2)

    training_data = []
    current_idx = get_file_idx(path)

    for i in list(range(4))[::-1]:
        print(i + 1)
        time.sleep(1)

    last_time = time.time()
    paused = False
    
    file_name = '{path}/training_data-{idx}.npy'.format(path=path,
        idx=current_idx)

    print('STARTING!!! training set saving to ',file_name)
    while(True):
        if not paused:
            screen = grab_screen(region = (0, TOP, GAME_WIDTH, GAME_HEIGHT))
            last_time = time.time()
            # resize to something a bit more acceptable for a CNN
            screen = cv2.resize(screen, (WIDTH, HEIGHT))
            # run a color convert:
            screen = cv2.cvtColor(screen, cv2.COLOR_BGR2RGB)
            keys = key_check()
            output = keys_to_output(keys)
            # add more feature, heading
            print("append screen with keys ",output)
            training_data.append([screen,output])

##            print('loop took {} seconds'.format(time.time()-last_time))
            last_time = time.time()

            if len(training_data) % 100 == 0:
                print(len(training_data))
                if len(training_data) == 500: #save 500 data points per file
                    np.save(file_name, training_data)
                    print('SAVED')
                    training_data = []
                    current_idx += 1
                    file_name = '{path}/training_data-{idx}.npy'.format(path=path,
                        idx=current_idx)
                    print("a new training set is created", file_name)

        keys = key_check()
        if 'T' in keys:
            if paused:
                paused = False
                print('Unpaused!')
                time.sleep(1)
            else:
                print('Pausing!')
                paused = True
                time.sleep(1)

if __name__ == "__main__":
   path_to_save = sys.argv[1]
   main(path_to_save)
