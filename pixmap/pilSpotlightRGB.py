#!/usr/bin/env python3
#
# "Spotlight" over a larger image
#  Shows a small window of a full image
#  Results transmitted via RabbitMQ
#
#  @author Aaron S. Crandall <crandall@gonzaga.edu>
#  @copyright 2022
#

from PIL import Image
from time import sleep
import random
import pika
import json
from pprint import pprint
import sys


# ****************************************************************************
class Pixel:
    def __init__(self, x, y, r, g, b):
        self.x = x
        self.y = y
        self.r = r
        self.g = g
        self.b = b

    def getDat(self) -> dict:
        dat = {
            "coordinate": {"x": self.x, "y": self.y},
            "color": {"r": self.r, "g": self.g, "b": self.b},
        }
        return dat

    def __str__(self) -> str:
        return json.dumps(self.getDat())


# ****************************************************************************
class Spotlight:
    def __init__(self, image: Image, spotlightSizeX: int, spotlightSizeY: int):
        self.image = image
        self.sizeX = spotlightSizeX
        self.sizeY = spotlightSizeY

        print(f"Spotlight on image:")
        print(f"\tImage format: {self.image.format}")
        print(f"\tSize: {self.image.size}")
        print(f"\tMode: {self.image.mode}")

        self.minX = 0
        self.minY = 0

        self.imageWidth, self.imageHeight = self.image.size

        self.maxX = self.imageWidth - self.sizeX
        self.maxY = self.imageHeight - self.sizeY

        self.minTickABSVelocity = 0.3
        self.maxTickABSVelocity = 1.0

        self.xTickVelocity = 1.0
        self.yTickVelocity = 1.0

        self.currX = random.randrange(self.minX, self.maxX)
        self.currY = random.randrange(self.minY, self.maxY)

        print("Spotlight initialized")

    def getSpotlightImage(self) -> Image:
        box = (self.currX, self.currY, self.currX + self.sizeX, self.currY + self.sizeY)
        region = self.image.crop(box)
        return region

    def updateCoordinates(self) -> None:
        self.currX += self.xTickVelocity
        self.currY += self.yTickVelocity

    def calcNewVelocity(self, oldVelocity) -> float:
        velocityChange = float(random.randrange(-1, 2, 1)) / 10.0
        newVelocity = oldVelocity + velocityChange

        direction = -1 if oldVelocity < 0 else 1

        if abs(newVelocity) < self.minTickABSVelocity:
            newVelocity = self.minTickABSVelocity * direction
        elif abs(newVelocity) > self.maxTickABSVelocity:
            newVelocity = self.maxTickABSVelocity * direction
        return newVelocity

    def handleBounce(self) -> None:
        if self.currX <= self.minX:
            self.currX = self.minX
            self.xTickVelocity = abs(self.xTickVelocity)
            self.xTickVelocity = self.calcNewVelocity(self.xTickVelocity)
        elif self.currX >= self.maxX:
            self.currX = self.maxX
            self.xTickVelocity = -1 * abs(self.xTickVelocity)
            self.xTickVelocity = self.calcNewVelocity(self.xTickVelocity)

        if self.currY <= self.minY:
            self.currY = self.minY
            self.yTickVelocity = abs(self.yTickVelocity)
            self.yTickVelocity = self.calcNewVelocity(self.yTickVelocity)
        elif self.currY >= self.maxY:
            self.currY = self.maxY
            self.yTickVelocity = -1 * abs(self.yTickVelocity)
            self.yTickVelocity = self.calcNewVelocity(self.yTickVelocity)

    def isAtEdge(self) -> bool:
        if (
            self.currX <= self.minX
            or self.currX >= self.maxX
            or self.currY <= self.minY
            or self.currY >= self.maxY
        ):
            return True
        else:
            return False

    def tick(self) -> None:
        self.updateCoordinates()
        if self.isAtEdge():
            self.handleBounce()


# ****************************************************************************
class RMQWrapper:
    def __init__(self):
        self.setupRMQ()

    def setupRMQ(self) -> None:
        print("Connecting to RMQ server -- ", end="")
        self.queueName = "MazeScreen"
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host="localhost")
        )
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queueName)
        print("Connected.")

    def publish(self, msg) -> None:
        try:
            self.channel.basic_publish(
                exchange="", routing_key=self.queueName, body=msg
            )
        except pika.exceptions.StreamLostError as e:
            pprint(e)
            self.setupRMQ()

    def close(self) -> None:
        self.connection.close()

    def sendClear(self) -> None:
        dat = {"type": "clear"}
        msg = json.dumps(dat)
        self.publish(msg)

    def sendScreenRedraw(self, screen) -> None:
        dat = {"type": "redraw", "pixels": []}

        width, height = screen.size
        for x in range(width):
            for y in range(height):
                r, g, b, a = screen.getpixel((x, y))
                pixel = Pixel(x, y, r, g, b)
                dat["pixels"].append(pixel.getDat())

        msg = json.dumps(dat)
        self.publish(msg)


# ** *************************************************************************
if __name__ == "__main__":
    print("Starting Spotlight Generator.")
    sleepDelay = 0.25

    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <background image file>")
        sys.exit()

    try:
        fullImage = Image.open(sys.argv[1])
    except FileNotFoundError as e:
        print(e)
        sys.exit()

    rmq = RMQWrapper()
    spotlight = Spotlight(fullImage, 32, 32)

    print("Starting spotlight's main movement")

    try:
        while True:
            spotlight.tick()
            newSpotlightImage = spotlight.getSpotlightImage()
            rmq.sendScreenRedraw(newSpotlightImage)
            sleep(sleepDelay)
    except KeyboardInterrupt:
        print("Caught keyboard interrupt - quitting")

    rmq.sendClear()
    rmq.close()

    print("Done.")
