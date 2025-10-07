from base_classes.CellBrain import CellBrain

class Virus(CellBrain):
    COLOR = (0, 255, 127)
    spawnCoordinates = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]
    def run(self):
        for coordinate in self.spawnCoordinates:
            newBrain = Virus(self._environment)
            self._environment.spawnCell(coordinate[0], coordinate[1], coordinate[2], newBrain)

        self._environment.deleteCurrentCell()