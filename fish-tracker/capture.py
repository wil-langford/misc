#!/usr/bin/env python

from PIL import Image
import numpy as np
import ueye
import time

capturedir="input"

cam = ueye.Cam()
cam.SetColorCorrection(ueye.CCOR_DISABLE)
cam.SetEdgeEnhancement(ueye.EDGE_EN_STRONG)

for i in range(100):
    print "Grabbing frame {}.".format(i)
    raw_input("press enter")
    im_array = cam.GrabImage()
    print "Got frame."
    Image.fromarray(im_array).save("{}/{:04d}.jpg".format(capturedir, i))
    print "Saved to {}/{:04d}.jpg.".format(capturedir, i)
