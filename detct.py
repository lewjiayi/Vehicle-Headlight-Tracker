import numpy as np
import cv2
from matplotlib import pyplot as pt
import math
from blob import Blob


cap = cv2.VideoCapture('stock_video/Pexels Videos 2053100.mp4')
blobs = []
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
        print("Blob count in this frame")
        print(len(contours))
        updatedBlob = []
        for blob in blobs:
            if blob.missingCount >= 1:
                continue
            badBlob = []
            # Check previous frame blob saved with new frame blob
            for countCnt, cnt in enumerate(contours, start=0):
                isUpdated = False
                low = np.min(np.max(cnt,axis=1),axis=0)
                high = np.max(np.max(cnt,axis=1),axis=0)
                x = high[0] - low[0]
                y = high[1] - low[1]
                # Check if contour is singular point
                if (x == 0) or (y == 0):
                    badBlob.append(countCnt)
                    continue
                elif (abs(x) < 3) or (abs(y) < 3):
                    badBlob.append(countCnt)
                    continue
                # elif (x/y < 0.5) or (x/y > 2):
                #     badBlob.append(countCnt)
                #     continue
                # Check if cnt in range
                if (low[0] not in range(blob.box[0][0], blob.box[1][0]) or
                    high[0] not in range(blob.box[0][0], blob.box[1][0]) or
                    low[1] not in range(blob.box[0][1], blob.box[2][1]) or
                    high[1] not in range(blob.box[0][1], blob.box[2][1])):
                    continue
                ret = cv2.matchShapes(blob.contour, cnt, 2, 0)
                # Check if cnt is similar
                # if ret >= 0.5:
                    # continue
                # Check if cnt moved only by small range
                mBlob = cv2.moments(blob.contour)
                mCnt = cv2.moments(cnt)

                blob.update(cnt, low, high, mCnt)
                updatedBlob.append(blob)
                isUpdated = True
                break
            if isUpdated:
                if (len(contours) > 0):
                    contours = np.delete(contours, countCnt)
            else:
                blob.missing()
            contours = np.delete(contours, badBlob)
        


        print("New blob count in this frame")
        print(len(contours))
        # Add newly detected blob into list
        if (len(contours) > 0):
            for cnt in contours:
                low = np.min(np.max(cnt,axis=1),axis=0)
                high = np.max(np.max(cnt,axis=1),axis=0)
                m = cv2.moments(cnt)
                blobs.append(Blob(len(blobs), cnt, low, high, m))
                updatedBlob.append(Blob(len(blobs)-1, cnt, low, high, m))    

        for blob in updatedBlob:
            cv2.putText(resized, str(blob.index), 
                (int((blob.minVal[0]+blob.maxVal[0])/2), blob.maxVal[1] - 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            # cv2.drawContours(resized, [blob.contour], -1, (0,0,0), 3)
        cv2.rectangle(resized, (blobs[0].box[0][0], blobs[0].box[0][1]), (blobs[0].box[2][0], blobs[0].box[2][1]), (0,0,0), 2)

        cv2.imshow('hsv', resized)
        
    else:
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()