from io import BytesIO
from base_classes.Renderer import Renderer
from ExportFunctions import ExportFunction, ControlElement

from PIL import Image, ImageDraw
import numpy as np

halfCubeWidth = 0.5
cubeVertices = np.array([[-halfCubeWidth, -halfCubeWidth, -halfCubeWidth],
                         [ halfCubeWidth, -halfCubeWidth, -halfCubeWidth], 
                         [ halfCubeWidth,  halfCubeWidth, -halfCubeWidth], 
                         [-halfCubeWidth,  halfCubeWidth, -halfCubeWidth],
                         [-halfCubeWidth, -halfCubeWidth,  halfCubeWidth], 
                         [ halfCubeWidth, -halfCubeWidth,  halfCubeWidth], 
                         [ halfCubeWidth,  halfCubeWidth,  halfCubeWidth], 
                         [-halfCubeWidth,  halfCubeWidth,  halfCubeWidth]])

cubeQuads = [[0, 1, 2, 3],
             [4, 5, 6, 7],
             [0, 1, 5, 4],
             [3, 2, 6, 7],
             [0, 3, 7, 4],
             [1, 2, 6, 5],]

class Simple3DRenderer(Renderer):
    def __init__(self, outputResolutionW, outputResolutionH):
        super().__init__(outputResolutionW, outputResolutionH)

        self._cameraPosition = [0.0, 0.0, 0.0] # X, Y, Z
        self._cameraRotation = [0.0, 0.0, 0.0] # roll, pitch, yaw 
        self._cameraMovementSpeed = 0.25

        self.test1 = 0
        self.test2 = 0

        self._FOV = 90

        self._exportFunctions = [ExportFunction(self._moveUp, "Move up", ControlElement.REPEATINGBUTTON, [10]),
                                 ExportFunction(self._moveDown, "Move down", ControlElement.REPEATINGBUTTON, [10]),
                                 ExportFunction(self._moveLeft, "Move left", ControlElement.REPEATINGBUTTON, [10]),
                                 ExportFunction(self._moveRight, "Move right", ControlElement.REPEATINGBUTTON, [10]),
                                 ExportFunction(self._moveForward, "Move forward", ControlElement.REPEATINGBUTTON, [10]),
                                 ExportFunction(self._moveBack, "Move back", ControlElement.REPEATINGBUTTON, [10]),
                                 ExportFunction(self._changeFOV, "FOV", ControlElement.SLIDER, [1, 1799, 900])]

        self._backgroundColor = (0, 0, 0)

    def render(self, cell3DList):
        outputBaseWidth = self.outputResolutionW
        outputBaseHeight = self.outputResolutionH

        outputImage = Image.new("RGB", (outputBaseWidth, outputBaseHeight), color = self._backgroundColor)
        outputImageDraw = ImageDraw.Draw(outputImage)

        testPosition1 = {}
        testPosition1["xPosition"] = 0
        testPosition1["yPosition"] = 0
        testPosition1["zPosition"] = 10

        testPosition2 = {}
        testPosition2["xPosition"] = 1
        testPosition2["yPosition"] = 1
        testPosition2["zPosition"] = 20

        testPosition3 = {}
        testPosition3["xPosition"] = -2
        testPosition3["yPosition"] = 0
        testPosition3["zPosition"] = 30

        testPosition4 = {}
        testPosition4["xPosition"] = 12
        testPosition4["yPosition"] = -4
        testPosition4["zPosition"] = 50

        testPosition5 = {}
        testPosition5["xPosition"] = 48
        testPosition5["yPosition"] = 5
        testPosition5["zPosition"] = 13

        testPosition6 = {}
        testPosition6["xPosition"] = -5
        testPosition6["yPosition"] = -5
        testPosition6["zPosition"] = 8


        cell3DList = [testPosition1, testPosition2, testPosition3, testPosition4, testPosition5, testPosition6]

        for cell in cell3DList:
            polygons = self._getCubePolygons((cell["xPosition"], cell["yPosition"], cell["zPosition"]))
            for polygon in polygons:
                outputImageDraw.polygon(polygon, "blue", "blue")

        # Convert PIL image to PNG bytes
        buffer = BytesIO()
        outputImage.save(buffer, format="PNG")
        return buffer.getvalue()

    def _getCubePolygons(self, coordinates):
        polygons = []
        
        screenCenterX = self.outputResolutionW / 2
        screenCenterY = self.outputResolutionH / 2

        for quad in cubeQuads:
            polygon = []
            skip = False
            for vertexIndex in quad:
                vertex = cubeVertices[vertexIndex]
                distance = vertex[2] + coordinates[2] - self._cameraPosition[2]
                if distance <= 0:
                    skip = True
                    break
                width = self.outputResolutionW / self._getBaseFromAngleAndHeight(self._FOV, distance)
                x = screenCenterX + width * (vertex[0] + coordinates[0] - self._cameraPosition[0])
                y = screenCenterY + width * (vertex[1] + coordinates[1] - self._cameraPosition[1])

                polygon.append((x, y))
            if not skip:
                polygons.append(polygon)
        
        return polygons
    
    def _getBaseFromAngleAndHeight(self, angle, height):
        if angle >= 180 or angle <= 0:
            return 1
        
        return np.tan(np.radians(angle) / 2) * height * 2
    
    def convertFromImageCoordinates(self, xCoordinate, yCoordinate):
        pass

    def _moveDown(self):
        self._cameraPosition[1] -= self._cameraMovementSpeed

    def _moveUp(self):
        self._cameraPosition[1] += self._cameraMovementSpeed

    def _moveLeft(self):
        self._cameraPosition[0] -= self._cameraMovementSpeed

    def _moveRight(self):
        self._cameraPosition[0] += self._cameraMovementSpeed

    def _moveBack(self):
        self._cameraPosition[2] -= self._cameraMovementSpeed

    def _moveForward(self):
        self._cameraPosition[2] += self._cameraMovementSpeed

    def _changeFOV(self, FOV):
        self._FOV = FOV / 10