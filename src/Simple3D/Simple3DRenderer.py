from io import BytesIO
from base_classes.Renderer import Renderer
from ExportFunctions import ExportFunction, ControlElement

from PIL import Image, ImageDraw
import numpy as np

class Simple3DRenderer(Renderer):
    def __init__(self, outputResolutionW, outputResolutionH):
        super().__init__(outputResolutionW, outputResolutionH)

        cameraPosition = [0, 0, 0] # X, Y, Z
        cameraRotation = [0, 0, 0] # roll, pitch, yaw 

        self._exportFunctions = []

        self._backgroundColor = (0, 0, 0)

    def render(self, cell3DList):
        outputBaseWidth = self.outputResolutionW
        outputBaseHeight = self.outputResolutionH

        outputImage = Image.new("RGB", (outputBaseWidth, outputBaseHeight), color = self._backgroundColor)
        outputImageDraw = ImageDraw.Draw(outputImage)

        testPosition1 = {}
        testPosition1["xPosition"] = 50
        testPosition1["yPosition"] = 50
        testPosition1["zPosition"] = 0

        testPosition2 = {}
        testPosition2["xPosition"] = 30
        testPosition2["yPosition"] = 20
        testPosition2["zPosition"] = 0


        cell3DList = [testPosition1, testPosition2]

        for cell in cell3DList:
            outputImageDraw.polygon(self._getCubePolygon((cell["xPosition"], cell["yPosition"], cell["zPosition"])), "blue", "blue")

        # Convert PIL image to PNG bytes
        buffer = BytesIO()
        outputImage.save(buffer, format="PNG")
        return buffer.getvalue()

    def _getCubePolygon(self, coordinates):
        polygon = []
        width = 0.5
        polygon.append((coordinates[0] - width, coordinates[1] - width))
        polygon.append((coordinates[0] + width, coordinates[1] - width))
        polygon.append((coordinates[0] + width, coordinates[1] + width))
        polygon.append((coordinates[0] - width, coordinates[1] + width))

        print(polygon)
        return polygon
    
    def convertFromImageCoordinates(self, xCoordinate, yCoordinate):
        pass