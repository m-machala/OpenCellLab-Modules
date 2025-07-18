from base_classes.CellBrain import CellBrain
import random

class RandomWalk(CellBrain):
    COLOR = (255, 0, 0)

    def __init__(self, environment, previousDirection = 0):
        super().__init__(environment)
        self.walked = False
        self.previousDirection = previousDirection

    def run(self):
        if self.walked:
            return
        
        newDirection = self.previousDirection
        while newDirection == self.previousDirection:
            newDirection = random.randint(0,3)

        newCell = RandomWalk(self._environment, (newDirection + 2) % 4)
        directions = [(-1, 0), (0, -1), (1, 0), (0, 1)]
        direction = directions[newDirection]
        self._environment.spawnCell(direction[0], direction[1], newCell)
        self.walked = True
        