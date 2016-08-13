import numpy as np
import argparse
import cv2

#load the image and change it to greyscale for operating it and read template image that is used to search lines in the image
image = cv2.imread(fi)
bgr = cv2.split(image) #Extracting rgb-channels from the image
gray = bgr[0] #apparently python uses bgr instead of rgb, so 2 is the red channel
#gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) 
template = cv2.imread('template.jpeg',0)
#cv2.imshow("Image", gray)
#cv2.waitKey(0)

#Here we crop the central part of the input image in order to exclude everything else in the image. Test lines must be at the center for this. 
#Croped area scales according to resolution input size with default 1280*720 resolution leading to 60 px height and 300 px width. 
imageSize=np.shape(gray)
#objectThreshold=imageSize[0]*imageSize[1]/1000
imgMidpoint = np.divide(imageSize,2)
#print imgMidpoint
croped = gray[imgMidpoint[0]-int(imageSize[0]/24):imgMidpoint[0]+int(imageSize[0]/24), imgMidpoint[1]-int(imageSize[1]/8.5):imgMidpoint[1]+int(imageSize[1]/8.5)]
#print croped
#cv2.imshow("croped", croped)
#cv2.waitKey(0)


#Size of the croped image is used to divide it into two parts from witch both lines can be detected without them interfering with each other.
croppedSize=np.shape(croped)
#print croppedSize

#Size of the template which is used to move T-line crop to the right of the C-line. This has to be also scaled to keep it consistent with higher resolutions.
w, h = template.shape[::-1]
w = int(w * (imageSize[1]/1280.0))
h = int(h * (imageSize[0]/720.0))


#We first crop 40% of the original croped images right side. C-line should be within this area while T-line should be outside if the image is taken correctly.
#This is done in case that T-line might be sometimes stronger than C-line so we have to exclude it just in case.
#C-line is always strong so we can use high threshold for it's detection.
#Once template matching finds the C-line we save it's location to locC for later use.
m = 0.35
for i in xrange (0,3):
    
    cropedC = croped[0:croppedSize[0], 0:int(croppedSize[1]*m)]
    #cv2.imshow("cropedC", cropedC)
    #cv2.waitKey(0)
    res = cv2.matchTemplate(cropedC,template,cv2.TM_CCOEFF_NORMED)
    threshold = 0.7
    locC = np.where( res >= threshold)
    locC = zip(*locC[::-1])
    #print locC
    if locC == []:
        m = m + 0.05
    else:
        break

if locC == []:
    print 'No C-line found'
else:    
#If C-line is not found the whole algorithm fails and skips the rest of the code. 
#Otherwise we find the maximum coordinates so we can draw C-lines location and crop original croped image from such a spot that C-line is never within it to find T-line correctly.


    max_locC = max(locC)
    #min_locC = min(locC)
    #print max_locC
    #print min_locC

    #T-line croping scales with width. With default 1280*720 resolution it's 100 px to the right of C-line's location.
    #Since T-line can be very light we use equalizing in order to emphasize it in it's locating crop.
    cropedT = croped[int(croppedSize[0]*0.1):int(croppedSize[0]*0.9), max_locC[0]+w:max_locC[0]+int(imageSize[1]/12.8)]

    clahe = cv2.createCLAHE(clipLimit=10.0, tileGridSize=(1,100))
    cropedT = clahe.apply(cropedT)
    #cropedT = cv2.equalizeHist(cropedT)
    alpha = np.array([1.35])
    beta = np.array([-50.0])

    # add a beta value to every pixel 
    cropedT = cv2.add(cropedT, beta)                                       

    # multiply every pixel value by alpha  
    cropedT = cv2.multiply(cropedT, alpha)  

    cv2.imshow("cropedT", cropedT)
    cv2.waitKey(0)

    #Using the template matching again we try to locate a possible T-line. Since it may be lighter than C-line we use lower threshold.
    #Again we save it's location for later use. 
    #If T-line is not found we just skip to the rest of the C-lines calculations and tell the ratio calculation that T-lines intensity is 255 so we can calculate the ratio even in this case.
    res = cv2.matchTemplate(cropedT,template,cv2.TM_CCOEFF_NORMED)
    threshold = 0.35
    locT = np.where( res >= threshold)
    locT = zip(*locT[::-1])
    #print locT
    if locT == []:
        print 'No T-line found'
        avg_T = 255
    else:
        max_locT = max(locT)
        #min_locT = min(locT)
        #print max_locT
        #print min_locT

        #Since we croped T-line image separately and equalized it we cannot use that for it's true location and ratio calculation. So instead we add it's location to C-lines location + template width.
        # Since we always crop T-line from the right of the C-line we know that C-lines location + template width added to the T-lines saved location equals T-lines location in the original croped image.
        top_leftT = np.add(max_locT[0], max_locC[0]+w),max_locC[1]
        bottom_rightT = (top_leftT[0] + w, top_leftT[1] + h)
        cv2.rectangle(croped,top_leftT, bottom_rightT, 255, 2)

        #Calculating average intensity of the T-line using it's coordinates calculated above. 
        Tline = croped[top_leftT[1]:bottom_rightT[1], top_leftT[0]:bottom_rightT[0]]
        avg_T = np.average(Tline)

    #Same as with T-line except it's a lot simpler because C-line is croped from the left of the original croped image.    
    top_leftC = max_locC
    bottom_rightC = (top_leftC[0] + w, top_leftC[1] + h)
    cv2.rectangle(croped,top_leftC, bottom_rightC, 255, 2)

    Cline = croped[top_leftC[1]:bottom_rightC[1], top_leftC[0]:bottom_rightC[0]]
    avg_C = np.average(Cline)

    cv2.imwrite('res.png',croped)

    #cv2.imshow("Cline", Cline)
    #cv2.waitKey(0)
    #cv2.imshow("Tline", Tline)
    #cv2.waitKey(0)

    #Ratio calculation. We first substract average intensity from 255 so that no T-line equals zero ratio and strong T-line 100% ratio.
    avg_C = 255 - avg_C
    avg_T = 255 - avg_T

    #print avg_C
    #print avg_T

    ratio = avg_T/avg_C

    print "ratio:", ratio