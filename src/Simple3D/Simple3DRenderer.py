from io import BytesIO
from base_classes.Renderer import Renderer
from ExportFunctions import ExportFunction, ControlElement

from PIL import Image, ImageDraw
import numpy as np
import time
from operator import itemgetter

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

        self._pressedKeys = set()
        self._lastFrame = time.perf_counter()
        self._currentFrame = self._lastFrame 

        self._cameraPosition = np.array([0.0, 0.0, 0.0]) # X, Y, Z
        self._cameraRotation = np.array([0.0, 0.0, 0.0]) # pitch, yaw, roll 
        self._cameraMovementSpeed = 0.25
        self._cameraRotationSpeed = 0.05

        self.test1 = 0
        self.test2 = 0

        self._FOV = 90

        self._exportFunctions = [ExportFunction(self._changeFOV, "FOV", ControlElement.SLIDER, [1, 1799, 900]),
                                 ExportFunction(self._changeMovementSpeed, "Movement speed", ControlElement.SLIDER, [1, 1000, 100]),
                                 ExportFunction(self._changeRotationSpeed, "Rotation speed", ControlElement.SLIDER, [1, 50, 5])]

        self._backgroundColor = (0, 0, 0)

    def render(self, cell3DList):
        outputBaseWidth = self.outputResolutionW
        outputBaseHeight = self.outputResolutionH

        self._currentFrame = time.perf_counter()
        self._processMovement()
        self._lastFrame = self._currentFrame

        outputImage = Image.new("RGB", (outputBaseWidth, outputBaseHeight), color = self._backgroundColor)
        outputImageDraw = ImageDraw.Draw(outputImage)

        testPosition1 = {}
        testPosition1["xPosition"] = 0
        testPosition1["yPosition"] = 0
        testPosition1["zPosition"] = 10
        testPosition1["color"] = (255, 0, 0)

        testPosition2 = {}
        testPosition2["xPosition"] = 1
        testPosition2["yPosition"] = 1
        testPosition2["zPosition"] = 20
        testPosition2["color"] = (0, 255, 0)

        testPosition3 = {}
        testPosition3["xPosition"] = -2
        testPosition3["yPosition"] = 0
        testPosition3["zPosition"] = 30
        testPosition3["color"] = (0, 0, 255)

        testPosition4 = {}
        testPosition4["xPosition"] = 12
        testPosition4["yPosition"] = -4
        testPosition4["zPosition"] = 50
        testPosition4["color"] = (255, 255, 0)

        testPosition5 = {}
        testPosition5["xPosition"] = 48
        testPosition5["yPosition"] = 5
        testPosition5["zPosition"] = 13
        testPosition5["color"] = (0, 255, 255)

        testPosition6 = {}
        testPosition6["xPosition"] = -5
        testPosition6["yPosition"] = -5
        testPosition6["zPosition"] = 8
        testPosition6["color"] = (255, 0, 255)


        cell3DList = [testPosition1, testPosition2, testPosition3, testPosition4, testPosition5, testPosition6]

        polygons = []
        for cell in cell3DList:
            cellPolygons = self._getCubePolygons((cell["xPosition"], cell["yPosition"], cell["zPosition"]), cell["color"])
            polygons += cellPolygons

        polygons.sort(reverse=True, key=itemgetter(0))
        
        for polygon in polygons:
            outputImageDraw.polygon(polygon[1], polygon[2], polygon[2])
        
        # Convert PIL image to PNG bytes
        buffer = BytesIO()
        outputImage.save(buffer, format="PNG")
        return buffer.getvalue()

    def _getCubePolygons(self, coordinates, color):
        polygons = []
        
        screenCenterX = self.outputResolutionW / 2
        screenCenterY = self.outputResolutionH / 2

        for quad in cubeQuads:
            polygon = []
            skip = False
            closestDistance = -1
            for vertexIndex in quad:
                vertex = cubeVertices[vertexIndex]
                x = vertex[0] + coordinates[0] - self._cameraPosition[0]
                y = vertex[1] + coordinates[1] - self._cameraPosition[1]
                z = vertex[2] + coordinates[2] - self._cameraPosition[2]

                currentDistance = np.sqrt(x**2 + y**2 + z**2)
                if currentDistance < closestDistance or closestDistance == -1:
                    closestDistance = currentDistance

                pitch, yaw, roll = self._cameraRotation

                transformationMatrix = self._getRotationMatrix(pitch, yaw, roll)
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
                polygons.append([closestDistance, polygon, color])
        
        return polygons
    
    def _getBaseFromAngleAndHeight(self, angle, height):
        if angle >= 180 or angle <= 0:
            return 1
        
        return np.tan(np.radians(angle) / 2) * height * 2

    
    def convertFromImageCoordinates(self, xCoordinate, yCoordinate):
        pass

    def _primaryDrag(self, originalData, newData):
        rotationVector = [(newData[1] - originalData[1]) / self.outputResolutionH * 75, (originalData[0] - newData[0]) / self.outputResolutionW * 75, 0]
        self._rotateCamera(rotationVector)

    def _moveCamera(self, movementVector):
        pitch, yaw, roll = self._cameraRotation
        rotationMatrix = self._getRotationMatrix(pitch, yaw, roll)
        transformationMatrix = rotationMatrix.T
        vector = np.array(movementVector) * self._cameraMovementSpeed
        transformed = vector @ transformationMatrix
        x, y, z = np.asarray(transformed).flatten()

        self._cameraPosition[0] += x
        self._cameraPosition[1] += y
        self._cameraPosition[2] += z

    def _moveUp(self, multiplier = 1.0):
        self._moveCamera(np.array([0, -1, 0]) * multiplier)

    def _moveDown(self, multiplier = 1.0):
        self._moveCamera(np.array([0, 1, 0])* multiplier)

    def _moveLeft(self, multiplier = 1.0):
        self._moveCamera(np.array([-1, 0, 0]) * multiplier)

    def _moveRight(self, multiplier = 1.0):
        self._moveCamera(np.array([1, 0, 0])* multiplier)

    def _moveBack(self, multiplier = 1.0):
        self._moveCamera(np.array([0, 0, -1]) * multiplier)

    def _moveForward(self, multiplier = 1.0):
        self._moveCamera(np.array([0, 0, 1])* multiplier)

    def _rotateCamera(self, rotationVector):
        scaledVector = np.array(rotationVector) * self._cameraRotationSpeed
        self._cameraRotation += scaledVector

        self._cameraRotation[0] = np.clip(self._cameraRotation[0], -1.570796, 1.570796)

    def _getRotationMatrix(self, pitch, yaw, roll):
        pitchMatrix = np.array([[1, 0, 0],
                                [0, np.cos(pitch), -np.sin(pitch)],
                                [0, np.sin(pitch), np.cos(pitch)]])

        yawMatrix = np.array([[np.cos(yaw), 0, np.sin(yaw)],
                              [0, 1, 0],
                              [-np.sin(yaw), 0, np.cos(yaw)]])

        #rollMatrix = np.array([[np.cos(roll), -np.sin(roll), 0],
        #                       [np.sin(roll),  np.cos(roll), 0],
        #                       [0, 0, 1]])
        
        return yawMatrix @ pitchMatrix #@ rollMatrix

    def _changeFOV(self, FOV):
        self._FOV = FOV / 10

    def _changeMovementSpeed(self, speed):
        self._cameraMovementSpeed = speed / 100

    def _changeRotationSpeed(self, speed):
        self._cameraRotationSpeed = speed / 100

    def _keyPressed(self, keyName):
        if keyName == "W" or keyName == "A" or keyName == "S" or keyName == "D" or keyName == "Q" or keyName == "E":
            self._lastMoved = time.perf_counter()
            self._pressedKeys.add(keyName)

    def _keyReleased(self, keyName):
        if keyName == "W" or keyName == "A" or keyName == "S" or keyName == "D" or keyName == "Q" or keyName == "E":
            self._pressedKeys.remove(keyName)

    def _processMovement(self):
        delta = min(self._currentFrame - self._lastFrame, 0.2)
        delta *= 5

        if "W" in self._pressedKeys:
            self._moveForward(delta)
        
        if "S" in self._pressedKeys:
            self._moveBack(delta)

        if "A" in self._pressedKeys:
            self._moveLeft(delta)

        if "D" in self._pressedKeys:
            self._moveRight(delta)

        if "Q" in self._pressedKeys:
            self._moveUp(delta)

        if "E" in self._pressedKeys:
            self._moveDown(delta)
