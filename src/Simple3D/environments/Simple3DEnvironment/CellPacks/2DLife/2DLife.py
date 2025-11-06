from base_classes.CellBrain import CellBrain
from enum import Enum

offset = [-1, 0, 1]

class AxisPair(Enum):
    XY = [offset, offset, [0]]
    YZ = [[0], offset, offset]
    ZX = [offset, [0], offset]

class DeadCell(CellBrain):
    COLOR = (0, 64, 255)
    def __init__(self, environment, xy, yz, zx):
        super().__init__(environment)

        self.xy = xy
        self.yz = yz
        self.zx = zx

        self.activeAxis = AxisPair.XY.value if xy else AxisPair.YZ.value if yz else AxisPair.ZX.value if zx else None

        self.neighborCount = 2

    def run(self):
        currentStep = self._environment.getCurrentStepNumber() % 3

        if currentStep == 0:
            return
        elif currentStep == 1:
            pairsToCheck = []
            checkedCoordinates = []
            if self.activeAxis:
                pairsToCheck.append(self.activeAxis)

            self.neighborCount = 0
            for checkedPair in pairsToCheck:
                for x in checkedPair[0]:
                    for y in checkedPair[1]:
                        for z in checkedPair[2]:
                            if x == 0 and y == 0 and z == 0:
                                continue

                            coordinate = (x, y, z)
                            if coordinate in checkedCoordinates:
                                continue
                            checkedCoordinates.append(coordinate)
                            
                            if self._environment.isCellType(x, y, z, AliveCell):
                                self.neighborCount += 1
        else:
            if self.neighborCount == 3:
                self._environment.deleteCurrentSpawnNewCell(AliveCell(self._environment, self.xy, self.yz, self.zx))
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
    def __init__(self, environment, xy, yz, zx):
        super().__init__(environment)

        self.xy = xy
        self.yz = yz
        self.zx = zx

        self.activeAxis = AxisPair.XY.value if xy else AxisPair.YZ.value if yz else AxisPair.ZX.value if zx else None

        self.neighborCount = 2

    def run(self):
        currentStep = self._environment.getCurrentStepNumber() % 3

        if currentStep == 0:
            pairsToSpawn = []
            spawnedCoordinates = []
            if self.activeAxis:
                pairsToSpawn.append(self.activeAxis)

            self.neighborCount = 0
            for checkedPair in pairsToSpawn:
                for x in checkedPair[0]:
                    for y in checkedPair[1]:
                        for z in checkedPair[2]:
                            if x == 0 and y == 0 and z == 0:
                                continue
                            coordinate = (x, y, z)
                            if coordinate in spawnedCoordinates:
                                continue
                            spawnedCoordinates.append(coordinate)
                            
                            self._environment.spawnCell(x, y, z, DeadCell(self._environment, self.xy, self.yz, self.zx))
                            
        elif currentStep == 1:
            pairsToCheck = []
            checkedCoordinates = []
            if self.activeAxis:
                pairsToCheck.append(self.activeAxis)

            self.neighborCount = 0
            for checkedPair in pairsToCheck:
                for x in checkedPair[0]:
                    for y in checkedPair[1]:
                        for z in checkedPair[2]:
                            if x == 0 and y == 0 and z == 0:
                                continue

                            coordinate = (x, y, z)
                            if coordinate in checkedCoordinates:
                                continue
                            checkedCoordinates.append(coordinate)
                            
                            if self._environment.isCellType(x, y, z, AliveCell):
                                self.neighborCount += 1
        else:
            if self.neighborCount < 2 or self.neighborCount > 3:
                self._environment.deleteCurrentSpawnNewCell(DeadCell(self._environment, self.xy, self.yz, self.zx))

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
