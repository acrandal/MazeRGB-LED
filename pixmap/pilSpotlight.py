#!/usr/bin/env python3

from PIL import Image
import pygame
from time import sleep
import random

minTick = 0.3


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


# ** *************************************************
if __name__ == "__main__":
    print("Starting.")

    pygame.init()

    gameDisplay = pygame.display.set_mode((32, 32))

    im = Image.open("place1000x1000.png")
    print(im.format, im.size, im.mode)

    width, height = im.size
    print(width, height)

    xTick = 0.1
    yTick = -1.0


    currX = 900
    currY = 100

    screenX = 32
    screenY = 32

    maxX, maxY = im.size

    sleepDelay = 0.05

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

        if int(lastX) == int(currX) and int(lastY) == int(currY):
            sleep(sleepDelay)
            continue

        # Update screen with new currX & currY
        box = (currX, currY, currX + screenX, currY + screenY)
        region = im.crop(box)

        # Could send message to screen here

        # Now covert to pygame surface image for debug
        mode = region.mode
        size = region.size
        data = region.tobytes()

        py_image = pygame.image.fromstring(data, size, mode)
        gameDisplay.blit(py_image, (1,1))
        pygame.display.update()

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
