import numpy as np

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

    def update(self, contour, minVal, maxVal, center, area):
        self.contour = contour
        self.minVal = minVal
        self.maxVal = maxVal
        self.center = center
        self.existed += 1
        self.area = area
        self.movement.append(center)

    def notACar(self):
        self.isCar = False
