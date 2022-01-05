#!/usr/bin/env python3

import random
from time import sleep
import pika
import json
from pprint import pprint


# ****************************************************************************
class Pixel:
    def __init__(self, x, y, r, g, b):
        self.x = x
        self.y = y
        self.r = r
        self.g = g
        self.b = b
    
    def getDat(self):
        dat = {
            "coordinate": {"x": self.x, "y": self.y},
            "color": {"r": self.r, "g": self.g, "b": self.b}
        }
        return dat

    def __str__(self):
        return json.dumps(self.getDat())

# ****************************************************************************
class Color:
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b


# ****************************************************************************
class Cell:
    def __init__(self, color=None):
        self.term = "c"
        self.color = color
        self.age = 0

        if not self.color:
            self.color = Color(random.randrange(255),
                               random.randrange(255),
                               random.randrange(255))

    def __str__(self):
        return self.term

    def isLive(self):
        return False

    def isDead(self):
        return False

    def getColor(self):
        return self.color

    def getOlder(self):
        self.age += 1


class Live(Cell):
    def __init__(self, color=None):
        super().__init__(color)
        self.term = 'x'

    def isLive(self):
        return True


class Dead(Cell):
    def __init__(self, color=None):
        super().__init__(color)
        self.term = ' '

    def isDead(self):
        return True


class World:
    def __init__(self, maxx=32, maxy=32):
        self._maxx = maxx
        self._maxy = maxy
        self._cells = self._createDeadCells()
        self._maxHashes = 10
        self._hashHistory = []
        self._gliderChance = 5

    def _calcHash(self):
        currStr = ""
        for x in range(self._maxx):
            for y in range(self._maxy):
                currStr += str(self._cells[x][y])
        return currStr

    def __str__(self):
        ret = ""
        for y in range(self._maxy):
            ret += "|"
            for x in range(self._maxx):
                ret += str(self._cells[x][y])
            ret += "\n"

        return ret

    def getLiveCount(self):
        count = 0
        for col in self._cells:
            for cell in col:
                if cell.isLive():
                    count += 1
        return count

    def seedRandom(self):
        for x in range(self._maxx):
            for y in range(self._maxy):
                if random.randrange(100) > 90:
                    self._cells[x][y] = Live()

    def _isValidX(self, x):
        if x >= 0 and x < self._maxx:
            return True
        return False

    def _isValidY(self, y):
        if y >= 0 and y < self._maxy:
            return True
        return False

    def _isValidLoc(self, x, y):
        return self._isValidX(x) and self._isValidY(y)


    def _getLiveNeighborCount(self, x, y):
        count = 0
        for xOffset in range(-1, 2, 1):
            for yOffset in range(-1, 2, 1):
                if( xOffset == 0 and yOffset == 0 ):
                    continue
                currX = x + xOffset
                currY = y + yOffset
                if not self._isValidLoc(currX, currY):
                    continue
                if self._cells[currX][currY].isLive():
                    count += 1
        return count
                

    def _createDeadCells(self):
        newCells = []
        for y in range(self._maxy):
            newCol = []
            for x in range(self._maxx):
                newCol.append(Dead())
            newCells.append(newCol)
        return newCells


    def _updateHashHistory(self):
        currHash = self._calcHash()
        self._hashHistory.append(currHash)
        if len(self._hashHistory) > self._maxHashes:
            self._hashHistory.pop(0)


    def getHistoryDiversityScore(self):
        score = 0
        hashes = {}
        for hash in self._hashHistory:
            hashes[hash] = 1
        for key, value in hashes.items():
            score += value
        return score


    def tick(self):
        oldCells = self._cells
        newCells = self._createDeadCells()
        for x in range(self._maxx):
            for y in range(self._maxy):
                neighborCount = self._getLiveNeighborCount(x, y)
                if oldCells[x][y].isLive() and neighborCount in [2, 3]:
                    newCells[x][y] = oldCells[x][y]     # Keep old live cell (inc color!)
                    newCells[x][y].getOlder()           # This cell gets older (for stats & colors)
                elif oldCells[x][y].isDead() and neighborCount == 3:    # Create new cell
                    newCells[x][y] = Live()
        self._cells = newCells

        self._updateHashHistory()


    def injectRandomNewNeighbor(self):
        if self.getLiveCount() < 1:
            return  # No one alive - should reset anyway

        liveLocs = []
        for x in range(self._maxx):
            for y in range(self._maxy):
                if self._cells[x][y].isLive():
                    liveLocs.append((x,y))
        selectedLoc = liveLocs[random.randrange(len(liveLocs))]
        selectedLiveX = selectedLoc[0]
        selectedLiveY = selectedLoc[1]

        neighXOffset = 0
        neighYOffset = 0
        while (neighXOffset == 0 and neighYOffset == 0) or not self._isValidLoc( selectedLiveX + neighXOffset, selectedLiveY + neighYOffset ):
            neighXOffset = random.randint(-1, 1)
            neighYOffset = random.randint(-1, 1)
        selectedNewLiveX = selectedLiveX + neighXOffset
        selectedNewLiveY = selectedLiveY + neighYOffset
        
        # Create new neighbor cell for some fireworks!
        self._cells[selectedNewLiveX][selectedNewLiveY] = Live()

    def _createRandomGlider(self):
        #print("Creating glider!")
        quadrant = random.randrange(4)
        if quadrant == 0:  # upper left
            #print("Upper left!")
            self._cells[1][0] = Live()
            self._cells[2][1] = Live()
            self._cells[0][2] = Live()
            self._cells[1][2] = Live()
            self._cells[2][2] = Live()
        elif quadrant == 1: # upper right
            #print("Upper right!")
            self._cells[self._maxx - 2][0] = Live()
            self._cells[self._maxx - 3][1] = Live()
            self._cells[self._maxx - 3][2] = Live()
            self._cells[self._maxx - 2][2] = Live()
            self._cells[self._maxx - 1][2] = Live()
        elif quadrant == 2: # lower left 
            #print("lower left!")
            self._cells[0][self._maxy - 3] = Live()
            self._cells[1][self._maxy - 3] = Live()
            self._cells[2][self._maxy - 3] = Live()
            self._cells[2][self._maxy - 2] = Live()
            self._cells[1][self._maxy - 1] = Live()
        elif quadrant == 3: # lower left 
            #print("lower right!")
            self._cells[self._maxx - 3][self._maxy - 3] = Live()
            self._cells[self._maxx - 2][self._maxy - 3] = Live()
            self._cells[self._maxx - 1][self._maxy - 3] = Live()
            self._cells[self._maxx - 3][self._maxy - 2] = Live()
            self._cells[self._maxx - 2][self._maxy - 1] = Live()
        #print("Glider created")
        
            


    def handleStuck(self):
        if self.getHistoryDiversityScore() < 3:
            self.injectRandomNewNeighbor()
        if self.getLiveCount() < 2:
            self.seedRandom()
        if self._gliderChance > random.randrange(100):
            # Create a randomly located Glider to smash stuff
            self._createRandomGlider()

    def getScreenCells(self, ulX, ulY, colsX, rowsY):
        screenCells = []
        for y in range(rowsY):
            newCol = []
            for x in range(colsX):
                newCol.append(Dead())
            screenCells.append(newCol)

        for x in range(colsX):
            for y in range(rowsY):
                screenCells[x][y] = self._cells[ulX + x][ulY + y]

        return screenCells



    

