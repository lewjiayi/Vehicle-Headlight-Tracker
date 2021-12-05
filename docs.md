Our system flow is as follows:

![flow](assets/flow.png)

If you have not read the [User Manual](README.md#user-manual), do read it before continue with the content below. It will help you better understand this document.

---

Below is the breakdown of [blob.py](blob.py) class

`index` is an unique id for each blob through out the runtime of the program
`contour` is the current contour of the blob
`minVal` is the lowest Y-axis point of the blob
`maxVal` is the highest Y-axis point of the blob
`center` is the center Y-axis point of the blob
`area` is the size the blob

```py
class Blob():
    def __init__(self, index, contour, minVal, maxVal, center, area):
        self.index = index
        self.contour = contour
        self.minVal = minVal
        self.maxVal = maxVal
        self.center = center
        self.existed = 1
        self.area = area
        self.isCar = True
        self.origin = center
        self.movement = []

```

Update the blob with its latest information

```py
    def update(self, contour, minVal, maxVal, center, area):
        self.contour = contour
        self.minVal = minVal
        self.maxVal = maxVal
        self.center = center
        self.existed += 1
        self.area = area
        self.movement.append(center)
```

Update the blob status as a background light source

```py
    def notACar(self):
        self.isCar = False
```

---

Below is the breakdown of [detect.py](detct.py) code

First, load the video in to the program

``` py
cap = cv2.VideoCapture('video/1.mp4')
```

It follows by defining and initializing some variables and functions

``` py
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

# Initialize Variable
blobs = []
index = 0 # Index for blobs
displayCount = 0 # Count Frames
displayText = 0 # Car Count Display
carCount = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0] # Car count per frame, up to 10 frames
```

Now we create trackbars using opencv GUI to get user input. The spaces is just to make the controller looks more align and nice

```py
# Write instruction on Controller
blank = np.zeros((200, 400), dtype=np.uint8)
instruction1 = "Please read readme.md"
instruction2 = "before tweaking the"
instruction3 = "values below"
cv2.putText(blank, instruction1 ,(10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
cv2.putText(blank, instruction2,(10, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
cv2.putText(blank, instruction3 ,(10, 130), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
# Create track bars
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
```

We are now ready to start the algorithm, initiate the while loop. We run our algorith if there are return value from reading the video, if not, we simply reset the frame

```py
# Start video
while (cap.isOpened()):
    ret, frame = cap.read()
    if ret:
        #Algorithm here
    else:
        # Restart video
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    # Change the number in waitkey brackets to alter play speed, bigger number slower speed
    # 'q' means press q to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
```

Start of the algorithm, it's started with collecting user input. Since most the track bar are are set at scale of 0 to 10. We need to transform the values collected. For BGR, the range of threshold should in between 155 to 255 while HSV is between 245 to 255 since it is more sensitive to light compare to grayscale(BGR). Explaination of others can be found in the instruction of controller

```py
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
```

At image processing prior selection of blobs we direct to BGR or HSV as specified by user. For HSV, we simply extract the V layer and set a threshold on it. As for BGR, we will need to convert it to grayscale to better process the image with only one layer. Since the video usually has high resolution, we need to blur it to increase the accuracy of blob detection using contour.

```py
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
```

Next, we eliminate the blobs we are not interested in, which are, those that are smaller that a given (user input) sizes

```py
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
```

Left with the interest blob, we do a checking and update the blob in order to track them. The blobs list has all the blobs that survived through checking from previous frame whie contours is the current frame blobs. We check blob in blobs one by one with newly drawn contour and update if we found a match. The matching constarint are:

1. Blob is within a close range
2. Difference in area is within 20%

To increase the efficiency of the loop, we skip the rest of the current iteration when a the contour does not survive through a checking. Generally, there are lesser contours within the range compare to the area checking, hence, the range searching is placed earlier. The matched contour will be removed so the algorithm will not run checking redundantly

```py
        missingBlobs = []
        potentialCar = []
        for countBlob, blob in enumerate(blobs, start=0):
            # Check previous frame blob saved with new frame blob
            for countCnt, cnt in enumerate(contours, start=0):
                isUpdated = False
                # Check if blob moved only by small range
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
```

The blobs that did not find a match will be eliminated as it is missing. For the contour that did not made a match, we need to add them in to the blobs list as new blobs for checking on next frame

```py
####### Remove missing blobs #######
        for i in sorted(missingBlobs, reverse=True):
            del blobs[i]
####### Add newly detected blob into list #######
        if (len(contours) > 0):
            for cnt in contours:
                index += 1
                # Determing the lowest and highest point on the Y-axis of the contour
                low = np.min(np.max(cnt,axis=1),axis=0)
                high = np.max(np.max(cnt,axis=1),axis=0)
                # Compute the area of the contour
                area = cv2.contourArea(cnt)
                # Compute the center point ob the Y-axis of the contour
                centerCnt = [(high[0]+low[0])/2, (high[1]+low[1])/2]
                # Create blob object and add into the list
                blobs.append(Blob(index, cnt, low, high, centerCnt, area))
```

Here, we are done with the blobs, we can work on pairing the blobs. We are trying to find matches of blob within the same list, hence there is a nested nested loop. The first loop pick from the start to end and skip the grouped blob. The seconde loop start from the one after first loop and skip blob taht had been grouped.

The checking of constraint is done in the second loop. We start by checking if the blob is within an acceptable range. The search limit is adjustable on the controller panel. Headlights from the same car must be around the same position on the Y-axis, hence, for each adjustment on controller panel, the limit is differ by factor of only 3. For horizontal search limit, the factor is 40.

Then, we check if the blobs are moving in the same direction using simple trigonometry.

For each of the two blob, compare the current and previous position of the blob to identify its latest movement vector. Compute the arc tangent of Y-axis movement over X-axis movement of the two blob `math.atan(y/x)`. This is the method used to calculate the angle of the movement vector but we are utilizing it to identify the direction of the movement.

If the movement of the blob is in Quadrant1 or Quadrant3, then the result above will be positive; if the current position of the blob is in Quadrant2 or Quadrant4, then the result will be negative. With the result compute for both blobs, multiply them together. If the multiplication result is negative, we can be sure that both the blob are moving in different direction. Hence they are not a pair.

For positive result, we have to do a final check to check if they are moving in opposite quadrant. We can simply check the vertical movement direction. By multiplying both vector's vertical movement magnitude, a positive result means they are moving in same vertical direction.

Now if all test are passed, we can group the two blobs together as a car headlight pair.

```py
matched = False
        groupedBlob = []
        cars = [[]]
        for countA, a in enumerate(potentialCar, start=0):
            # Skip blob that had been grouped
            if countA in groupedBlob:
                continue
            if not a.isCar:
                continue
            for countB, b in enumerate(potentialCar[(countA + 1):], start=0):
                # Skip blob that had been grouped
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
                # Check if blob are moving in same direction
                for countM, m in enumerate(blob.movement[-3:], start=0):
                    matched = True
                    # The if else for zero is simply because the start of blob.movement
                    # is the second position instead of its origin
                    if countM == 0:
                        # For theta (vector) movement in Q1 and Q3 result in positive
                        # While moving in Q2 and Q4 result in negative number
                        # If multiplication of two vectors result in negative
                        # They are moving in different direction
                        if (theta(a.origin, a.movement[countM]) *
                            theta(b.origin, b.movement[countM])) < 0:
                            matched = False
                            break
                        # Above only remove the possibility of two adjacent quadrant movement
                        # We still need to check opposite quadrant
                        # This can be achive by checking the vertical movement
                        if ((a.origin[1] - a.movement[countM][1]) *
                            (b.origin[1] - b.movement[countM][1])) < 0:
                            matched = False
                            break
                    else:
                        # SAME AS ABOVE
                        if (theta(a.movement[countM - 1], a.movement[countM]) *
                            theta(b.movement[countM - 1], b.movement[countM])) < 0:
                            matched = False
                            break
                        if ((a.movement[countM - 1][1] - a.movement[countM][1]) *
                            (b.movement[countM - 1][1] - b.movement[countM][1])) < 0:
                            matched = False
                            break
                # It's a match! GROUP EM
                if matched:
                    # GROUPING EM
                    cars.append([a,b])
                    # Append second for loop count is enough, as first loop proceeds on
                    # If you are confused
                    # First loop moved on to next iteration because it din't find a match
                    # So, there's no need to look back to those when look into second loop
                    # If you are STILL confused, just accept the fact that this improve the efficiency of the code
                    groupedBlob.append((countA + countB + 1))
                    break
```
