from base_classes.Environment import Environment
from base_classes.Cell import Cell
from ExportFunctions import ExportFunction, ControlElement
import random

class Simple3DEnvironment(Environment):
    def __init__(self, renderer):
        super().__init__(renderer)

        self._cellMap = {}
        self._stepCount = 0

    def _updateCellMap(self, x, y, z, cell = None):
        if cell == None:
            self._cellMap.pop((x, y, z), None)
        else:
            self._cellMap[(x, y, z)] = cell

    def getCurrentStepNumber(self):
        return self._stepCount

    def isCellType(self, relativeX, relativeY, relativeZ, cellType):
        currentCell = self._cellExecutor.currentCell
        if not currentCell:
            return None

        absoluteX = relativeX + currentCell.cellData["xPosition"]
        absoluteY = relativeY + currentCell.cellData["yPosition"]
        absoluteZ = relativeZ + currentCell.cellData["zPosition"]

        if (absoluteX, absoluteY, absoluteZ) in self._cellMap:
            return isinstance(self._cellMap[(absoluteX, absoluteY, absoluteZ)].cellBrain, cellType)
        return None
    
    def spawnCell(self, relativeX, relativeY, relativeZ, newCellBrain):
        currentCell = self._cellExecutor.currentCell
        if not currentCell:
            return

        absoluteX = relativeX + currentCell.cellData["xPosition"]
        absoluteY = relativeY + currentCell.cellData["yPosition"]
        absoluteZ = relativeZ + currentCell.cellData["zPosition"]

        self._spawnCell(absoluteX, absoluteY, absoluteZ, newCellBrain)

    def deleteCurrentCell(self):
        currentCell = self._cellExecutor.currentCell
        if currentCell == None:
            return
        
        currentCellX = currentCell.cellData["xPosition"]
        currentCellY = currentCell.cellData["yPosition"]
        currentCellZ = currentCell.cellData["zPosition"]

        self._updateCellMap(currentCellX, currentCellY, currentCellZ)
        self._cellExecutor.removeCell(currentCell)

    def deleteCurrentSpawnNewCell(self, newCellBrain):
        currentCell = self._cellExecutor.currentCell
        xPosition = currentCell.cellData["xPosition"]
        yPosition = currentCell.cellData["yPosition"]
        zPosition = currentCell.cellData["zPosition"]

        self.deleteCurrentCell()

        self._spawnCell(xPosition, yPosition, zPosition, newCellBrain)


    def _spawnCell(self, xCoordinate, yCoordinate, zCoordinate, newCellBrain):
        if (xCoordinate, yCoordinate, zCoordinate) in self._cellMap:
            return
            
        newCell = Cell(newCellBrain)
        newCell.cellData["xPosition"] = xCoordinate
        newCell.cellData["yPosition"] = yCoordinate
        newCell.cellData["zPosition"] = zCoordinate

        if hasattr(type(newCellBrain), "COLOR"):
            newCell.cellData["color"] = type(newCellBrain).COLOR
        else:
            newCell.cellData["color"] = (255, 255, 255)
        
        self._cellExecutor.addCell(newCell)

        self._updateCellMap(xCoordinate, yCoordinate, zCoordinate, newCell)

    def _addUserCell(self, position):
        xCoordinate = position[0]
        yCoordinate = position[1]
        zCoordinate = position[2]

        cellBrainReference = self._cellExecutor.selectedCellBrainReference
        if cellBrainReference == None:
            return
        
        newCellBrain = cellBrainReference(self)

        self._spawnCell(xCoordinate, yCoordinate, zCoordinate, newCellBrain)

    def _removeUserCell(self, position):
        xCoordinate = position[0]
        yCoordinate = position[1]
        zCoordinate = position[2]

        if (xCoordinate, yCoordinate, zCoordinate) in self._cellMap:
            cell = self._cellMap[(xCoordinate, yCoordinate, zCoordinate)]
            self._cellExecutor.removeCell(cell)
            self._updateCellMap(xCoordinate, yCoordinate, zCoordinate)
        return

    def _executorClearedCells(self):
        self._cellMap = {}

    def _cellsCycled(self):
        self._stepCount += 1

    def _primaryClick(self, data):
        found = False
        previousPosition = None
        for position in data:
            for cell in self._cellExecutor.cellList:
                cellData = cell.cellData
                if position[0] == cellData["xPosition"] and position[1] == cellData["yPosition"] and position[2] == cellData["zPosition"]:
                    if position[3] == -1:
                        return
                    found = True
            if found:
                break
            previousPosition = position

        if not found:
            self._addUserCell(data[0])
        else:
            self._addUserCell(previousPosition)

    def _secondaryClick(self, data):
        found = False
        foundPosition = None
        for position in data:
            for cell in self._cellExecutor.cellList:
                cellData = cell.cellData
                if position[0] == cellData["xPosition"] and position[1] == cellData["yPosition"] and position[2] == cellData["zPosition"]:
                    if position[3] == -1:
                        return
                    foundPosition = position
                    found = True
            if found:
                break

        if not found:
            self._removeUserCell(data[0])
        else:
            self._removeUserCell(foundPosition)