#!/usr/bin/env python


from matplotlib import pyplot as plt
import cv2
import numpy as np


def plot_histogram(image, vertlines=[]):

    colors = ("b", "g", "r")
    chans = cv2.split(image)
    # colors = ("b")
    plt.figure()
    plt.title("'Flattened' Color Histogram")
    plt.xlabel("Bins")
    plt.ylabel("# of Pixels")
    features = []
    for (chan, color) in zip(chans, colors):
        hist,bins = np.histogram(chan.ravel(),256,[2,254])
        features.extend(hist)
        for i in vertlines:
            plt.axvline(x=i)
        plt.plot(hist, color = color)
        plt.xlim([0, 256])
    plt.show()


def equalize_RBG(image):
    chans = cv2.split(image)
    mean = np.mean(chans, axis = 1)
    A_Coeff = mean[0]/mean[2]
    B_Coeff = mean[0]/mean[1]

    img = np.copy(image)
    img[:,:,2] = A_Coeff * image[:,:,2]
    img[:,:,1] = B_Coeff * image[:,:,1]
    return img

def get_new_contrast(pixel, a, b, c , d):
    # a is lower limit
    # b is upper limit
    # c is minimum pixel value in image
    # d is max pixel value currently present
    return (pixel - c) * (b - a) / (d - c) + a;

def my_funct(image, clipPercent):
    histSize = 256
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    hist = cv2.calcHist([gray_image], [0], None, [256], [0, 256])

    accum = np.zeros(len(hist))
    accum[0] = hist[0]
    for i in xrange(1, len(hist)):
        accum[i] = accum[i-1] + hist[i]
    max_in_accum = accum[-1]

    clipPercent = clipPercent * (max_in_accum/100.0)
    clipPercent = clipPercent/2

    minGray = 0
    while (accum[minGray] < clipPercent):
        minGray=minGray+1

    maxGray = len(hist) - 1
    while(accum[maxGray] >= (max_in_accum - clipPercent)):
        maxGray=maxGray-1

    plt.figure()
    plt.title("Grayscale Histogram")
    plt.xlabel("Bins")
    plt.ylabel("# of Pixels")
    plt.plot(hist)
    plt.xlim([0, 256])
    plt.axvline(x=minGray)
    plt.axvline(x=maxGray)
    plt.plot()

    plot_histogram(image, vertlines=[minGray, maxGray])
    contrastCorrection = ContrastCorrection(image, minGray, maxGray)
    # res = contrastCorrection.correct_lower()
    # contrastCorrection.update_img(res)
    # res = contrastCorrection.correct_upper()
    res = contrastCorrection.correct_both()
    plot_histogram(res)


    cv2.imshow("1", image)
    cv2.imshow("2", res)
    cv2.waitKey(0)

class ContrastCorrection:
    def __init__(self, image, minGray, maxGray):
        (B, G, R) = cv2.split(image)
        self.blue_vals = [np.min(B[np.nonzero(B)]), np.max(B[np.nonzero(B)])]
        self.green_vals = [np.min(G[np.nonzero(G)]), np.max(G[np.nonzero(G)])]
        self.red_vals = [np.min(R[np.nonzero(R)]), np.max(R[np.nonzero(R)])]
        self.image = image
        self.minGray = minGray
        self.maxGray = maxGray
        self.inputRange = maxGray - minGray

    def correct_upper(self):
        res = np.copy(self.image)
        alpha = (255 - self.red_vals[0])/(self.inputRange)
        beta = self.red_vals[0]
        res[:,:,0:2] = (res[:,:,0:2] - self.minGray) * alpha + beta
        return res
    def correct_lower(self):
        res = np.copy(self.image)
        alpha = (self.blue_vals[1])/(self.inputRange)
        beta = 0
        res[:,:,0:2] = (res[:,:,0:2] - self.minGray) * alpha + beta
        return res
    def correct_both(self):
        res = np.copy(self.image)
        alpha = (255)/(self.inputRange)
        beta = 0
        res[:,:,0:2] = (res[:,:,0:2] - self.minGray) * alpha + beta
        return res
    def update_img(self, image):
        self.image = image
img = cv2.imread('maxresdefault.jpg')
# maxresdefault.jpg

# plot_histogram(img)

bleh = equalize_RBG(img)

my_funct(bleh, .05)

# plot_histogram(bleh)

# chans = cv2.split(image)
# hist,bins = np.histogram(chan.ravel(),256,[0,256])


# min_vals = np.min(np.min(bleh, axis=0), axis=0)
# max_vals = np.max(np.max(bleh, axis=0), axis=0)
# print min_vals, max_vals

# contrast = 25
# factor = (259.0 * (contrast + 255.0)) / (255.0 * (259.0 - contrast))

# my_range = max_vals - min_vals
# alpha = (255/my_range)
# beta = -min_vals * alpha


# res = cv2.convertScaleAbs(bleh, alpha, beta)
# res = res*alpha
# print bleh
# bleh[:,:,:] = alpha*bleh[:,:,:] + 100

# min_vals = np.min(np.min(bleh, axis=0), axis=0)
# max_vals = np.max(np.max(bleh, axis=0), axis=0)
# print min_vals, max_vals
# bleh = cv2.imread('shark.png')
# cv2.imshow("sdis", bleh)
# cv2.waitKey(0)
# bleh[:,:,:] = bleh[:,:,:] + 25;
# bleh[:,:,:] = (factor * (bleh[:,:,:] - 128) + 128)
# print bleh[np.nonzero(bleh[:,:,0:3])]
# print bleh
# print min_vals


# bleh[:,:,0] = get_new_contrast(bleh[:,:,0], min_vals[2], 255, min_vals[0], max_vals[0])
# bleh[:,:,1] = get_new_contrast(bleh[:,:,1], min_vals[2], 255, min_vals[1], max_vals[1])
# bleh[:,:,2] = get_new_contrast(bleh[:,:,2], min_vals[2], 255, min_vals[2], max_vals[2])
# print bleh

# chans = np.array(cv2.split(bleh))
# print chans.shape
# min_val, max_val, min_loc, max_loc= cv2.minMaxLoc(chans[0])

# print min_val, max_val

# print "============================================"
# print min_vals

# bleh[:,:,0:3] = (bleh[:,:,0:3] - min_vals[:]) * (255 - min_vals[2])/(max_vals[:] - min_vals[:]) + min_vals[2]


# print "===================================="
# print bleh
# cv2.imshow(bleh)
# cv2.imshow("soidiosd", bleh)
# cv2.imshow("Sdposdop", (bleh - min_vals) * (255 - ))
# img_yuv = cv2.cvtColor(img, cv2.COLOR_BGR2YUV)

# # equalize the histogram of the Y channel
# img_yuv[:,:,0] = cv2.equalizeHist(img_yuv[:,:,0])

# # convert the YUV image back to RGB format
# img_output = cv2.cvtColor(img_yuv, cv2.COLOR_YUV2BGR)

# plot_histogram(img_output)

# cv2.waitKey(0)