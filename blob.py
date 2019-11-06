import numpy as np

class Blob():
    def __init__(self, index, contour, minVal, maxVal, center, area):
        self.index = index
        self.contour = contour
        self.minVal = minVal
        self.maxVal = maxVal
        self.center = center
        self.area = area

    def update(self, contour, minVal, maxVal, center, area):
        self.contour = contour
        self.minVal = minVal
        self.maxVal = maxVal
        self.center = center
        self.area = area