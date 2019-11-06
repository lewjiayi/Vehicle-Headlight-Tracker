import numpy as np

class Blob():
    def __init__(self, index, contour, minVal, maxVal, area):
        self.index = index
        self.contour = contour
        self.minVal = minVal
        self.maxVal = maxVal
        self.width = maxVal[0] - minVal[0]
        self.height = maxVal[1] - minVal[1]
        self.box = [[minVal[0] - 20, minVal[1] - 20],
                    [maxVal[0] + 20, minVal[1] - 20], 
                    [maxVal[0] + 20, maxVal[1] + 20], 
                    [minVal[0] - 20, maxVal[1] + 20]]
        self.area = area
        self.missingCount = 0

    def update(self, contour, minVal, maxVal, area):
        self.contour = contour
        self.minVal = minVal
        self.maxVal = maxVal
        self.width = maxVal[0] - minVal[0]
        self.height = maxVal[1] - minVal[1]
        self.box = [[minVal[0] - 20, minVal[1] - 20],
                    [maxVal[0] + 20, minVal[1] - 20], 
                    [maxVal[0] + 20, maxVal[1] + 20], 
                    [minVal[0] - 20, maxVal[1] + 20]]
        self.area =area

    def missing(self):
        self.missingCount += 1