from base_classes.CellBrain import CellBrain

class DeadCell(CellBrain):
    COLOR = (0, 64, 255)
    def __init__(self, environment, xAxis, yAxis, zAxis):
        super().__init__(environment)
        self.xOffset = [-1, 0, 1] if xAxis else [0]
        self.yOffset = [-1, 0, 1] if yAxis else [0]
        self.zOffset = [-1, 0, 1] if zAxis else [0]

        self.xAxis = xAxis
        self.yAxis = yAxis
        self.zAxis = zAxis

        self.neighborCount = 2

    def run(self):
        currentStep = self._environment.getCurrentStepNumber() % 3

        if currentStep == 0:
            return
        elif currentStep == 1:
            self.neighborCount = 0
            for x in self.xOffset:
                for y in self.yOffset:
                    for z in self.zOffset:
                        if x == 0 and y == 0 and z == 0:
                            continue

                        if self._environment.isCellType(x, y, z, AliveCell):
                            self.neighborCount += 1
        else:
            if self.neighborCount == 3:
                self._environment.deleteCurrentSpawnNewCell(AliveCell(self._environment, self.xAxis, self.yAxis, self.zAxis))
            elif self.neighborCount == 0:
                self._environment.deleteCurrentCell()

class DeadXY(DeadCell):
    COLOR = (0, 64, 255)

    def __init__(self, environment):
        super().__init__(environment, True, True, False)

class DeadYZ(DeadCell):
    COLOR = (0, 64, 255)

    def __init__(self, environment):
        super().__init__(environment, False, True, True)

class DeadZX(DeadCell):
    COLOR = (0, 64, 255)

    def __init__(self, environment):
        super().__init__(environment, True, False, True)


class AliveCell(CellBrain):
    COLOR = (0, 255, 255)
    def __init__(self, environment, xAxis, yAxis, zAxis):
        super().__init__(environment)
        self.xOffset = [-1, 0, 1] if xAxis else [0]
        self.yOffset = [-1, 0, 1] if yAxis else [0]
        self.zOffset = [-1, 0, 1] if zAxis else [0]
        
        self.xAxis = xAxis
        self.yAxis = yAxis
        self.zAxis = zAxis

        self.neighborCount = 2
    def run(self):
        currentStep = self._environment.getCurrentStepNumber() % 3

        if currentStep == 0:
            for x in self.xOffset:
                for y in self.yOffset:
                    for z in self.zOffset:
                        if x == 0 and y == 0 and z == 0:
                            continue
                        self._environment.spawnCell(x, y, z, DeadCell(self._environment, self.xAxis, self.yAxis, self.zAxis))
        elif currentStep == 1:
            self.neighborCount = 0
            for x in self.xOffset:
                for y in self.yOffset:
                    for z in self.zOffset:
                        if x == 0 and y == 0 and z == 0:
                            continue
                        
                        if self._environment.isCellType(x, y, z, AliveCell):
                            self.neighborCount += 1
        else:
            if self.neighborCount < 2 or self.neighborCount > 3:
                self._environment.deleteCurrentSpawnNewCell(DeadCell(self._environment, self.xAxis, self.yAxis, self.zAxis))

class AliveXY(AliveCell):
    COLOR = (0, 255, 255)

    def __init__(self, environment):
        super().__init__(environment, True, True, False)

class AliveYZ(AliveCell):
    COLOR = (0, 255, 255)

    def __init__(self, environment):
        super().__init__(environment, False, True, True)

class AliveZX(AliveCell):
    COLOR = (0, 255, 255)

    def __init__(self, environment):
        super().__init__(environment, True, False, True)
