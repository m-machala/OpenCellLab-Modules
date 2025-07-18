from base_classes.CellBrain import CellBrain

class Pattern(CellBrain):
    COLOR = (255, 200, 0)
    
    def __init__(self, environment, currentChain = 1, currentNumber = 1, currentDirection = 0):
        super().__init__(environment)
        self.currentChain = currentChain
        self.currentNumber = currentNumber
        self.currentDirection = currentDirection
        self.moved = False
        
    
    def run(self):
        if self.moved:
            return
        directions = [(-1, 0), (0, -1), (1, 0), (0, 1)]
        newChain = self.currentChain
        newNumber = self.currentNumber
        newDirection = self.currentDirection

        if newNumber == newChain:
            newNumber = 0
            newChain += 1
            newDirection = (newDirection + 1) % 4

        newNumber += 1
            
        newCell = Pattern(self._environment, newChain, newNumber, newDirection)
        self._environment.spawnCell(directions[self.currentDirection][0], directions[self.currentDirection][1], newCell)
