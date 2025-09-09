from base_classes.Environment import Environment
from base_classes.Cell import Cell
from ExportFunctions import ExportFunction, ControlElement
import random

class Simple3DEnvironment(Environment):
    def __init__(self, renderer):
        super().__init__(renderer)

    def _spawnCell(self, xCoordinate, yCoordinate, zCoordinate, newCellBrain):
        newCell = Cell(newCellBrain)
        newCell.cellData["xPosition"] = xCoordinate
        newCell.cellData["yPosition"] = yCoordinate
        newCell.cellData["zPosition"] = zCoordinate

        if hasattr(type(newCellBrain), "COLOR"):
            newCell.cellData["color"] = type(newCellBrain).COLOR
        else:
            newCell.cellData["color"] = (255, 255, 255)
        
        self._cellExecutor.addCell(newCell)

    def _addUserCell(self, data):
        xCoordinate = data[0]
        yCoordinate = data[1]
        zCoordinate = data[2]

        cellBrainReference = self._cellExecutor.selectedCellBrainReference
        if cellBrainReference == None:
            return
        
        newCellBrain = cellBrainReference(self)

        self._spawnCell(xCoordinate, yCoordinate, zCoordinate, newCellBrain)


    def _primaryClick(self, data):
        self._addUserCell(data)

    def _primaryDrag(self, originalData, newData):
        self._primaryClick(newData)

