import numpy as np
import cv2
from matplotlib import pyplot as pt
import math
from blob import Blob


cap = cv2.VideoCapture('stock_video/Pexels Videos 2053100.mp4')
blobs = []
index = 0
speed = 20
while (cap.isOpened()):
    ret, frame = cap.read()
    if ret:
        resized = cv2.resize(frame,(int(frame.shape[1]/4), int(frame.shape[0]/4)), fx=0.5, fy=0.5, interpolation=cv2.INTER_LINEAR)
        hsv = cv2.cvtColor(resized, cv2.COLOR_BGR2HSV)
        v = hsv[:,:,2]
        _, t = cv2.threshold(v, 254, 255, cv2.THRESH_BINARY)
        contours, hierarchy = cv2.findContours(t, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        # gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
        # blur = cv2.blur(gray, (5,5))
        # _, t = cv2.threshold(blur, 220, 255, cv2.THRESH_BINARY)
        # contours, hierarchy = cv2.findContours(t, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # Remove Bad Blod
        badBlob = []
        for countCnt, cnt in enumerate(contours, start=0):
            low = np.min(np.max(cnt,axis=1),axis=0)
            high = np.max(np.max(cnt,axis=1),axis=0)
            x = high[0] - low[0]
            y = high[1] - low[1]
            # Check if contour is singular point
            if (x == 0) or (y == 0):
                badBlob.append(countCnt)
            # Check for very small blob
            elif (abs(x) < 3) or (abs(y) < 3):
                badBlob.append(countCnt)
            if cv2.contourArea(cnt) == 0:
                badBlob.append(countCnt)
            # elif (x/y < 0.5) or (x/y > 2):
            #     badBlob.append(countCnt)
            #     continue
            # Check if cnt in range
        contours = np.delete(contours, badBlob)

        # Update Blob movement
        missingBlobs = []
        for countBlob, blob in enumerate(blobs, start=0):
            # Check previous frame blob saved with new frame blob
            for countCnt, cnt in enumerate(contours, start=0):
                isUpdated = False
                # Check if area moved only by small range
                low = np.min(np.max(cnt,axis=1),axis=0)
                high = np.max(np.max(cnt,axis=1),axis=0)
                centerCnt = [(high[0]+low[0])/2, (high[1]+low[1])/2]
                if (abs(centerCnt[0]-blob.center[0]) > speed or
                    abs(centerCnt[1]-blob.center[1]) > speed ):
                    continue
                # Check if cnt is similar
                # ret = cv2.matchShapes(blob.contour, cnt, 2, 0)
                # if ret >= 0.5:
                    # continue
                # Check if area is similar
                areaCnt = cv2.contourArea(cnt)
                if ((blob.area/areaCnt) >= 1.2 or
                    (blob.area/areaCnt) <= 0.8 ):
                    continue
                blob.update(cnt, low, high, centerCnt, areaCnt)
                isUpdated = True
                break
            # Remove Matched Contour and flag missing blob
            if isUpdated:
                if (len(contours) > 0):
                    contours = np.delete(contours, countCnt)
            else:
                missingBlobs.append(countBlob)

        for i in sorted(missingBlobs, reverse=True):
            del blobs[i]
        
        # print("New blob count in this frame")
        # print(len(contours))
        # Add newly detected blob into list
        if (len(contours) > 0):
            for cnt in contours:
                index += 1
                low = np.min(np.max(cnt,axis=1),axis=0)
                high = np.max(np.max(cnt,axis=1),axis=0)
                area = cv2.contourArea(cnt)
                centerCnt = [(high[0]+low[0])/2, (high[1]+low[1])/2]
                blobs.append(Blob(index, cnt, low, high, centerCnt, area))

        for blob in blobs:
            cv2.putText(resized, str(blob.index),
                (int(blob.center[0] - 10), int(blob.center[1] - 20)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            # cv2.drawContours(resized, [blob.contour], -1, (0,0,0), 3)
        # cv2.rectangle(resized, (blobs[0].box[0][0], blobs[0].box[0][1]), (blobs[0].box[2][0], blobs[0].box[2][1]), (0,0,0), 2)

        cv2.imshow('hsv', resized)
        
    else:
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()