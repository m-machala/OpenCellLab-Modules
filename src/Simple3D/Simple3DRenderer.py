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
        screenCenterX = outputBaseWidth / 2
        screenCenterY = outputBaseHeight / 2

        self._currentFrame = time.perf_counter()
        self._processMovement()
        self._lastFrame = self._currentFrame

        fov_rad = np.radians(self._FOV)
        if fov_rad <= 0 or fov_rad >= np.pi:
            focal_mult = 1.0
        else:
            tan_half_fov = np.tan(fov_rad / 2)
            focal_mult = outputBaseWidth / (2 * tan_half_fov)

        if not cell3DList:
            outputImage = Image.new("RGB", (outputBaseWidth, outputBaseHeight), color=self._backgroundColor)
            buffer = BytesIO()
            outputImage.save(buffer, format="PNG")
            return buffer.getvalue()

        count = len(cell3DList)
        raw_positions = np.zeros((count, 3))
        colors = np.empty(count, dtype=object)

        for i, cell in enumerate(cell3DList):
            data = cell.cellData
            raw_positions[i] = (data["xPosition"], data["yPosition"], data["zPosition"])
            colors[i] = data["color"]

        diff = np.abs(raw_positions - self._cameraPosition)
        mask = np.all(diff <= self._renderDistance, axis=1)
        
        positions = raw_positions[mask]
        colors = colors[mask]
        
        if len(positions) == 0:
            outputImage = Image.new("RGB", (outputBaseWidth, outputBaseHeight), color=self._backgroundColor)
            buffer = BytesIO()
            outputImage.save(buffer, format="PNG")
            return buffer.getvalue()

        world_verts = positions[:, np.newaxis, :] + cubeVertices[np.newaxis, :, :]
        cam_verts = world_verts - self._cameraPosition
        trans_verts = cam_verts @ self._transformationMatrix
        
        X = trans_verts[..., 0]
        Y = trans_verts[..., 1]
        Z = trans_verts[..., 2]

        Z_safe = np.where(Z <= 0, 0.0001, Z) 
        scale = focal_mult / Z_safe
        screen_X = screenCenterX + X * scale
        screen_Y = screenCenterY + Y * scale

        quad_indices = np.array(cubeQuads)
        Q_X = screen_X[:, quad_indices]
        Q_Y = screen_Y[:, quad_indices]
        Q_Z = Z[:, quad_indices]

        min_z = np.min(Q_Z, axis=2)
        visible_mask = min_z > 0

        V_dist_sq = X**2 + Y**2 + Z**2
        Q_dist_sq = V_dist_sq[:, quad_indices]
        avg_dist_sq = np.mean(Q_dist_sq, axis=2)

        avg_dist_sq[~visible_mask] = np.inf
        sorted_face_indices = np.argsort(avg_dist_sq, axis=1)
        top_3_indices = sorted_face_indices[:, :3]

        row_indices = np.arange(len(positions))[:, np.newaxis]
        chosen_dists = avg_dist_sq[row_indices, top_3_indices]
        valid_final_mask = chosen_dists != np.inf
        flat_valid = valid_final_mask.flatten()

        if not np.any(flat_valid):
            outputImage = Image.new("RGB", (outputBaseWidth, outputBaseHeight), color=self._backgroundColor)
            buffer = BytesIO()
            outputImage.save(buffer, format="PNG")
            return buffer.getvalue()

        flat_X = Q_X[row_indices, top_3_indices].reshape(-1, 4)[flat_valid]
        flat_Y = Q_Y[row_indices, top_3_indices].reshape(-1, 4)[flat_valid]
        flat_dists = chosen_dists.flatten()[flat_valid]
        flat_colors = np.repeat(colors, 3, axis=0)[flat_valid]

        sort_order = np.argsort(flat_dists)[::-1]
        final_X = flat_X[sort_order]
        final_Y = flat_Y[sort_order]
        final_colors = flat_colors[sort_order]

        outputImage = Image.new("RGB", (outputBaseWidth, outputBaseHeight), color=self._backgroundColor)
        outputImageDraw = ImageDraw.Draw(outputImage)

        for i in range(len(final_X)):
            poly = list(zip(final_X[i], final_Y[i]))
            outputImageDraw.polygon(poly, fill=final_colors[i], outline=(0, 0, 0))
        
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