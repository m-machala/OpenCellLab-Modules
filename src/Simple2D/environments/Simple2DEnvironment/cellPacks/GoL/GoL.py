from base_classes.CellBrain import CellBrain

class DeadCell(CellBrain):
    COLOR = (0, 64, 255)
    def __init__(self, environment):
        super().__init__(environment)
        self.neighborCount = 2
    def run(self):
        currentStep = self._environment.getCurrentStepNumber() % 3

        if currentStep == 0:
            return
        elif currentStep == 1:
            self.neighborCount = 0
            for xOffset in [-1, 0, 1]:
                for yOffset in [-1, 0, 1]:
                    if xOffset == 0 and yOffset == 0:
                        continue

                    if self._environment.checkIfCellTypeEqual(xOffset, yOffset, AliveCell):
                        self.neighborCount += 1
        else:
            if self.neighborCount == 3:
                self._environment.deleteCurrentSpawnNewCell(AliveCell(self._environment))
            elif self.neighborCount == 0:
                self._environment.deleteCurrentCell()


class AliveCell(CellBrain):
    COLOR = (0, 255, 255)
    def __init__(self, environment):
        super().__init__(environment)
        self.neighborCount = 2
    def run(self):
        currentStep = self._environment.getCurrentStepNumber() % 3

        if currentStep == 0:
            for xOffset in [-1, 0, 1]:
                for yOffset in [-1, 0, 1]:
                    if xOffset == 0 and yOffset == 0:
                        continue
                    self._environment.spawnCell(xOffset, yOffset, DeadCell(self._environment))
        elif currentStep == 1:
            self.neighborCount = 0
            for xOffset in [-1, 0, 1]:
                for yOffset in [-1, 0, 1]:
                    if xOffset == 0 and yOffset == 0:
                        continue
                    
                    if self._environment.checkIfCellTypeEqual(xOffset, yOffset, AliveCell):
                        self.neighborCount += 1
        else:
            if self.neighborCount < 2 or self.neighborCount > 3:
                self._environment.deleteCurrentSpawnNewCell(DeadCell(self._environment))