# ****************************************************************************
class RMQWrapper():
    def __init__(self):
        print("Connecting to RMQ server -- ", end='')
        self.queueName = "MazeScreen"
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queueName)
        print("Connected.")

    def publish(self, msg):
        self.channel.basic_publish(exchange='', routing_key=self.queueName, body=msg)

    def close(self):
        self.connection.close()

    def sendClear(self):
        dat = {"type": "clear"}
        msg = json.dumps(dat)
        self.publish(msg)

    def sendScreenCells(self, screenCells):
        self.sendClear()
        for x in range(len(screenCells)):
            for y in range(len(screenCells[0])):
                if screenCells[x][y].isLive():
                    cell = screenCells[x][y]
                    color = cell.getColor()
                    pixel = Pixel(x, y, color.r, color.g, color.b)
                    dat = {
                        "type": "drawPixel",
                        "pixel": pixel.getDat()
                    }
                    msg = json.dumps(dat)
                    #print(msg)
                    self.publish(msg)


# ****************************************************************************
def cls():
    print("\n" * 50)


if __name__ == "__main__":
    print("Starting game of life")
    rmq = RMQWrapper()
    rmq.sendClear()

    world = World(maxx=38, maxy=38)
    world.seedRandom()
    while True:
        cls()
        print(world)
        world.tick()
        world.handleStuck()

        screenCells = world.getScreenCells(3, 3, 32, 32)
        rmq.sendScreenCells(screenCells)

        sleep(1)

    print("Game done.")
