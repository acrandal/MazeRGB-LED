#!/usr/bin/env python3
#
# Shows 32x32 logo images from a HUGE dataset!
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
from progress.bar import Bar


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
class DatasetImages:
    def __init__(self, datasetFilenames: List):
        self.datasetFilenames = datasetFilenames
        self.currDatasetImageIndex = 0
        self.datasetImages = []

        self.loadDatasetImages()

    def loadDatasetImages(self):
        for datasetFilename in self.datasetFilenames:
            try:
                print("Loading in dataset file: " + datasetFilename)
                dataDict = self.unpickleFile(datasetFilename)
                self.unpackImages(dataDict)
            except FileNotFoundError as e:
                print(e)
                sys.exit()
    
    def getNextLogoImage(self):
        retImage = self.datasetImages[self.currDatasetImageIndex]
        self.currDatasetImageIndex += 1
        self.currDatasetImageIndex %= len(self.datasetImages)
        return retImage

    def getRandomLogoImage(self):
        return random.choice(self.datasetImages)
    
    def getImage(self, dataDict, imageNumber):
        imgColorsArr = dataDict[b'data'][imageNumber]
        #pprint(imgColorsArr)

        img = Image.new('RGBA', (32,32), color = 'black')
        for arrIndex in range(1024):
            red = imgColorsArr[arrIndex]
            green = imgColorsArr[arrIndex + 1024]
            blue = imgColorsArr[arrIndex + 2048]
            white = 0 

            imageX = arrIndex % 32
            imageY = int(arrIndex / 32)

            img.putpixel((imageX, imageY), (red, green, blue, white))
        return img

    def unpackImages(self, dataDict):
        imagesToLoadCount = 10000
        #progressBar = Bar('Loading Images', max=10000, suffix='%(eta)ds')
        progressBar = Bar('Loading Images', max=imagesToLoadCount, suffix='%(percent).1f%% - %(eta)ds')
        for imageNumber in range(imagesToLoadCount):
            progressBar.next()
            #print(f"\r  Loading image #{imageNumber}", end="")
            currImage = self.getImage(dataDict, imageNumber)
            self.datasetImages.append(currImage)
        print()

    def unpickleFile(self, filename):
        import pickle
        with open(filename, 'rb') as fo:
            dict = pickle.load(fo, encoding='bytes')
        return dict



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
    sleepDelay = 5

    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <logo image file>")
        sys.exit()

    logoFilenames = []
    for filename in sys.argv:
        logoFilenames.append(filename)
    logoFilenames.pop(0)

    logoImages = DatasetImages(logoFilenames)

    rmq = RMQWrapper()

    print("Starting Logo Render")

    try:
        while True:
            #rmq.sendScreenRedraw(logoImages.getNextLogoImage())
            rmq.sendScreenRedraw(logoImages.getRandomLogoImage())
            sleep(sleepDelay)
    except KeyboardInterrupt:
        print("Caught keyboard interrupt - quitting")

    rmq.sendClear()
    rmq.close()

    print("Done.")
