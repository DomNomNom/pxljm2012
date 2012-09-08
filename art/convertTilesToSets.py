#!/usr/bin/env python2

from PIL import Image
import glob, os
from os import path



basePath = path.dirname(__file__)
#print os.listdir(path.join(basePath, "tiles"))

for folderName in os.listdir(path.join(basePath, "tiles")):
    # read
    images = []
    width = height = 0
    for infile in glob.glob(path.join(basePath, "tiles", folderName, "*.png")):
        file, ext = os.path.splitext(infile)
        im = Image.open(infile)
        width = max(width, im.size[0])
        height += im.size[1]
        images.append(im)


    # make image
    y=0
    size = (width, height)
    out = Image.new('RGBA', size)
    for img in images:
        out.paste(img, (0, y))
        y += img.size[1]

    # write
    out.save(path.join(basePath, "tileSets", folderName + '.png'), "PNG") # write
