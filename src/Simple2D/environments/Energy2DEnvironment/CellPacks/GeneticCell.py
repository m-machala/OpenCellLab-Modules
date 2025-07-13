from base_classes.CellBrain import CellBrain
import random

class GeneticCell(CellBrain):
    COLOR = (0, 255, 127)

    def __init__(self, environment, firstGenome = None, secondGenome = None):
        super().__init__(environment)
        genomeSize = 15
        mutationRate = 0.05
        self.genome = []
        if firstGenome != None and secondGenome != None:
            for i in range(genomeSize):
                if len(firstGenome) < i + 1 or len(secondGenome) < i + 1 or random.random() < mutationRate:
                    self.genome.append(random.randint(1, 1000))
                else:
                    self.genome.append(max(0, min(1000, (int(firstGenome[i]), int(secondGenome[i]))[random.randint(0, 1)])))                   
        else:
            for i in range(genomeSize):
                self.genome.append(random.randint(1, 1000))

        self.variable = 200

        self.colorSet = False

    def run(self):
        if not self.colorSet:
            newColor = [0, 0, 0]
            third = len(self.genome) // 3
            for i in range(third):
                newColor[0] += self.genome[i]
                newColor[1] += self.genome[third + i]
                newColor[2] += self.genome[2 * third + i]

            self._environment.changeColor(((int)(newColor[0] / (1000 * third) * 255), (int)(newColor[1] / (1000 * third) * 255), (int)(newColor[2] / (1000 * third) * 255)))
            self.colorSet = True
        i = 0
        while i < len(self.genome):
            currentInstruction = self.genome[i] % 14
            nextNumber = self.genome[(i + 1) % len(self.genome)]
            direction = [[0, 1], [1, 0], [0, -1], [-1, 0]][nextNumber % 4]
            currentEnergy = self._environment.getEnergyLevel()

            if currentInstruction == 1:
                self._environment.rest()
            elif currentInstruction == 2:
                if self.variable > 100:
                    messageMemory = self._environment.getTopMessage()
                    if messageMemory != None:
                        secondGenome = messageMemory
                    else:
                        secondGenome = self.genome
                    newCellBrain = GeneticCell(self._environment, self.genome, secondGenome)
                    self._environment.spawnCell(direction[0], direction[1], newCellBrain)
                    i += 1
                        
            elif currentInstruction == 3:
                self.variable += nextNumber
            elif currentInstruction == 4:
                self.variable -= nextNumber
            elif currentInstruction == 5:
                self.variable += currentEnergy * 10
            elif currentInstruction == 6:
                self.variable -= currentEnergy * 10
            elif currentInstruction == 7:
                self.variable = 0
            elif currentInstruction == 8:
                self._environment.move(direction[0], direction[1])
                i += 1
            elif currentInstruction == 9:
                self._environment.deleteCurrentCell()
            elif currentInstruction == 10:
                if self._environment.checkForCell(direction[0], direction[1]):
                    self.variable += 100
                i += 1
            elif currentInstruction == 11:
                if self.variable > 100:
                    self._environment.sendMessage(direction[0], direction[1], self.genome)
                    i += 1
            elif currentInstruction == 12:
                if self.variable > 0:
                    self._environment.giveEnergy(direction[0], direction[1], 1 / max(1, self.variable))
                    i += 1
            i += 1