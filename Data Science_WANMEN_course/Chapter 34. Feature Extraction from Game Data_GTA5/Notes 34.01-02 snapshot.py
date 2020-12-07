#Purpose of this python code:
# To snapshot a 800*600 size (or user defined size) of screenshot from topleft of the current window
# and save it as an img object

import cv2
import numpy as np
import win32gui, win32ui, win32con, win32api


def grab_screen(region=None):
    hwin = win32gui.GetDesktopWindow() #get current desktop window object (snapshot)
    if region:
            left,top,x2,y2 = region
            width = x2 - left + 1
            height = y2 - top + 1
    else:
        width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
        height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
        left = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
        top = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)

    hwindc = win32gui.GetWindowDC(hwin) #get device context of current desktop window object, e.g. window title...
    srcdc = win32ui.CreateDCFromHandle(hwindc)
    memdc = srcdc.CreateCompatibleDC()
    bmp = win32ui.CreateBitmap()
    bmp.CreateCompatibleBitmap(srcdc, width, height)
    memdc.SelectObject(bmp)
    memdc.BitBlt((0, 0), (width, height), srcdc, (left, top), win32con.SRCCOPY) #(0,0):top left corner is the starting point (coordinate of origin)
    					#width, height: snapshot size, i.e. width, height
    					#SRCCOPY: copy window snapshot object to system memory

    signedIntsArray = bmp.GetBitmapBits(True)
    img = np.fromstring(signedIntsArray, dtype='uint8')
    img.shape = (height,width,4)

    srcdc.DeleteDC()
    memdc.DeleteDC()
    win32gui.ReleaseDC(hwin, hwindc)
    win32gui.DeleteObject(bmp.GetHandle())

    return img #cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

if __name__ == "__main__":
    screen = grab_screen(region=(0,0,800,600)) #0,0 is the top left corner of the screen, as the origin of the region; 800, 600 is the width and height of the region
    cv2.imwrite( "test.jpg", screen )  