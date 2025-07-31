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
        self._cameraRotationMatrix = np.identity(3)  # pitch, yaw, roll 
        self._cameraMovementSpeed = 0.25
        self._cameraRotationSpeed = 0.05

        self.test1 = 0
        self.test2 = 0

        self._FOV = 90

        self._exportFunctions = [ExportFunction(self._moveUp, "Move up", ControlElement.REPEATINGBUTTON, [10]),
                                 ExportFunction(self._moveDown, "Move down", ControlElement.REPEATINGBUTTON, [10]),
                                 ExportFunction(self._moveLeft, "Move left", ControlElement.REPEATINGBUTTON, [10]),
                                 ExportFunction(self._moveRight, "Move right", ControlElement.REPEATINGBUTTON, [10]),
                                 ExportFunction(self._moveForward, "Move forward", ControlElement.REPEATINGBUTTON, [10]),
                                 ExportFunction(self._moveBack, "Move back", ControlElement.REPEATINGBUTTON, [10]),
                                 ExportFunction(self._rotateUp, "Rotate up", ControlElement.REPEATINGBUTTON, [10]),
                                 ExportFunction(self._rotateDown, "Rotate down", ControlElement.REPEATINGBUTTON, [10]),
                                 ExportFunction(self._rotateLeft, "Rotate left", ControlElement.REPEATINGBUTTON, [10]),
                                 ExportFunction(self._rotateRight, "Rotate right", ControlElement.REPEATINGBUTTON, [10]),
                                 ExportFunction(self._rotateClockwise, "Rotate clockwise", ControlElement.REPEATINGBUTTON, [10]),
                                 ExportFunction(self._rotateCounterclockwise, "Rotate counterclockwise", ControlElement.REPEATINGBUTTON, [10]),
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
                x = vertex[0] + coordinates[0] - self._cameraPosition[0]
                y = vertex[1] + coordinates[1] - self._cameraPosition[1]
                z = vertex[2] + coordinates[2] - self._cameraPosition[2]

                transformationMatrix = self._cameraRotationMatrix
                vector = np.array([x, y, z])
                transformed = vector @ transformationMatrix
                x, y, z = np.asarray(transformed).flatten()

                if z <= 0:
                    skip = True
                    break
                width = self.outputResolutionW / self._getBaseFromAngleAndHeight(self._FOV, z)
                x = screenCenterX + width * x
                y = screenCenterY + width * y

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

    def _moveCamera(self, movementVector):

        transformationMatrix = self._cameraRotationMatrix.T
        vector = np.array(movementVector) * self._cameraMovementSpeed
        transformed = vector @ transformationMatrix
        x, y, z = np.asarray(transformed).flatten()

        self._cameraPosition[0] += x
        self._cameraPosition[1] += y
        self._cameraPosition[2] += z

    def _moveUp(self):
        self._moveCamera([0, -1, 0])

    def _moveDown(self):
        self._moveCamera([0, 1, 0])

    def _moveLeft(self):
        self._moveCamera([-1, 0, 0])

    def _moveRight(self):
        self._moveCamera([1, 0, 0])

    def _moveBack(self):
        self._moveCamera([0, 0, -1])

    def _moveForward(self):
        self._moveCamera([0, 0, 1])


    def _rotateCamera(self, rotationVector):
        pitch, yaw, roll = np.array(rotationVector) * self._cameraRotationSpeed

        pitchMatrix = np.array([[1, 0, 0],
                                [0, np.cos(pitch), -np.sin(pitch)],
                                [0, np.sin(pitch), np.cos(pitch)]])

        yawMatrix = np.array([[np.cos(yaw), 0, np.sin(yaw)],
                              [0, 1, 0],
                              [-np.sin(yaw), 0, np.cos(yaw)]])

        rollMatrix = np.array([[np.cos(roll), -np.sin(roll), 0],
                               [np.sin(roll),  np.cos(roll), 0],
                               [0, 0, 1]])

        deltaRotation = yawMatrix @ pitchMatrix @ rollMatrix

        self._cameraRotationMatrix = self._cameraRotationMatrix @ deltaRotation


    def _rotateLeft(self):
        self._rotateCamera([0, -1, 0])

    def _rotateRight(self):
        self._rotateCamera([0, 1, 0])

    def _rotateDown(self):
        self._rotateCamera([-1, 0, 0])

    def _rotateUp(self):
        self._rotateCamera([1, 0, 0])

    def _rotateCounterclockwise(self):
        self._rotateCamera([0, 0, -1])

    def _rotateClockwise(self):
        self._rotateCamera([0, 0, 1])

    def _changeFOV(self, FOV):
        self._FOV = FOV / 10