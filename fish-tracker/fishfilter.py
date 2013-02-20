#!/usr/bin/env python

"""Tries to isolate the fish as the white pixels in a binary image."""

DEBUG = False

import numpy as np
from scipy import ndimage
from skimage.filter import canny
import matplotlib.pyplot as plt

def outlinefish(nofish, rawfish):
    """Takes two color image numpy arrays, one without the
    fish and one with, then outlines the fish."""

    fish = filterfish(nofish, rawfish)

    fish = canny(fish, 3, 0.3, 0.2)

    fish=np.uint8(fish)
    fish[fish>0]=255

    return np.uint8(fish)


def filterfish(nofish, rawfish):
    """Takes two color image numpy arrays, one without the
    fish and one with, then returns a black and white image with
    the fish in white."""

    # we're going to need negative numbers for this next bit
    fish = np.int16(rawfish)

    # find the difference between the images
    thresh = 30
    fish = fish - thresh
    fish = fish - nofish

#    # RGB thresholds
#    r_thresh = 3
#    g_thresh = 3
#    b_thresh = 3
#
#    # any color below its threshold gets zeroed
#    # any color above its threshold gets set to 255
#    fish[:,:,0] = 255*(fish[:,:,0]>r_thresh)
#    fish[:,:,1] = 255*(fish[:,:,1]>g_thresh)
#    fish[:,:,2] = 255*(fish[:,:,2]>b_thresh)

    # add up all the colors and average them
    fish = (fish[:,:,0] + fish[:,:,1] + fish[:,:,2]) // 3

    # anything that's less than 255 gets tossed
    # we only want pixels that passed on all three thresholds
    fish[fish<255]=0
    fish[fish==255]=1

    labeled, how_many_labels = ndimage.label(fish)
    sizes = ndimage.sum(fish, labeled, range(how_many_labels + 1))
    max_label = list(sizes).index(max(sizes))
    labeled[labeled!=max_label]=0
    labeled[labeled==max_label]=255

    return np.uint8(labeled)
