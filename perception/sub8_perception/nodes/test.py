#!/usr/bin/env python

from matplotlib import pyplot as plt
import numpy as np

import cv2

def plot_histogram(image):

    colors = ("b", "g", "r")
    chans = cv2.split(image)
    # colors = ("b")
    plt.figure()
    plt.title("'Flattened' Color Histogram")
    plt.xlabel("Bins")
    plt.ylabel("# of Pixels")
    features = []
    for (chan, color) in zip(chans, colors):
        hist,bins = np.histogram(chan.ravel(),256,[0,256])
        features.extend(hist)
        b = np.average(chan)

        plt.plot(hist, color = color)
        plt.axvline(x=b, color = "black")
        plt.xlim([0, 256])
    plt.show()


image = cv2.imread("gate.png")

plot_histogram(image)

test1, test2 = cv2.meanStdDev(image)

img = np.copy(image)
mask = cv2.inRange(img, test1 - 2*test2, test1+2*test2)
mask = cv2.bitwise_not(mask, mask)
res = cv2.bitwise_and(img,img, mask= mask)

# print img
# print "-------------------------------"
# print img[:,:,1]
# inds = img[:,:,0] > test1[0] - 2*test2[0]
# img[inds] = [255,255,255]

# print "------------------"
# print img
cv2.imshow("sds", res)

# plot_histogram(res)

cv2.waitKey(0)