from base_classes.Environment import Environment
from base_classes.Cell import Cell
from ExportFunctions import ExportFunction, ControlElement
import random

class Simple3DEnvironment(Environment):
    def __init__(self, renderer):
        super().__init__(renderer)

    def _spawnCell(self, xCoordinate, yCoordinate, zCoordinate, newCellBrain):
        for cell in self._cellExecutor.cellList:
            if cell.cellData["xPosition"] == xCoordinate and cell.cellData["yPosition"] == yCoordinate and cell.cellData["zPosition"] == zCoordinate:
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

        for cell in self._cellExecutor.cellList:
            if cell.cellData["xPosition"] == xCoordinate and cell.cellData["yPosition"] == yCoordinate and cell.cellData["zPosition"] == zCoordinate:
                self._cellExecutor.removeCell(cell)
                return

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