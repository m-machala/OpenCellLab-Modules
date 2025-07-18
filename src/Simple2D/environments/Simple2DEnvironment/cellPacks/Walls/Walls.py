from base_classes.CellBrain import CellBrain

class WhiteWall(CellBrain):
    COLOR = (255, 255, 255)

    def run(self):
        pass
        
class GrayWall(CellBrain):
    COLOR = (127, 127, 127)

    def run(self):
        pass