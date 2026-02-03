from base_classes.Environment import Environment
from base_classes.Cell import Cell
from ExportFunctions import ExportFunction, ControlElement
import random
from collections import defaultdict

class Simple3DEnvironment(Environment):
    def __init__(self, renderer):
        super().__init__(renderer)

        self._cellMap = {}
        self._stepCount = 0
        
        # Spatial Indices for O(1) coordinate lookups
        self._xIndex = defaultdict(set)
        self._yIndex = defaultdict(set)
        self._zIndex = defaultdict(set)

    def _updateCellMap(self, x, y, z, cell = None):
        if cell == None:
            self._cellMap.pop((x, y, z), None)
        else:
            self._cellMap[(x, y, z)] = cell

    def _addToIndices(self, x, y, z, cell):
        self._xIndex[x].add(cell)
        self._yIndex[y].add(cell)
        self._zIndex[z].add(cell)

    def _removeFromIndices(self, x, y, z, cell):
        if cell in self._xIndex[x]: self._xIndex[x].discard(cell)
        if cell in self._yIndex[y]: self._yIndex[y].discard(cell)
        if cell in self._zIndex[z]: self._zIndex[z].discard(cell)

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
        self._removeFromIndices(currentCellX, currentCellY, currentCellZ, currentCell)

    def deleteCurrentSpawnNewCell(self, newCellBrain):
        currentCell = self._cellExecutor.currentCell
        xPosition = currentCell.cellData["xPosition"]
        yPosition = currentCell.cellData["yPosition"]
        zPosition = currentCell.cellData["zPosition"]

        self.deleteCurrentCell()

        self._spawnCell(xPosition, yPosition, zPosition, newCellBrain)

    def _checkArea(self, x1, x2, y1, y2, z1, z2):
        currentCellData = self._cellExecutor.currentCell.cellData
        xPosition = currentCellData["xPosition"]
        yPosition = currentCellData["yPosition"]
        zPosition = currentCellData["zPosition"]

        x1 += xPosition
        x2 += xPosition
        y1 += yPosition
        y2 += yPosition
        z1 += zPosition
        z2 += zPosition

        candidates = None

        if x1 == x2:
            candidates = self._xIndex[x1]
        
        if y1 == y2:
            yCandidates = self._yIndex[y1]
            if candidates is None:
                candidates = yCandidates
            else:
                candidates = candidates.intersection(yCandidates)
                if not candidates: return []

        if z1 == z2:
            zCandidates = self._zIndex[z1]
            if candidates is None:
                candidates = zCandidates
            else:
                candidates = candidates.intersection(zCandidates)
                if not candidates: return []

        if candidates is None:
            candidates = self._cellExecutor.cellList

        foundCells = []

        for cell in candidates:
            cellData = cell.cellData
            if cellData == currentCellData:
                continue

            if min(x1, x2) <= cellData["xPosition"] <= max(x1, x2) and \
               min(y1, y2) <= cellData["yPosition"] <= max(y1, y2) and \
               min(z1, z2) <= cellData["zPosition"] <= max(z1, z2):
                foundCells.append(cell)
        
        return foundCells

    def checkAreaForCells(self, x1, x2, y1, y2, z1, z2):
        foundCells = self._checkArea(x1, x2, y1, y2, z1, z2)
        foundTypes = []
        for cell in foundCells:
            foundType = type(cell.cellBrain)
            if foundType not in foundTypes:
                foundTypes.append(foundType)
        return foundTypes
    
    def checkAreaForTags(self, x1, x2, y1, y2, z1, z2):
        foundCells = self._checkArea(x1, x2, y1, y2, z1, z2)
        foundTags = []

        for cell in foundCells:
            tags = cell.cellData["tags"]
            for tag in tags:
                if tag not in foundTags:
                    foundTags.append(tag)
        return foundTags
    
    def getTagsOfCellsInArea(self, x1, x2, y1, y2, z1, z2):
        foundCells = self._checkArea(x1, x2, y1, y2, z1, z2)
        foundTagsList = []
        for cell in foundCells:
            foundTagsList.append(list(cell.cellData["tags"]))
        return foundTagsList
    
    def addTag(self, tag):
        currentCellData = self._cellExecutor.currentCell.cellData
        if tag not in currentCellData["tags"]:
            currentCellData["tags"].append(tag)

    def removeTag(self, tag):
        currentCellData = self._cellExecutor.currentCell.cellData
        if tag in currentCellData["tags"]:
            currentCellData["tags"].remove(tag)

    def testForTag(self, tag):
        currentCellData = self._cellExecutor.currentCell.cellData
        return tag in currentCellData["tags"]


    def _spawnCell(self, xCoordinate, yCoordinate, zCoordinate, newCellBrain):
        if (xCoordinate, yCoordinate, zCoordinate) in self._cellMap:
            return
            
        newCell = Cell(newCellBrain)
        newCell.cellData["xPosition"] = xCoordinate
        newCell.cellData["yPosition"] = yCoordinate
        newCell.cellData["zPosition"] = zCoordinate
        newCell.cellData["tags"] = []

        if hasattr(type(newCellBrain), "COLOR"):
            newCell.cellData["color"] = type(newCellBrain).COLOR
        else:
            newCell.cellData["color"] = (255, 255, 255)
        
        self._cellExecutor.addCell(newCell)

        self._updateCellMap(xCoordinate, yCoordinate, zCoordinate, newCell)
        self._addToIndices(xCoordinate, yCoordinate, zCoordinate, newCell)

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
            self._removeFromIndices(xCoordinate, yCoordinate, zCoordinate, cell)
        return

    def _executorClearedCells(self):
        self._cellMap = {}
        self._xIndex.clear()
        self._yIndex.clear()
        self._zIndex.clear()

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