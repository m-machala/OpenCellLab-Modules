from io import BytesIO
from PIL import Image, ImageDraw
from base_classes.Renderer import Renderer
from ExportFunctions import ExportFunction, ControlElement
import math

class Simple2DRenderer(Renderer):
    def __init__(self, outputResolutionW, outputResolutionH):
        super().__init__(outputResolutionW, outputResolutionH)
        self._scale = 16
        self._moveSpeed = 1
        self._xCenterPosition = 0
        self._yCenterPosition = 0

        self._exportFunctions = [
            ExportFunction(self._moveUp, "Move up", ControlElement.REPEATINGBUTTON, [10]),
            ExportFunction(self._moveDown, "Move down", ControlElement.REPEATINGBUTTON, [10]),
            ExportFunction(self._moveLeft, "Move left", ControlElement.REPEATINGBUTTON, [10]),
            ExportFunction(self._moveRight, "Move right", ControlElement.REPEATINGBUTTON, [10]),
            ExportFunction(self._zoomIn, "Zoom in", ControlElement.BUTTON),
            ExportFunction(self._zoomOut, "Zoom out", ControlElement.BUTTON),
            ExportFunction(self._setMoveSpeed, "Camera speed", ControlElement.SLIDER, [1, 25, 1])            
        ]

        self._backgroundColor = (0, 0, 0)

    def render(self, simple2DCellList):
        outputBaseWidth = self.outputResolutionW
        outputBaseHeight = self.outputResolutionH

        gridTopBound = self._yCenterPosition - outputBaseHeight / (2 * self._scale)
        gridBottomBound = self._yCenterPosition + outputBaseHeight / (2 * self._scale)
        gridLeftBound = self._xCenterPosition - outputBaseWidth / (2 * self._scale)
        gridRightBound = self._xCenterPosition + outputBaseWidth / (2 * self._scale)

        outputImage = Image.new("RGB", (outputBaseWidth, outputBaseHeight), color = self._backgroundColor)
        outputImageDraw = ImageDraw.Draw(outputImage)
        if outputImageDraw is None:
            return None
        
        for cell in simple2DCellList:
            if gridLeftBound - self._scale <= cell.cellData["xPosition"] <= gridRightBound + self._scale and gridTopBound - self._scale <= cell.cellData["yPosition"] <= gridBottomBound + self._scale:
                topLeftX = min(outputBaseWidth - 1, max(0, math.floor(((cell.cellData["xPosition"] - gridLeftBound) * self._scale))))
                topLeftY = min(outputBaseHeight - 1, max(0, math.floor(((cell.cellData["yPosition"] - gridTopBound) * self._scale))))

                bottomRightX = min(outputBaseWidth - 1, max(0, math.floor(((cell.cellData["xPosition"] - gridLeftBound) * self._scale) + self._scale - 1)))
                bottomRightY = min(outputBaseHeight - 1, max(0, math.floor(((cell.cellData["yPosition"] - gridTopBound) * self._scale) + self._scale - 1)))

                if (topLeftX == bottomRightX or topLeftY == bottomRightY) and self._scale != 1:
                    continue

                if topLeftX > bottomRightX or topLeftY > bottomRightY:
                    continue

                outputImageDraw.rectangle([(topLeftX, topLeftY), (bottomRightX, bottomRightY)], fill = cell.cellData["color"])

        # Convert PIL image to PNG bytes
        buffer = BytesIO()
        outputImage.save(buffer, format="PNG")
        return buffer.getvalue()
    
    def setBackgroundColor(self, colorTuple):
        self._backgroundColor = colorTuple

    def convertFromImageCoordinates(self, xCoordinate, yCoordinate):
        xConverted = math.floor((xCoordinate / self._scale) + (self._xCenterPosition - self.outputResolutionW / (2 * self._scale)))
        yConverted = math.floor((yCoordinate / self._scale) + (self._yCenterPosition - self.outputResolutionH / (2 * self._scale)))
        return [xConverted, yConverted]

    def _moveUp(self):
        self._yCenterPosition -= self._moveSpeed / self._scale

    def _moveDown(self):
        self._yCenterPosition += self._moveSpeed / self._scale

    def _moveLeft(self):
        self._xCenterPosition -= self._moveSpeed / self._scale

    def _moveRight(self):
        self._xCenterPosition += self._moveSpeed / self._scale

    def _zoomIn(self):
        self._scale *= 2
    
    def _zoomOut(self):
        self._scale //= 2
        if self._scale < 1:
            self._scale = 1

    def _setMoveSpeed(self, speed):
        self._moveSpeed = speed

    def _primaryDrag(self, originalData, newData):
        self._xCenterPosition += (originalData[0] - newData[0]) / self._scale
        self._yCenterPosition += (originalData[1] - newData[1]) / self._scale

