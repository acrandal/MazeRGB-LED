#!/usr/bin/env python3

import sys
from pprint import pprint
from PIL import Image

def unpickle(file):
    import pickle
    with open(file, 'rb') as fo:
        dict = pickle.load(fo, encoding='bytes')
    return dict

def getImage(dataDict, imageNumber):
    imgColorsArr = dataDict[b'data'][imageNumber]
    #pprint(imgColorsArr)

    img = Image.new('RGB', (32,32), color = 'black')
    for arrIndex in range(1024):
        red = imgColorsArr[arrIndex]
        green = imgColorsArr[arrIndex + 1024]
        blue = imgColorsArr[arrIndex + 2048]

        imageX = arrIndex % 32
        imageY = int(arrIndex / 32)

        img.putpixel((imageX, imageY), (red, green, blue))
    return img



if __name__ == "__main__":
    print("Starting")
    dict = unpickle(sys.argv[1])
    #pprint(dict)

    images = []

    for imageNumber in range(10000):
        print(f"\rLoading image #{imageNumber}", end="")
        currImage = getImage(dict, imageNumber)
        images.append(currImage)
    print()
    pprint(images)

    
    #img = Image.new('RGB', (32,32), color = 'black')
    #for arrIndex in range(1024):
        #red = imgColorsArr[arrIndex]
        #green = imgColorsArr[arrIndex + 1024]
        #blue = imgColorsArr[arrIndex + 2048]

        #imageX = arrIndex % 32
        #imageY = int(arrIndex / 32)
##
        #img.putpixel((imageX, imageY), (red, green, blue))

    #img = Image.new('RGB', (32,32), color = 'black')
    #img.putpixel((10, 20), (155,155,155))
    #img.save('testout.png')
    #img.show()
