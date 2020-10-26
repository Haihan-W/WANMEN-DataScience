import cv2
cap = cv2.VideoCapture('../imgs/kmeans.mp4')

# #在播放每一帧时，使用cv2.waitKey()适当持续时间，一般可以设置25ms

# Check if camera opened successfully
if (cap.isOpened() == False):
    print("Error opening video stream or file")
# Read until video is completed
while(cap.isOpened()):
    # Capture frame-by-frame
    ret, frame = cap.read()
    if ret == True:
        # Display the resulting frame
        cv2.namedWindow("frame", cv2.WINDOW_NORMAL)
        cv2.imshow('frame', frame)

        # Press Q on keyboard to  exit
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break
    # Break the loop
    else:
        break

    i += 1
# When everything done, release the video capture object
cap.release()

# Closes all the frames
cv2.destroyAllWindows()