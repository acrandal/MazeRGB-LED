#!/usr/bin/env python3
from samplebase import SampleBase

from random import randint, uniform
from time import sleep

import pika, os, sys
import json
from pprint import pprint


class Coordinate:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Color:
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b

class Pixel:
    def __init__(self, coordinate, color):
        self.coordinate = coordinate
        self.color = color


class ScreenServer(SampleBase):
    def __init__(self, *args, **kwargs):
        super(ScreenServer, self).__init__(*args, **kwargs)

    def drawPixel(self, pixel: Pixel):
        self.matrix.SetPixel(pixel.coordinate.x, pixel.coordinate.y, pixel.color.r, pixel.color.g, pixel.color.b)

    def redrawPixels(self, pixels: list):
        # new_canvas = self.matrix.CreateFrameCanvas()

        for pixel_dat in pixels:
            self.new_canvas.SetPixel(
                pixel_dat["coordinate"]["x"],
                pixel_dat["coordinate"]["y"],
                pixel_dat["color"]["r"],
                pixel_dat["color"]["g"],
                pixel_dat["color"]["b"]
            )

        self.new_canvas = self.matrix.SwapOnVSync(self.new_canvas)


    def jsonHandler(self, msg):
        try:
            dat = json.loads(msg)
        except:
            print(f"JSON parse fail: {msg}")
            return
        #pprint(dat)

        if dat["type"] == "clear":
            self.matrix.Clear()
        elif dat["type"] == "drawPixel":
            coord = Coordinate(dat["pixel"]["coordinate"]["x"],
                               dat["pixel"]["coordinate"]["y"])
            color = Color(
                dat["pixel"]["color"]["r"],
                dat["pixel"]["color"]["g"],
                dat["pixel"]["color"]["b"])

            pixel = Pixel(coord, color)

            self.drawPixel(pixel)
        elif dat["type"] == "redraw":
            pixels = dat["pixels"]
            # pprint(pixels)
            self.redrawPixels(pixels)


    def messageHandler(self, ch, method, properties, body):
        msg = str(body, 'utf-8')
        if msg[0] == '{':
            self.jsonHandler(msg)
        else:
            print(f"Unknown message format: {msg}")


    def run(self):
        self.new_canvas = self.matrix.CreateFrameCanvas()

        queueName = 'MazeScreen'
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()
        channel.queue_declare(queue=queueName)

        channel.basic_consume(queue=queueName, on_message_callback=self.messageHandler, auto_ack=True)

        print(' [*] Waiting for messages. To exit press CTRL+C')
        channel.start_consuming()


# Main function
if __name__ == "__main__":
    print("Starting RGB server")
    screenServer = ScreenServer()
    if (not screenServer.process()):
        screenServer.print_help()

    print("Shutting down.")
