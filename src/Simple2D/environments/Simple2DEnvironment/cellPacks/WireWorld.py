from base_classes.CellBrain import CellBrain
import random

class Wire(CellBrain):
    COLOR = (100, 100, 100)

    def __init__(self, environment):
        super().__init__(environment)
        self.neighborCount = 0

    def run(self):
        currentStep = self._environment.getCurrentStepNumber() % 2

        if currentStep == 0:
            self.checkNeighbors()
        else:
            if self.neighborCount < 1 or self.neighborCount > 2:
                return
            
            self._environment.deleteCurrentSpawnNewCell(Head(self._environment))

    def checkNeighbors(self):
        self.neighborCount = 0
        for xOffset in [-1, 0, 1]:
            for yOffset in [-1, 0, 1]:
                if xOffset == 0 and yOffset == 0:
                    continue

                if self._environment.checkIfCellTypeEqual(xOffset, yOffset, Head):
                    self.neighborCount += 1
            

        
class Head(CellBrain):
    COLOR = (255, 255, 0)

    def run(self):
        currentStep = self._environment.getCurrentStepNumber() % 2

        if currentStep == 1:
            self._environment.deleteCurrentSpawnNewCell(Tail(self._environment))

class Tail(CellBrain):
    COLOR = (255, 127, 0)

    def run(self):
        currentStep = self._environment.getCurrentStepNumber() % 2

        if currentStep == 1:
            self._environment.deleteCurrentSpawnNewCell(Wire(self._environment))