#!/usr/bin/env python3
#
# Shows 32x32 logo images
#
#  @author Aaron S. Crandall <crandall@gonzaga.edu>
#  @copyright 2022
#

from typing import List
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
class LogoImages:
    def __init__(self, logoFilenames: List):
        self.logoFilenames = logoFilenames
        self.currLogoImageIndex = 0
        self.logoImages = []

        self.loadLogoImages()

    def loadLogoImages(self):
        for logoFilename in self.logoFilenames:
            try:
                fullImage = Image.open(logoFilename)
                self.logoImages.append(fullImage)
            except FileNotFoundError as e:
                print(e)
                sys.exit()
    
    def getNextLogoImage(self):
        retImage = self.logoImages[self.currLogoImageIndex]
        self.currLogoImageIndex += 1
        self.currLogoImageIndex %= len(self.logoImages)
        return retImage



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
    print("Starting Logo Renderer.")
    sleepDelay = 1

    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <logo image file>")
        sys.exit()

    logoFilenames = []
    for filename in sys.argv:
        logoFilenames.append(filename)
    logoFilenames.pop(0)

    logoImages = LogoImages(logoFilenames)

    rmq = RMQWrapper()

    print("Starting Logo Render")

    try:
        while True:
            rmq.sendScreenRedraw(logoImages.getNextLogoImage())
            sleep(sleepDelay)
    except KeyboardInterrupt:
        print("Caught keyboard interrupt - quitting")

    rmq.sendClear()
    rmq.close()

    print("Done.")
