import numpy as np
import cv2
import math
from blob import Blob

# Load Video
cap = cv2.VideoCapture('stock_video/Pexels Videos 2099536.mp4')

# Define functions
def distance(start, end):
    x = start[0] - end[0]
    y = start[1] - end[1]
    return math.sqrt((x*x)+(y*y))

def theta(start, end):
    x = start[0] - end[0]
    y = start[1] - end[1]
    return math.atan(y/x)

# Trackbar requires an function input
def nothing(x):
    pass

# Track bars
blank = np.zeros((200, 400), dtype=np.uint8)
instruction1 = "Please read readme.md"
instruction2 = "before tweaking the"
instruction3 = "values below"
cv2.putText(blank, instruction1 ,(10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
cv2.putText(blank, instruction2,(10, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
cv2.putText(blank, instruction3 ,(10, 130), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
cv2.namedWindow('Output')
cv2.namedWindow('Controller')
cv2.createTrackbar('BGR - HSV                                                 ', 'Controller',1,1,nothing)
cv2.createTrackbar('BGR Threshold                                    ', 'Controller',4,10,nothing)
cv2.createTrackbar('HSV Threshold                                    ', 'Controller',9,10,nothing)
cv2.createTrackbar('Stablize Display Count                            ', 'Controller',0,1,nothing)
cv2.createTrackbar('Car Count on Average                       ', 'Controller',5,10,nothing)
cv2.createTrackbar('Resize Value                                        ', 'Controller',7,10,nothing)
cv2.createTrackbar('Headlight Min Area in Pixels            ', 'Controller',5,10,nothing)
cv2.createTrackbar('Show Blob Detected                               ', 'Controller',0,1,nothing)
cv2.createTrackbar('Show Cars                                               ', 'Controller',1,1,nothing)
cv2.createTrackbar('Car Direction Vertical - Horizontal      ', 'Controller',0,1,nothing)
cv2.createTrackbar('Headlight max horizontal distance', 'Controller',5,10,nothing)
cv2.createTrackbar('Headlight max vertical distance      ', 'Controller',5,10,nothing)
cv2.createTrackbar('Camera FPS * 10                                   ', 'Controller',3,5,nothing)

# Initialize Variable
blobs = []
index = 0 # Index for blobs
displayCount = 0 # Count Frames
displayText = 0 # Car Count Display
carCount = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0] # Car count per frame, up to 10 frames

# Start video
while (cap.isOpened()):
    ret, frame = cap.read()
    # cap.set(1,200)
    if ret:
        BGR_HSV = cv2.getTrackbarPos('BGR - HSV                                                 ', 'Controller')
        BGRThreshold = (cv2.getTrackbarPos('BGR Threshold                                    ', 'Controller') * 10) + 155
        HSVThreshold = cv2.getTrackbarPos('HSV Threshold                                    ', 'Controller') + 245
        toggleStableCount = cv2.getTrackbarPos('Stablize Display Count                            ', 'Controller')
        stableCountValue = cv2.getTrackbarPos('Car Count on Average                       ', 'Controller')
        resizeValue = 11 - cv2.getTrackbarPos('Resize Value                                        ', 'Controller')
        blobMinSize = (cv2.getTrackbarPos('Headlight Min Area in Pixels            ', 'Controller') * 10) + 1
        showBlob = cv2.getTrackbarPos('Show Blob Detected                               ', 'Controller')
        showCar = cv2.getTrackbarPos('Show Cars                                               ', 'Controller')
        carDirection = cv2.getTrackbarPos('Car Direction Vertical - Horizontal      ', 'Controller')
        carGroupX = cv2.getTrackbarPos('Headlight max horizontal distance', 'Controller')
        carGroupY = cv2.getTrackbarPos('Headlight max vertical distance      ', 'Controller')
        camFPS = (6 - cv2.getTrackbarPos('Camera FPS * 10                                   ', 'Controller')) * 10

        # Resize the video
        resized = cv2.resize(frame,(int(frame.shape[1]/resizeValue), int(frame.shape[0]/resizeValue)), fx=0.5, fy=0.5, interpolation=cv2.INTER_LINEAR)

####### HSV or BGR #######
        if BGR_HSV:
            # HSV alternative code
            hsv = cv2.cvtColor(resized, cv2.COLOR_BGR2HSV)
            # Grab the V layer of HSV
            v = hsv[:,:,2]
            # Set threshold for V value at 254, max values at 255 (python uses 0 - 255 instead of 0 - 100)
            _, t = cv2.threshold(v, HSVThreshold, 255, cv2.THRESH_BINARY)
            contours, hierarchy = cv2.findContours(t, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        else:
            # BGR alternative code
            gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
            blur = cv2.blur(gray, (5,5))
            _, t = cv2.threshold(blur, BGRThreshold, 255, cv2.THRESH_BINARY)
            contours, hierarchy = cv2.findContours(t, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

####### Remove Bad Blob #######
        badBlob = []
        for countCnt, cnt in enumerate(contours, start=0):
            # Get min and max XY coordinates
            # Contours has a weird structure, max at axis = 1 is to extract the list from the structure
            low = np.min(np.max(cnt,axis=1),axis=0)
            high = np.max(np.max(cnt,axis=1),axis=0)
            # Get length and height
            x = high[0] - low[0]
            y = high[1] - low[1]

            # Removing blob smaller than specific sizes
            if cv2.contourArea(cnt) < blobMinSize:
                badBlob.append(countCnt)

        contours = np.delete(contours, badBlob)

####### Update Blob movement #######
        missingBlobs = []
        potentialCar = []
        for countBlob, blob in enumerate(blobs, start=0):
            # Check previous frame blob saved with new frame blob
            for countCnt, cnt in enumerate(contours, start=0):
                isUpdated = False
                # Check if area moved only by small range
                low = np.min(np.max(cnt,axis=1),axis=0)
                high = np.max(np.max(cnt,axis=1),axis=0)
                # Get the center of blob
                centerCnt = [(high[0]+low[0])/2, (high[1]+low[1])/2]
                # Check is blob is in range defined by FPS
                if (abs(centerCnt[0]-blob.center[0]) > camFPS or
                    abs(centerCnt[1]-blob.center[1]) > camFPS ):
                    continue

                # Check if area is similar
                areaCnt = cv2.contourArea(cnt)
                # Check the difference in area using ratio
                if ((blob.area/areaCnt) >= 1.2 or
                    (blob.area/areaCnt) <= 0.8 ):
                    continue

                # If the blob survived all the checks above, update its new position
                blob.update(cnt, low, high, centerCnt, areaCnt)
                isUpdated = True
                # Interested blob is found, the loop can be broke
                break
            # If the blob is not missing
            if isUpdated:
                # If it existed for few frames, it can potentially be a car
                if blob.existed >= 3:
                    if blob.existed >= 100:
                        if distance(blob.origin, blob.center) < (max(resized.shape)/20):
                            blob.notACar()
                    if blob.isCar:
                        potentialCar.append(blob)

                # Remove Matched Contour 
                if (len(contours) > 0):
                    contours = np.delete(contours, countCnt)
            
            # If blob does not get updated, it simply is missing, flag it for removal later
            else:
                missingBlobs.append(countBlob)

####### Remove missing blobs #######
        for i in sorted(missingBlobs, reverse=True):
            del blobs[i] 
        
####### Add newly detected blob into list #######
        if (len(contours) > 0):
            for cnt in contours:
                index += 1
                low = np.min(np.max(cnt,axis=1),axis=0)
                high = np.max(np.max(cnt,axis=1),axis=0)
                area = cv2.contourArea(cnt)
                centerCnt = [(high[0]+low[0])/2, (high[1]+low[1])/2]
                blobs.append(Blob(index, cnt, low, high, centerCnt, area))
        
######## Group potential blobs as cars ########
        matched = False
        groupedBlob = []
        cars = [[]]
        for countA, a in enumerate(potentialCar, start=0):
            # Skip grouped blob
            if countA in groupedBlob:
                continue
            if not a.isCar:
                continue
            for countB, b in enumerate(potentialCar[(countA + 1):], start=0):
                # Skip grouped blob
                if (countA + countB + 1) in groupedBlob:
                    continue
                if not b.isCar:
                    continue

                # Check if blob is witin a certain range
                minValX = min(a.minVal[0], b.minVal[0])
                maxValX = max(a.maxVal[0], b.maxVal[0])

                if carDirection:
                    # Set horizontal search limits for blobs
                    if (abs(minValX - maxValX) > (carGroupY * 40)):
                            continue
                    # Set vertical search limits for blobs
                    if (abs(a.center[1] - b.center[1]) > (carGroupX * 3)):
                            continue
                else:
                    # Set horizontal search limits for blobs
                    if (abs(minValX - maxValX) > (carGroupX * 40)):
                            continue
                    # Set vertical search limits for blobs
                    if (abs(a.center[1] - b.center[1]) > (carGroupY * 3)):
                            continue

                # if ((a.area/b.area) >= 1.2 or
                #     (a.area/b.area) <= 0.8 ):
                #     continue

                # Check if blob are moving in same direction
                for countM, m in enumerate(blob.movement[-3:], start=0):
                    matched = True
                    # The if else for zero is simply because I screwed up the blob class structure and too lazy to fix it
                    if countM == 0:
                        # For theta (vector) movement in Q1 and Q3 result in positive while moving in Q2 and Q4 result in negative number
                        # If multiplication of two vectore result in negative, they are moving in different direction
                        if (theta(a.origin, a.movement[countM]) * theta(b.origin, b.movement[countM])) < 0:
                            matched = False
                            break
                        # Above only remove the possibility of two adjacent quadrant movement, we still need to check opposite quadrant
                        # This can be achive by checking the vertical movement
                        if ((a.origin[1] - a.movement[countM][1]) * (b.origin[1] - b.movement[countM][1])) < 0:
                            matched = False
                            break
                    else:
                        # SAME AS ABOVE LOL
                        if (theta(a.movement[countM - 1], a.movement[countM]) * theta(b.movement[countM - 1], b.movement[countM])) < 0:
                            matched = False
                            break
                        if ((a.movement[countM - 1][1] - a.movement[countM][1]) * (b.movement[countM - 1][1] - b.movement[countM][1])) < 0:
                            matched = False
                            break
                        
                # It's a match! GROUP EM
                if matched:
                    # GROUPING EM
                    cars.append([a,b])
                    # Append second for loop count is enough, as first loop proceeds on
                    # If you are confused
                    # First loop moved on to next iteration because it din't find a match, so there's no need to look back to those when look into second loop
                    # If you are STILL confused, just accept the fact that this improve the efficiency of the code
                    groupedBlob.append((countA + countB + 1))
                    break
                    
####### Draw stuff around the car headlights #######
        if showCar:
            for countCar, car in enumerate(cars):
                if car:
                    # Look for borders
                    minValX = min(car[0].minVal[0], car[1].minVal[0])
                    minValY = min(car[0].minVal[1], car[1].minVal[1])
                    maxValX = max(car[0].maxVal[0], car[1].maxVal[0])
                    maxValY = max(car[0].maxVal[1], car[1].maxVal[1])      
                    # Look for center
                    centerX = (minValX + maxValX)/2
                    centerY = (minValY + maxValY)/2
                    # # Draw em
                    cv2.putText(resized, str(countCar),
                        (int(centerX - 10), int(centerY - 20)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    cv2.rectangle(resized, (minValX, minValY), (maxValX, maxValY), (0,0,0), 2)
        
####### Text of cars detected #######     
        carCount.append(countCar)
        carCount.pop(0)
        displayCount += 1
        if toggleStableCount:
            if stableCountValue == 0:
                stableCountValue = 1
            if (displayCount % stableCountValue) == 0:
                carCountSum = 0
                for x in carCount[-stableCountValue:]:
                    carCountSum += x
                displayText = int(carCountSum/stableCountValue)
                if displayText == 0:
                    if not (carCountSum == 0):
                        displayText = 1
                if displayCount >= 1000:
                    displayCount = 0
        else:
            displayText = countCar

        text = "Car Detected: " + str(displayText)
        cv2.putText(resized, text,
            (10, 50),
            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                    
####### Draw blobs #######
        if showBlob:
            for blob in blobs:
                cv2.putText(resized, str(blob.index),
                    (int(blob.center[0] - 10), int(blob.center[1] - 20)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                cv2.drawContours(resized, [blob.contour], -1, (0,0,0), 3)

####### Display results #######
        cv2.imshow('Output', resized)
        cv2.imshow('Controller',blank)
### Restart video ###
    else:
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

### Play video ###
    # Change the number in waitkey brackets to alter play speed, bigger number slower speed
    # 'q' means press q to exit
    if cv2.waitKey() & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()