#!/usr/bin/env python

"""Tries to isolate the fish as the white pixels in a binary image."""

from PIL import Image
import numpy as np
import fishfilter

first = 2
step = 1
last = 3

inputdir = "input"
outputdir = "output"

nofish = np.array(Image.open("{}/calibrate.jpg".format(inputdir)))

for i in xrange(first,last+1,step):
    fish = np.array(Image.open("{}/{:04d}.jpg".format(inputdir,i)))
    outline = fishfilter.outlinefish(nofish, fish)
    fish[:,:,0] = outline
    fishout = Image.fromarray(fish)
    fishout.save("{}/{:04d}.jpg".format(outputdir,i))
