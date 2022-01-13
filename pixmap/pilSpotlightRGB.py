#!/usr/bin/env python3

from PIL import Image
from time import sleep
import random
import pika
import json
from pprint import pprint

minTick = 0.3
sleepDelay = 0.25

xTick = 1.0
yTick = 1.0 

currX = random.randrange(100, 900)
currY = random.randrange(100, 900)

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
def flipDir(tick):
    tick *= -1
    inc = float(random.randrange(-1, 2, 1)) / 10.0

    # Rail. I'm sure there's a better way to do this concisely
    if tick < 0.0:
        if (tick + inc) < -1.0:
            tick = -1.0
        elif (tick + inc) > -1*(minTick):
            tick = -1*(minTick)
        else:
            tick += inc
    else:
        if (tick + inc) > 1.0:
            tick = 1.0
        elif (tick + inc) < minTick:
            tick = minTick
        else:
            tick += inc

    return tick


# ****************************************************************************
class RMQWrapper():
    def __init__(self):
        self.setupRMQ()

    def setupRMQ(self):
        print("Connecting to RMQ server -- ", end='')
        self.queueName = "MazeScreen"
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queueName)
        print("Connected.")

    def publish(self, msg):
        try:
            self.channel.basic_publish(exchange='', routing_key=self.queueName, body=msg)
        except pika.exceptions.StreamLostError as e:
            pprint(e)
            self.setupRMQ()

    def close(self):
        self.connection.close()

    def sendClear(self):
        dat = {"type": "clear"}
        msg = json.dumps(dat)
        self.publish(msg)

    def sendScreenRedraw(self, screen):
        dat = {
            "type": "redraw",
            "pixels": []
            }

        width, height = screen.size
        for x in range(width):
            for y in range(height):
                r, g, b, a = screen.getpixel((x, y))
                pixel = Pixel(x, y, r, g, b)
                dat["pixels"].append(pixel.getDat())

        msg = json.dumps(dat)
        self.publish(msg)

# ** *************************************************
if __name__ == "__main__":
    print("Starting.")

    rmq = RMQWrapper()


    im = Image.open("place1000x1000.png")
    print(im.format, im.size, im.mode)

    width, height = im.size
    print(width, height)



    screenX = 32
    screenY = 32

    maxX, maxY = im.size


    while True:
        if currX <= 0 or (currX + screenX) >= maxX:
            # print(f"Flip X: {xTick}")
            xTick = flipDir(xTick)
            # print(f"Flip X: {xTick}")
        if currY <= 0 or (currY + screenY) >= maxY:
            # print(f"Flip Y: {yTick}")
            yTick = flipDir(yTick)
            #print(f"Flip Y: {yTick}")

        lastX = currX
        lastY = currY

        currX += xTick
        currY += yTick

        #if int(lastX) == int(currX) and int(lastY) == int(currY):
        #    sleep(sleepDelay)
        #    continue

        # Update screen with new currX & currY
        box = (currX, currY, currX + screenX, currY + screenY)
        region = im.crop(box)

        # Could send message to screen here
        rmq.sendScreenRedraw(region)



        sleep(sleepDelay)


    for y in range(0, height - 32, 32):
        for x in range(width - 32):
            box = (x, y, x + 32, y + 32)
            region = im.crop(box)

            # Now covert to pygame surface image
            mode = region.mode
            size = region.size
            data = region.tobytes()

            py_image = pygame.image.fromstring(data, size, mode)

            #region.save("test.png")

            gameDisplay.blit(py_image, (1,1))
            pygame.display.update()

            sleep(0.05)
    print("Done.")
