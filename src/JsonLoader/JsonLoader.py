import json
from base_classes.Loader import Loader
from base_classes.Cell import Cell


class JsonLoader(Loader):
    def load(self, filePath, cellClasses):
        cells = []
        classNames = []

        for cellClass in cellClasses:
            classNames.append(cellClass.__name__)


        with open(filePath, "r") as file:
            JSON = json.load(file)

            for cellJson in JSON["cells"]:
                if cellJson["class"] in classNames:
                    cellClassReference = cellClasses[classNames.index(cellJson["class"])]
                    if "constructor arguments" in cellJson:
                        cellJson["constructor arguments"]["environment"] = self.environment
                        kwargs = cellJson["constructor arguments"]
                        cell = Cell(cellClassReference(**kwargs))
                    else:
                        cell = Cell(cellClassReference(self.environment))

                    if "data" in cellJson:
                        cell.cellData = cellJson["data"]

                    cells.append(cell)
        
        for cell in cells:
            self.executor.addCell(cell)
        
        self.executor.cellsChangedManually()