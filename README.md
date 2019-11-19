# Vehicle-Headlight-Tracker

This is an algorithm that detecte cars on the road using headlights. It detects the lights and pair their movement as moving cars. When light source is not moving for some time, it will be excluded from grouping and treated as background light.

## Instructions

The algorithm output with 2 windows, namely 'Output' and 'Controller'. As the name suggests, the 'Output' window show the result of the processed window while 'Controller' is used to control the variables of algorithm for better performances

The variables of the controller are as below:

1. BGR - HSV

> Toggle between using BGR (Blue Green Red) and HSV (Hue Saturation Value) to detect headlight
> 0: BGR
> 1: HSV
> Default value: HSV
>
> HSV is more sensitive compare to BGR in terms of light, hence, it is generally better than BGR. BGR tends to pick up white pixels as light as well, which leads to low accuracy. At very specific situation, BGR will higher accuracy. So, toggle to BGR setting only when HSV is picking up a lot of errors.

2. BGR Threshold

> Threshold value or simply the brightness to be categorized as light source. The higher the value, the brighter the pixel has to be for the algorithm to pick it up as light source
> Min value: 0
> Max Value: 10
> Default Value: 4
> In HSV mode, this value does not affect the algorithm in any way

3. HSV Threshold

> Threshold value or simply the brightness to be categorized as light source. The higher the value, the brighter the pixel has to be for the algorithm to pick it up as light source
> Min value: 0
> Max Value: 10
> Default Value: 9
> In BGR mode, this value does not affect the algorithm in any way

4. Stablize Display Count

> Toggle to stablize the display of car count. The value changes EVERY FRAME, in 30FPS video you can't see anything, unless you are Superman. When turned on, it simply take display the average count of every few frames
> 0: Off
> 1: On
> Default Value: Off

5. Car Count on Average

> How long you want display of car count to update (per frame)
> Min Value: 0
> Max Value: 10
> Default Value: 5
> When 'Stablize Display Count' is off, this value does not affect the algorithm in any way

6. Resize Value

> Resize the output window, the larger the value, the larger the window size
> Min Value: 0
> Max Value: 10
> Default Value: 7

7. Headlight Min Area in Pixels

> The minimum the area of light needs to be for the algorithm to take it as headlight of a car. The value is given in 10 pixels, i.e. value of the bar at 2 refers to 20 pixels
> Min Value: 0
> Max Value: 10
> Default Value: 5
> Disclaimer: Do NOT attempt to ~~be stupid~~ put the value as 0. If you put the value at 0 and wonder why the algorithm is not detecting any car......... wait for it........ because headlight can be smaller than nothing. Conclusion? Don't put 0!
> Since it is in pixels, if you made the video output way too small by changing the resize value, at the point where all light source are smaller than 10 pixels, nothing will be detected as well

8. Show Blob Detected

> Toggle to show all blobs or the potentials headlight detected. You can use this to view what is being picked up by the algorithm
> 0: Off
> 1: On
> Default Value: Off

9.  Show Cars

> Toggle to show the cars (the numbering and boxes around the headlight pairs)
> 0: Off
> 1: On
> Default Value: On

10.  Car Direction Vertical - Horizontal

> The direction of the car movement. The car could be moving horizontally or vertically in the video, toggle this to change the detection mode
> 0: Vertical
> 1: Horizontal
> Default Value: Vertical

11.  Headlight max horizontal distance
> The horizontal distance between the headlight pair of a car (in pixel).
> Min Value: 0
> Max Value: 10
> Default Value: 5
> The scale of the value changes according to the direction of the car. When the car is moving vertical, per tick on the track bar refers to 40 pixels; while the car is moving horizontal, per tick on the track bar refers to 5 pixels

12.  Headlight max vertical distance
> The vertical distance between the headlight pair of a car (in pixel).
> Min Value: 0
> Max Value: 10
> Default Value: 5
> The scale of the value changes according to the direction of the car. When the car is moving horizontal, per tick on the track bar refers to 40 pixels; while the car is moving vertical, per tick on the track bar refers to 5 pixels

13.  Camera FPS * 10
> The FPS of the camera that captures the video, not the video nor display itself. The higher the FPS of camera, the smaller the distances of the light move from one frame to another. It is used to track the movement of the light. The value per tick in the track bar refer to 10FPS
> Min Value: 0
> Max Value: 5
> Default Value: 3
> Why max value at 50FPS? If the FPS is too high, the light does not seems to move at all from one frame to another, and, I couldn't afford 60FPS camera :( so no one is get to process 60 FPS video

Features to implement

1. Display car detected as average number of few frames fo number dont jump too much
2. Detect non moving object and put black spot on it before drawing contour everytime to prevent lag
3. Movement are checking twice in cnt and cars, should try implement in one loop
4. Car detection range is still hardcoded
5. Bad blob checking area constraint is still hardcoded, can try user input

Constraint

1. atan might have error values
2. HSV too sensitive (reflective) while BGR take in all white cars, bright environment should use HSV while dark environment can use BGR

Note

1. For theta (vector) moving in Q1 and Q3 result in positive while moving in Q2 and Q4 result in negative number
