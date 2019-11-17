# Vehicle-Headlight-Tracker

Features to implement

1. Display car detected as average number of few frames fo number dont jump too much
2. Detect non moving object and put black spot on it before drawing contour everytime to prevent lag
3. Movement are checking twice in cnt and cars, should try implement in one loop
4. Car detection range is still hardcoded
5. Bad blob checking area constraint is still hardcoded, can try user input

Constraint

1. atan might have error values
2. HSV too sensitive (reflective) while BGR take in all white cars, bright environment should use HSV while dark environment can use BGR
3. User should input speed, depending on fps (used for the range to check light movement)

Note

1. For theta (vector) moving in Q1 and Q3 result in positive while moving in Q2 and Q4 result in negative number
2. Frame size is reduced to 1/4 original size currently, hard coded number might be off
3. Distance def is currently not in used
