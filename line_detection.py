#from scipy.spatial import distance as dist
#from imutils import perspective
#from imutils import contours
import numpy as np
import argparse
#import imutils
import cv2
import time
import os
import xlsxwriter


#from matplotlib import pyplot as plt

timestamp1 = time.time()
 
# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=False,
	help="path to the input image")
ap.add_argument("-d", "--dir", required=False,
	help="path to the input directory")
ap.add_argument("-t", "--tl", required=True,
	help="T-line's distance from C-line in pixels")
ap.add_argument("-tem", "--template", required=True,
	help="Template for test area")

args = vars(ap.parse_args())
tl = int(args["tl"])
testArea = args["template"]
if args["dir"] is None and args["image"] is None:
    print "Please give either a single image or image folder as argument"
elif args["dir"] is None:
    fi = args["image"]
    execfile ("single_img.py")
    #execfile ("single_image.py")
else:
    indir = args["dir"]
    execfile ("multi_img.py")
    #execfile ("multi_image.py")
    
execfile ("classifier_teach.py")


#cells = sheet['B1':'B61']
#print cells
#reference = (sheet['B2:B61'].value)
#print reference
                

timestamp2 = time.time()
print "time", (timestamp2 - timestamp1)