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
        self._cameraMovementSpeed = 1
        self._cameraRotationSpeed = 0.05
        self._renderDistance = 10

        self._movementKeyCounter = 0

        self.test1 = 0
        self.test2 = 0

        self._FOV = 90

        self._exportFunctions = [ExportFunction(self._changeFOV, "FOV", ControlElement.SLIDER, [1, 1799, 900]),
                                 ExportFunction(self._changeMovementSpeed, "Movement speed", ControlElement.SLIDER, [1, 1000, int(self._cameraMovementSpeed * 100)]),
                                 ExportFunction(self._changeRotationSpeed, "Rotation speed", ControlElement.SLIDER, [1, 50, int(self._cameraRotationSpeed * 100)]),
                                 ExportFunction(self._changeRenderDistance, "Render distance", ControlElement.SLIDER, [1, 250, int(self._renderDistance)])]

        self._backgroundColor = (0, 0, 0)

    def render(self, cell3DList):
        pitch, yaw, roll = self._cameraRotation
        self._transformationMatrix = self._getRotationMatrix(pitch, yaw, roll)
        outputBaseWidth = self.outputResolutionW
        outputBaseHeight = self.outputResolutionH

        self._currentFrame = time.perf_counter()
        self._processMovement()
        self._lastFrame = self._currentFrame

        outputImage = Image.new("RGB", (outputBaseWidth, outputBaseHeight), color = self._backgroundColor)
        outputImageDraw = ImageDraw.Draw(outputImage)

        polygons = []
        for cell in cell3DList:
            data = cell.cellData
            xPosition = data["xPosition"]
            yPosition = data["yPosition"]
            zPosition = data["zPosition"]

            if abs(self._cameraPosition[0] - xPosition) > self._renderDistance or abs(self._cameraPosition[1] - yPosition) > self._renderDistance or abs(self._cameraPosition[2] - zPosition) > self._renderDistance:
                continue

            cellPolygons = self._getCubePolygons((data["xPosition"], data["yPosition"], data["zPosition"]), data["color"])
            polygons += cellPolygons

        polygons.sort(reverse=True, key=itemgetter(0))
        
        for polygon in polygons:
            outputImageDraw.polygon(polygon[1], polygon[2], (0, 0, 0))
        
        # Convert PIL image to PNG bytes
        buffer = BytesIO()
        outputImage.save(buffer, format="PNG")
        return buffer.getvalue()

    def _getCubePolygons(self, coordinates, color):
        polygons = []

        screenCenterX = self.outputResolutionW / 2
        screenCenterY = self.outputResolutionH / 2

        transformedVertices = []

        for vertex in cubeVertices:
            x = vertex[0] + coordinates[0] - self._cameraPosition[0]
            y = vertex[1] + coordinates[1] - self._cameraPosition[1]
            z = vertex[2] + coordinates[2] - self._cameraPosition[2]
            vector = np.array([x, y, z])
            transformed = vector @ self._transformationMatrix
            transformedVertices.append(np.asarray(transformed).flatten())

        for quad in cubeQuads:
            polygon = []
            skip = False
            distanceSum = 0

            for vertexIndex in quad:
                x, y, z = transformedVertices[vertexIndex]                

                currentDistance = np.sqrt(x**2 + y**2 + z**2)
                distanceSum += currentDistance

                if z <= 0:
                    skip = True
                    break
                width = self.outputResolutionW / self._getBaseFromAngleAndHeight(self._FOV, z)
                x = screenCenterX + width * x
                y = screenCenterY + width * y

                polygon.append((x, y))
            if not skip:
                averageDistance = distanceSum / len(quad)
                polygons.append([averageDistance, polygon, color])
        
        polygons.sort(key=itemgetter(0))
        if len(polygons) > 3:
            return polygons[:3]
        return polygons
    
    def _getBaseFromAngleAndHeight(self, angle, height):
        if angle >= 180 or angle <= 0:
            return 1
        
        return np.tan(np.radians(angle) / 2) * height * 2

    
    def convertFromImageCoordinates(self, xCoordinate, yCoordinate):
        xFromCenter = xCoordinate - self.outputResolutionW / 2
        yFromCenter = yCoordinate - self.outputResolutionH / 2

        xScaled = xFromCenter / (self.outputResolutionW / 2)
        yScaled = yFromCenter / (self.outputResolutionW / 2)

        fov = np.radians(self._FOV)

        cameraX = xScaled * np.tan(fov / 2)
        cameraY = yScaled * np.tan(fov / 2)

        direction = np.array([cameraX, cameraY, 1.0], dtype=float)
        direction = direction / np.linalg.norm(direction)

        pitch, yaw, roll = self._cameraRotation
        rotationMatrix = self._getRotationMatrix(pitch, yaw, roll)
        worldDirection = direction @ rotationMatrix.T
        worldDirection = worldDirection / np.linalg.norm(worldDirection)

        renderDistance = float(self._renderDistance)

        searchStart = (float(self._cameraPosition[0]),
                       float(self._cameraPosition[1]),
                       float(self._cameraPosition[2]))

        voxelX = int(np.floor(searchStart[0] + 0.5))
        voxelY = int(np.floor(searchStart[1] + 0.5))
        voxelZ = int(np.floor(searchStart[2] + 0.5))

        stepX = int(np.sign(worldDirection[0]))
        stepY = int(np.sign(worldDirection[1]))
        stepZ = int(np.sign(worldDirection[2]))

        if stepX > 0:
            boundaryX = voxelX + 0.5
        elif stepX < 0:
            boundaryX = voxelX - 0.5
        else:
            boundaryX = float("inf")

        if stepY > 0:
            boundaryY = voxelY + 0.5
        elif stepY < 0:
            boundaryY = voxelY - 0.5
        else:
            boundaryY = float("inf")

        if stepZ > 0:
            boundaryZ = voxelZ + 0.5
        elif stepZ < 0:
            boundaryZ = voxelZ - 0.5
        else:
            boundaryZ = float("inf")

        if boundaryX is float("inf") or abs(worldDirection[0]) < 1e-12:
            tMaxX = float("inf")
        else:
            tMaxX = (boundaryX - searchStart[0]) / worldDirection[0]

        if boundaryY is float("inf") or abs(worldDirection[1]) < 1e-12:
            tMaxY = float("inf")
        else:
            tMaxY = (boundaryY - searchStart[1]) / worldDirection[1]

        if boundaryZ is float("inf") or abs(worldDirection[2]) < 1e-12:
            tMaxZ = float("inf")
        else:
            tMaxZ = (boundaryZ - searchStart[2]) / worldDirection[2]

        if abs(worldDirection[0]) < 1e-12:
            tDeltaX = float("inf")
        else:
            tDeltaX = abs(1.0 / worldDirection[0])

        if abs(worldDirection[1]) < 1e-12:
            tDeltaY = float("inf")
        else:
            tDeltaY = abs(1.0 / worldDirection[1])

        if abs(worldDirection[2]) < 1e-12:
            tDeltaZ = float("inf")
        else:
            tDeltaZ = abs(1.0 / worldDirection[2])

        foundCoordinates = []
        foundCoordinates.append([voxelX, voxelY, voxelZ, -1])

        t = 0.0
        steps = 0
        maxSteps = int(2 * renderDistance + 1)

        while steps < maxSteps:
            if tMaxX <= tMaxY and tMaxX <= tMaxZ:
                t = tMaxX
                if t > renderDistance:
                    break
                voxelX += stepX
                tMaxX += tDeltaX
            elif tMaxY <= tMaxX and tMaxY <= tMaxZ:
                t = tMaxY
                if t > renderDistance:
                    break
                voxelY += stepY
                tMaxY += tDeltaY
            else:
                t = tMaxZ
                if t > renderDistance:
                    break
                voxelZ += stepZ
                tMaxZ += tDeltaZ

            foundCoordinates.append([voxelX, voxelY, voxelZ, t])
            steps += 1

            if (abs(voxelX - searchStart[0]) > renderDistance or
                abs(voxelY - searchStart[1]) > renderDistance or
                abs(voxelZ - searchStart[2]) > renderDistance):
                break

        foundCoordinates.sort(key=itemgetter(-1))
        return foundCoordinates


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

    def _changeRenderDistance(self, distance):
        self._renderDistance = distance

    def _keyPressed(self, keyName):
        if keyName == "W" or keyName == "A" or keyName == "S" or keyName == "D" or keyName == "Q" or keyName == "E":
            if self._movementKeyCounter == 0:
                self._lastMoved = time.perf_counter()

            self._movementKeyCounter += 1
            self._pressedKeys.add(keyName)

    def _keyReleased(self, keyName):
        if keyName == "W" or keyName == "A" or keyName == "S" or keyName == "D" or keyName == "Q" or keyName == "E":

            if self._movementKeyCounter > 0:
                self._movementKeyCounter -= 1
            self._pressedKeys.remove(keyName)

    def _processMovement(self):
        delta = min(self._currentFrame - self._lastFrame, 0.1)
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
