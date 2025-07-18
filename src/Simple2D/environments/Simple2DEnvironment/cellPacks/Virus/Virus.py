from base_classes.CellBrain import CellBrain

class Virus(CellBrain):
    COLOR = (0, 255, 127)
    def run(self):
        topCell = Virus(self._environment)
        bottomCell = Virus(self._environment)
        leftCell = Virus(self._environment)
        rightCell = Virus(self._environment)

        self._environment.spawnCell(0, -1, topCell)
        self._environment.spawnCell(0, 1, bottomCell)
        self._environment.spawnCell(-1, 0, leftCell)
        self._environment.spawnCell(1, 0, rightCell)

        self._environment.deleteCurrentCell()
        