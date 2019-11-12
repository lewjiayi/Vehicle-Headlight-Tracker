import numpy as np
import cv2
from matplotlib import pyplot as pt
import math
from blob import Blob
from math import atan, sqrt

def distance(start, end):
    x = start[0] - end[0]
    y = start[1] - end[1]
    return sqrt((x*x)+(y*y))

def theta(start, end):
    x = start[0] - end[0]
    y = start[1] - end[1]
    return atan(y/x)

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
        # _, t = cv2.threshold(blur, 240, 255, cv2.THRESH_BINARY)
        # contours, hierarchy = cv2.findContours(t, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # Remove Bad Blod
        badBlob = []
        for countCnt, cnt in enumerate(contours, start=0):
            low = np.min(np.max(cnt,axis=1),axis=0)
            high = np.max(np.max(cnt,axis=1),axis=0)
            x = high[0] - low[0]
            y = high[1] - low[1]
            # if (abs(x) < 3) or (abs(y) < 3):
            #     badBlob.append(countCnt)
            #     continue
            if cv2.contourArea(cnt) < 50:
                badBlob.append(countCnt)
            # elif (x/y < 0.5) or (x/y > 2):
            #     badBlob.append(countCnt)
            #     continue
        contours = np.delete(contours, badBlob)

        # Update Blob movement
        missingBlobs = []
        potentialCar = []

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
            if isUpdated:
                if blob.existed >= 3:
                    potentialCar.append(blob)
                # Remove Matched Contour and flag missing blob
                if (len(contours) > 0):
                    contours = np.delete(contours, countCnt)
                # Check for non-moving blob  
                # Assume 30FPS, 5 second and move less than 50px
                # if (blob.existed > 150):
                #     if ((distance(blob.origin, blob.center)) < 50):
                #         blob.notcar()
##################### DO A CHECKING EVERY 5 SECOND
                    # if not blob.isCar():
                    #     if (blob.existed > 300):
                    #         if ((distance(blob.origin, blob.center)) > 50):
                    #             blob.isACar()
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
        
        matched = False
        groupedBlob = []
        cars = [[]]
        for countA, a in enumerate(potentialCar, start=0):
            if countA in groupedBlob:
                continue
            for countB, b in enumerate(potentialCar[(countA + 1):], start=0):
                if (countA + countB + 1) in groupedBlob:
                    continue
                if (abs(a.center[0] - b.center[0]) > 300):
                        continue
                if (abs(a.center[1] - b.center[1]) > 30):
                        continue
                print("start")
                for countM, m in enumerate(blob.movement[:2], start=0):
                    matched = True
                    if countM == 0:
                        aMovement = [distance(a.origin, a.movement[countM]), theta(a.origin, a.movement[countM])]
                        bMovement = [distance(b.origin, b.movement[countM]), theta(b.origin, b.movement[countM])]
                    else:
                        aMovement = [distance(a.movement[countM - 1], a.movement[countM]), theta(a.movement[countM - 1], a.movement[countM])]
                        bMovement = [distance(b.movement[countM - 1], b.movement[countM]), theta(b.movement[countM - 1], b.movement[countM])]
                    
                    print(a.movement[countM])
                    if (aMovement[0] < 0.8*bMovement[0] or
                        aMovement[0] > 1.2*bMovement[0]):
                        # pass
                        matched = False
                        break
                    # else:
                    #     if (aMovement[1] < 0.8*bMovement[1] or
                    #         aMovement[1] > 1.2*bMovement[1]):
                    #         matched = False
                    #         break
                if matched:
                    cars.append([a,b])
                    groupedBlob.append((countA + countB + 1))
                    break
                    
        for countCar, car in enumerate(cars):
            if car:
                if car[0].minVal[0] > car[1].minVal[0]:
                    minValX = car[1].minVal[0]
                    minValY = car[1].minVal[1]
                else:
                    minValX = car[0].minVal[0]
                    minValY = car[0].minVal[1]
                if car[0].maxVal[0] < car[1].maxVal[0]:
                    maxValX = car[1].maxVal[0]
                    maxValY = car[1].maxVal[1]
                else:
                    maxValX = car[0].maxVal[0]
                    maxValY = car[0].maxVal[1]                
                centerX = (minValX + maxValX)/2
                centerY = (minValY + maxValY)/2
                # cv2.putText(resized, str(countCar),
                #     (int(centerX - 10), int(centerY - 20)),
                #     cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                cv2.rectangle(resized, (minValX, minValY), (maxValX, maxValY), (0,0,0), 2)
        
        text = "Car Detected: " + str(countCar)
        cv2.putText(resized, text,
            (10, 50),
            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                    
        for blob in blobs:
            cv2.putText(resized, str(blob.index),
                (int(blob.center[0] - 10), int(blob.center[1] - 20)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        #     cv2.drawContours(resized, [blob.contour], -1, (0,0,0), 3)
        # cv2.rectangle(resized, (blobs[0].box[0][0], blobs[0].box[0][1]), (blobs[0].box[2][0], blobs[0].box[2][1]), (0,0,0), 2)

        cv2.imshow('hsv', resized)
        
    else:
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()