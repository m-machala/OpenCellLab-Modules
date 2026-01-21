from base_classes.CellBrain import CellBrain

PLANES = {
    "xy": [(x, y, 0) for x in range(-1, 2) for y in range(-1, 2) if not (x == 0 and y == 0)],
    "yz": [(0, y, z) for y in range(-1, 2) for z in range(-1, 2) if not (y == 0 and z == 0)],
    "zx": [(x, 0, z) for x in range(-1, 2) for z in range(-1, 2) if not (x == 0 and z == 0)]
}

class LifeCell(CellBrain):
    def __init__(self, environment, initialPlanes):
        super().__init__(environment)
        self.initialPlanes = initialPlanes
        self.neighborCount = 0
        self._initialized = False

    def getActivePlanes(self):
        activePlanes = set()

        for plane in PLANES.keys():
            if self._environment.testForTag(plane):
                activePlanes.add(plane)

        x_tags = self._environment.checkAreaForTags(float("-inf"), float("inf"), 0, 0, 0, 0)
        if "anchor" in x_tags:
            if "xy" in x_tags: activePlanes.add("xy")
            if "zx" in x_tags: activePlanes.add("zx")

        y_tags = self._environment.checkAreaForTags(0, 0, float("-inf"), float("inf"), 0, 0)
        if "anchor" in y_tags:
            if "xy" in y_tags: activePlanes.add("xy")
            if "yz" in y_tags: activePlanes.add("yz")

        z_tags = self._environment.checkAreaForTags(0, 0, 0, 0, float("-inf"), float("inf"))
        if "anchor" in z_tags:
            if "yz" in z_tags: activePlanes.add("yz")
            if "zx" in z_tags: activePlanes.add("zx")
        
        return list(activePlanes)

    def run(self):
        if not self._initialized:
            self.initializeTags()
            self._initialized = True

        currentStep = self._environment.getCurrentStepNumber() % 3
        activePlanes = self.getActivePlanes()

        if currentStep == 0:
            self.spawnNeighbors(activePlanes)

        elif currentStep == 1:
            self.neighborCount = 0
            
            uniqueOffsets = set()
            for plane in activePlanes:
                for offset in PLANES[plane]:
                    uniqueOffsets.add(offset)
            
            for dx, dy, dz in uniqueOffsets:
                if self._environment.isCellType(dx, dy, dz, AliveCell):
                    self.neighborCount += 1

        else:
            self.updateState(activePlanes)

    def initializeTags(self):
        for plane in self.initialPlanes:
            self._environment.addTag(plane)

    def spawnNeighbors(self, activePlanes):
        pass

    def updateState(self, activePlanes):
        pass


class AliveCell(LifeCell):
    COLOR = (0, 255, 255)

    def spawnNeighbors(self, activePlanes):
        for plane in activePlanes:
            for dx, dy, dz in PLANES[plane]:
                self._environment.spawnCell(dx, dy, dz, DeadCell(self._environment, [plane]))

    def updateState(self, activePlanes):
        if self.neighborCount < 2 or self.neighborCount > 3:
            self._environment.deleteCurrentSpawnNewCell(DeadCell(self._environment, activePlanes))

class DeadCell(LifeCell):
    COLOR = (0, 64, 255)

    def updateState(self, activePlanes):
        if self.neighborCount == 3:
            self._environment.deleteCurrentSpawnNewCell(AliveCell(self._environment, activePlanes))
        elif self.neighborCount == 0:
            self._environment.deleteCurrentCell()


class AliveAnchor(AliveCell):
    def initializeTags(self):
        super().initializeTags()
        self._environment.addTag("anchor")

    def updateState(self, activePlanes):
        if self.neighborCount < 2 or self.neighborCount > 3:
            self._environment.deleteCurrentSpawnNewCell(DeadAnchor(self._environment, activePlanes))

class DeadAnchor(DeadCell):
    def initializeTags(self):
        super().initializeTags()
        self._environment.addTag("anchor")

    def updateState(self, activePlanes):
        if self.neighborCount == 3:
            self._environment.deleteCurrentSpawnNewCell(AliveAnchor(self._environment, activePlanes))

class AliveXY(AliveCell):
    def __init__(self, environment): super().__init__(environment, ["xy"])

class AliveYZ(AliveCell):
    def __init__(self, environment): super().__init__(environment, ["yz"])

class AliveZX(AliveCell):
    def __init__(self, environment): super().__init__(environment, ["zx"])

class DeadXY(DeadCell):
    def __init__(self, environment): super().__init__(environment, ["xy"])

class DeadYZ(DeadCell):
    def __init__(self, environment): super().__init__(environment, ["yz"])

class DeadZX(DeadCell):
    def __init__(self, environment): super().__init__(environment, ["zx"])

class AnchorXY(AliveAnchor):
    def __init__(self, environment): super().__init__(environment, ["xy"])

class AnchorYZ(AliveAnchor):
    def __init__(self, environment): super().__init__(environment, ["yz"])

class AnchorZX(AliveAnchor):
    def __init__(self, environment): super().__init__(environment, ["zx"])

class AnchorUniversal(AliveAnchor):
    def __init__(self, environment): super().__init__(environment, ["xy", "yz", "zx"])

class DeadAnchorXY(DeadAnchor):
    def __init__(self, environment): super().__init__(environment, ["xy"])

class DeadAnchorYZ(DeadAnchor):
    def __init__(self, environment): super().__init__(environment, ["yz"])

class DeadAnchorZX(DeadAnchor):
    def __init__(self, environment): super().__init__(environment, ["zx"])

class DeadAnchorUniversal(DeadAnchor):
    def __init__(self, environment): super().__init__(environment, ["xy", "yz", "zx"])