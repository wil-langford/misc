#!/usr/bin/env python

"""Tries to isolate the fish as the white pixels in a binary image."""

DEBUG = False

from PIL import Image
import numpy as np
from scipy import ndimage
from skimage import filter as skifilter
import matplotlib.pyplot as plt
import time
import cv

class Wrangler:
    def __init__(self, image):
        self.newImage(image)
        self.mask = np.zeros(self.image.shape, dtype=np.int16)

    def newImage(self, image):
        """Object is getting a new image.  If it's already a numpy array, make
        sure it's got data type int16.  If it's a string, try to load from it
        like it's a filename."""
        if(type(image)==np.ndarray):
            if image.dtype==np.int16:
                self.image = image
            else:
                self.image = np.int16(image)
        elif(type(image)==str):
            self.image = np.int16(Image.open(image).convert('RGB'))
        else:
            raise ImageInitError("newImage requires a numpy array or filename.")

    def imageForPyplot(self):
        return np.uint8(self.image)

    def outlineLargestObjectInRed(self, calimage):
    
        self.deltaImage(calimage, 30, saveMask=True)
        self.largestObjectInMask(saveMask=True)
        self.findOutlineInMask(saveMask=True)
        return self.applyMaskInGreen()


    def findOutlineInMask(self,mask=None,saveMask=False,useCVCanny=True):
        """Basic edge detection using scipy's canny filter.  The image should
        be a grayscale image in numpy.uint8 format."""

        if mask == None:
            mask = self.mask
        
        t = time.time()

        if useCVCanny:
            im = np.uint8(mask * 255)
            im2 = np.zeros(im.shape, np.uint8)
            mat = cv.fromarray(im)
            mat2 = cv.fromarray(im2)
            mat3 = cv.fromarray(im2)
            dr = 21
            dr2 = (dr-1)/2
            shp = cv.CV_SHAPE_ELLIPSE
            cv.Canny(mat, mat2, 50, 100, 3)
            cv.Dilate(mat2,mat3,cv.CreateStructuringElementEx(7,7,3,3,shp))
            ol = np.asarray(mat2)
        else:
            im = mask * 255
            ol = skifilter.canny(im, 3, 0.3, 0.2)
        
        print "Canny filter took {} seconds.".format(time.time()-t)


        ol[ol>0]=1

        ol = np.uint8(ol)

        if saveMask:
            self.mask = ol

        return ol

    def applyMaskInGreen(self, mask=None):
    
        if mask==None:
            mask = self.mask

        im = np.copy(self.image)
        im[mask==1,1]=255

        return im


    def grayImage(self, saveImage=False, method=0):
        """If my image is not grayscale, convert it and return the gray version.
        Otherwise, return the image itself."""
        if self.image.ndim==2:
            gray = copy.deepcopy(self.image)
        else:
            # I experimented with each method.  All seem to work fine with my test images
            # so I'm using the fastest by default.
            # The higher the number of the method, the longer it takes.
            if method==0: # max of all three color values
                gray = np.amax(self.image, axis=2)
            elif method==1: # min of all three color values
                gray = np.amin(self.image, axis=2)
            elif method==2: # average of max color and min color
                gray = (np.amax(self.image, axis=2) + np.amin(self.image, axis=2)) // 2
            elif method==3: # average of all three colors
                gray = np.sum(self.image, axis=2) // 3
            elif method==4: # using the mean function and converting to integer
                gray = np.mean(self.image, axis=2)
                gray = np.int16(gray)

        if saveImage:
            self.image = gray

        return gray

    def deltaImage(self, calimage, threshold, saveMask=False):
        """Takes a calimage (e.g. an empty fish tank) and compares it with the image
        contained in the instance (e.g. the same tank with a fish).  It returns
        a numpy.uint8 array mask with zeroes where the instance's image is close
        to the calimage, and ones where they differ significantly."""

        cg = calimage.grayImage()
        sg = self.grayImage()

        if cg.shape != sg.shape:
            raise ImageMismatchError("Image and calibration image are not the same shape.")

        # find the difference between the images
        mask = abs(sg - cg)

        # Everything not over the threshold is zeroed out.  Everything above it
        # is set to one.
        mask[mask<threshold] = 0
        mask[mask>=threshold] = 1

        mask = np.uint8(mask)

        if saveMask:
            self.mask = mask

        return mask

    def largestObjectInMask(self, mask=None, saveMask=False):
        """Takes a numpy.uint8 array with 1s and 0s for values.  Labels each connected
        region of 1s with a different integer.  Determines the largest such connected
        region.  Discards all blocks except the largest, and returns the mask with only
        the largest object represented by 1s."""

        if mask==None:
            mask = self.mask

        # this is the part where all the magic is performed by scipy
        labeled, how_many_labels = ndimage.label(mask)

        # spit out an array listing the size of each labeled block
        sizes = ndimage.sum(mask, labeled, range(how_many_labels + 1))

        # find the label of the largest region
        max_label = list(sizes).index(max(sizes))

        # if you're not in the largest region, you get set to zero
        # if you are in the largest region, you get set to 1
        mask[labeled!=max_label]=0
        mask[labeled==max_label]=1

        mask = np.uint8(mask)

        if saveMask:
            self.mask = mask

        return mask


class ImageInitError(Exception):
    pass

class ImageMismatchError(Exception):
    pass
