import numpy as np
import argparse
import cv2

"""***************************************************************
******************Image reading and preparation*******************
***************************************************************"""
#load the image and change it to greyscale for operating it and read template image that is used to search lines in the image
"""image = open('iPhone6_10_01.txt')
#print image
triplets=image.read().split()
for i in range(0,len(triplets)): triplets[i]=triplets[i].split(';')
#print triplets    
image=np.array(triplets, dtype=np.uint8)"""
#print triplets
image = cv2.imread(fi)
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#gray = cv2.equalizeHist(gray)
#croped = gray
template = cv2.imread('template.jpeg',0)
#cv2.imshow("Image", gray)
#cv2.waitKey(0)
testArea = cv2.imread(testArea,0)
#Here we crop the central part of the input image in order to exclude everything else in the image. Test
#lines must be at the center for this. We also crop the colored version for later use with intensities.
#Croped area scales according to resolution input size with default 1280*720 resolution leading to 60 px height and 300 px width.

imageSize=np.shape(gray)
#print imageSize

imgMidpoint = np.divide(imageSize,2)
#print imgMidpoint

gray_middle = gray[imgMidpoint[0]-int(imageSize[0]/5):imgMidpoint[0]+int(imageSize[0]/5), imgMidpoint[1]-int(imageSize[1]/3):imgMidpoint[1]+int(imageSize[1]/3)]

image_middle = image[imgMidpoint[0]-int(imageSize[0]/5):imgMidpoint[0]+int(imageSize[0]/5), imgMidpoint[1]-int(imageSize[1]/3):imgMidpoint[1]+int(imageSize[1]/3)]

#cv2.imshow("croped", gray_middle)
#cv2.waitKey(0)


#Size of the croped image is used to divide it into two parts from which both lines can be detected
#without them interfering with each other.
#croppedSize=np.shape(croped)
#print croppedSize

#Size of the template which is used to move T-line crop to the right of the C-line. This has to be also
#scaled to keep it consistent with higher resolutions.
w, h = template.shape[::-1]
w = int(w * (imageSize[1]/1280.0))
h = int(h * (imageSize[0]/720.0))
#print h

w2, h2 = testArea.shape[::-1]
w2 = int(w2 * (imageSize[1]/1280.0))
h2 = int(h2 * (imageSize[0]/720.0))

res = cv2.matchTemplate(gray_middle,testArea,cv2.TM_CCOEFF_NORMED)
#print res
min_val, max_val, min_locTem, max_locTem = cv2.minMaxLoc(res)
print min_locTem, max_locTem, max_val
croped = gray_middle[max_locTem[1]:max_locTem[1]+h2, max_locTem[0]:max_locTem[0]+w2]
cropedcolor = image_middle[max_locTem[1]:max_locTem[1]+h2, max_locTem[0]:max_locTem[0]+w2]
cv2.imshow("croped", croped)
cv2.waitKey(0)
croppedSize=np.shape(croped)


"""***************************************************************
******************************C-line******************************
***************************************************************"""
#We first crop 35% of the original croped images right sides. C-line should be within this area and if
#not we enlarge the crop area by 5% up to 45%. At the same time we grow variable l for later use with T-line. 
#T-line should be outside if the image is taken correctly.
#This split is done in case that T-line might be sometimes stronger than C-line so we have to exclude it just in case.
#C-line is always strong so we can use high threshold for it's detection.
#Once template matching finds the C-line we save it's location to locC for later use.
r = 0.35
l = 0.0
for i in xrange (0,3):

    cropedC = croped[0:croppedSize[0], 0:int(croppedSize[1]*r)]
    cv2.imshow("cropedC", cropedC)
    cv2.waitKey(0)
    res = cv2.matchTemplate(cropedC,template,cv2.TM_CCOEFF_NORMED)
    #print res
    min_val, max_val, min_locC, max_locC = cv2.minMaxLoc(res)
    print 'C-max_val', max_val
    #print max_locC
    
    #threshold = 0.7
    #locC = np.max(res >= threshold)
    #locC = zip(*locC[::-1])
    #print locC
    if max_val < 0.7:
        r = r + 0.05
        l = l + 0.05
    else:
        break
        

#If test area is not found from the middle then we search for it from the whole image.
if max_val < 0.7:
    res = cv2.matchTemplate(gray,testArea,cv2.TM_CCOEFF_NORMED)
    #print res
    min_val, max_val, min_locTem, max_locTem = cv2.minMaxLoc(res)
    print min_locTem, max_locTem, max_val
    croped = gray[max_locTem[1]:max_locTem[1]+h2, max_locTem[0]:max_locTem[0]+w2]
    cropedcolor = image[max_locTem[1]:max_locTem[1]+h2, max_locTem[0]:max_locTem[0]+w2]
    #cv2.imshow("croped", croped)
    #cv2.waitKey(0)
    croppedSize=np.shape(croped)
    
    r = 0.35
    l = 0.0
    for i in xrange (0,3):

        cropedC = croped[0:croppedSize[0], 0:int(croppedSize[1]*r)]
        cv2.imshow("cropedC", cropedC)
        cv2.waitKey(0)
        res = cv2.matchTemplate(cropedC,template,cv2.TM_CCOEFF_NORMED)

        min_val, max_val, min_locC, max_locC = cv2.minMaxLoc(res)
        print max_val

        if max_val < 0.7:
            r = r + 0.05
            l = l + 0.05
        else:
            break
    if max_val < 0.7:
        print 'No C-line found'
        exit()
        
#Bilateral filter is heavy for performance but it preserves edges much better, so we use it to both grayscale and color image to filter away noise.
#Because it's heavy it should not be used on to whole image but only to small important area of it.
croped = cv2.bilateralFilter(croped,7,75,75)
cropedcolor = cv2.bilateralFilter(cropedcolor,7,75,75)        


#Calculate C-lines top left coordinate and it's buttom right coordinate which we can then use to
#separate C-line from the rest of the image for later ratio calculation and of course to crop area
#that T-line is in without including C-line.  
top_leftC = max_locC
bottom_rightC = (top_leftC[0] + w, top_leftC[1] + h)

"""***************************************************************
***********************Channel Selection**************************
***************************************************************"""

#Here we first crop C-line and take the intensity values of it's center area. By using the colored
#image we croped earlier we can split it into blue, green and red channels and use the center pixels'
#intensity values and compare those to similar sized non-line area next to it. This way we can use the channel that gives 
#greatest contrast between background and line's colors as grayscale image. This helps detecting T-line when it might be dim.

Cline = cropedcolor[int(top_leftC[1]):int(bottom_rightC[1]), top_leftC[0]:bottom_rightC[0]]
#cv2.imshow("Cline", Cline)
#cv2.waitKey(0)

ClineMid = np.divide(np.shape(Cline),2)
Cmid = Cline[ClineMid[0]-5:ClineMid[0]+5, ClineMid[1]-3:ClineMid[1]+3]
CmidSum = np.sum(Cmid,axis=1)
CmidSum = np.sum(CmidSum,axis=0)


Cout = cropedcolor[ClineMid[0]-5:ClineMid[0]+5, bottom_rightC[0]+w:bottom_rightC[0]+w+6]
Cout = np.sum(Cout,axis=1)
Cout = np.sum(Cout,axis=0)

ClineCont = Cout - CmidSum

if ClineCont[0] > ClineCont[1] and ClineCont[0] > ClineCont[2]:
    bgrValue = 0
elif ClineCont[1] > ClineCont[0] and ClineCont[1] > ClineCont[2]:
    bgrValue = 1
elif ClineCont[2] > ClineCont[0] and ClineCont[2] > ClineCont[1]:
    bgrValue = 2

bgr = cv2.split(cropedcolor) #Extracting rgb-channels from the image
cropedbgr = bgr[bgrValue] #apparently python uses bgr instead of rgb, so 0 is blue and 2 is red
Cline = cropedbgr[int(top_leftC[1]):int(bottom_rightC[1]), top_leftC[0]:bottom_rightC[0]]
Cmid = Cline[ClineMid[0]-5:ClineMid[0]+5, ClineMid[1]-3:ClineMid[1]+3]
#Cmid = cv2.cvtColor(Cmid, cv2.COLOR_BGR2GRAY)    
avg_C = np.average(Cmid)
#print avg_C


"""***************************************************************
******************************T-line******************************
***************************************************************"""
#T-line croping scales with width. With default 1280*720 resolution it's 100 px to the right of C-line's location.
#Since T-line can be very light we use contrast in order to emphasize it in it's locating crop.
cropedT = cropedbgr[int(top_leftC[1]):int(bottom_rightC[1]), top_leftC[0]+w:bottom_rightC[0]+int(imageSize[1]/12.8)]

#Basic idea here is that substract from low intensity value is relatively larger drop than with
#bright area. Therefore if we substract large amount of intensity and then multiply the result with
#something larger than 1 dark areas are left much darker than light areas.
#cropedT = cv2.blur(cropedT,(10,10))
clahe = cv2.createCLAHE(clipLimit=100.0, tileGridSize=(1,100))
cropedT = clahe.apply(cropedT)
alpha = np.array([1.55])
beta = np.array([-50.0])

# add a beta value to every pixel 
cropedT = cv2.add(cropedT, beta)                                       

# multiply every pixel value by alpha  
cropedT = cv2.multiply(cropedT, alpha)
#cropedT = cv2.blur(cropedT,(2,10))



#cropedT = cv2.bilateralFilter(cropedT,9,75,75)
#cropedT = cv2.GaussianBlur(cropedT,(5,5),0)
#cropedT = cv2.blur(cropedT,(5,15))

#cropedT = cv2.equalizeHist(cropedT)


cv2.imshow("cropedT", cropedT)
cv2.waitKey(0)

#Tsum is the sum of croped T area by it's x vector. We then calculate it's average value and drop it
#just slightly to get a threshold value for detecting T-line.

Tsum = np.sum(cropedT, axis=0)
#TsumAvg = np.average(Tsum)*0.999

TsumSize = np.shape(Tsum)

#print TsumAvg
#print TsumSize



#locT is the x pixel that we start looking T-line from as there is no use to look for it right next to
#C-line. This is calculated by using distance argument value given to the main program that is then
#droped to 80% to leave a bit of room for T-line and is then moved by l variable we calculated
#earlier when we detected C-line. This is in case that C-line is very far to the right and therefore
#T-line is more to the left of the croped image. This generally happens when test area is smaller in
#the image and we need to have some tolerance for it. Same kind of scaling is udes to the right side
#of the T-line with scale from 25% to 35% left off.

#Size variable is grown by each point below the threshold and reseted to 0 if there are not enough of
#them in a row and next one is farther than 2 points away, which is what tolerance variable is for.
#Finally we get T-lines leftmost location by adding 1 to it each time there is no line point present.
locT = int(tl * 0.8 *(1-l*2.5))
locTR = int(tl * (0.5+l*2))
#print locT
#print locTR
#print TsumSize[0]-locTR
Tavg = Tsum[locT:TsumSize[0]-locTR]
TsumAvg = np.average(Tavg)*0.95
#print Tavg
#print TsumAvg


size = 0
tolerance = 0
min_size = int(w*0.6)
#print min_size
for x in xrange(locT,TsumSize[0]-locTR):

    if Tsum[x] > TsumAvg and size >= min_size:
        Tsum[x] = 0
        if tolerance > 0:
            tolerance = tolerance - 1
        else:
            break
    elif Tsum[x] < TsumAvg:
        size = size + 1
    elif Tsum[x] > TsumAvg and size <= min_size:
        locT = locT + 1 + size
        Tsum[x] = 0
        size = 0

#print Tsum   
print size
print locT

if size < min_size: #or size > 14:
    avg_T = 255
    avg_bg = 255
    locT = 0
    size = 0
else:
    if size > w:
        offset = (size - w)/2
        size = w
    else:
        offset = 0

    #Using T-line's and template's sizes scale C-line's size along both axis and T-line's Y-axis
    #and recrop C-line, so it's intensity can be calculated more accurately.
    Xscale = (w-size)/2
    #print Xscale
    Yscale = abs(int((float(size)/float(w)) * h - h) /2 )

    top_leftC = (max_locC[0] + Xscale, max_locC[1] + Yscale)
    bottom_rightC = (top_leftC[0] + size, top_leftC[1] + h -Yscale)
    #print top_leftC
    #print bottom_rightC

    Cline = croped[int(top_leftC[1]):int(bottom_rightC[1]), top_leftC[0]:bottom_rightC[0]]

    #avg_C = np.average(Cline)

    top_leftT = (bottom_rightC[0]+locT+offset, bottom_rightC[1]-h +Yscale)
    bottom_rightT = (top_leftT[0] + size, top_leftT[1] + h -Yscale)

    #print top_leftT
    #print bottom_rightT

    """***************************************************************
    ************************Ratio Calculation*************************
    ***************************************************************"""

    #Calculating average intensity of the T-line using it's coordinates calculated above. 
    # In addition we take areas from it's left and right side to get reference value for background
    #intensity for ratio calculation. 
    Tline = cropedbgr[top_leftT[1]:bottom_rightT[1], top_leftT[0]-20:bottom_rightT[0]+20]

    TlineMid = np.divide(np.shape(Tline),2)
    Tmid = Tline[TlineMid[0]-3:TlineMid[0]+3, TlineMid[1]-3:TlineMid[1]+3]
    #print TlineMid

    Tleft = Tline[TlineMid[0]-3:TlineMid[0]+3, TlineMid[1]-3-w:TlineMid[1]+3-w]
    Tright = Tline[TlineMid[0]-3:TlineMid[0]+3, TlineMid[1]-3+w:TlineMid[1]+3+w]
    
    avg_T = np.average(Tmid)
    avg_Tleft = np.average(Tleft)
    avg_Tright = np.average(Tright)
    avg_bg = (avg_Tleft+avg_Tright)/2
    #Tline = cropedbgr[top_leftT[1]:bottom_rightT[1], top_leftT[0]-20:bottom_rightT[0]+20]
    

cv2.rectangle(cropedcolor,top_leftC, bottom_rightC, 255, 2)




cv2.imshow("Cline", Cline)
cv2.waitKey(0)
cv2.imshow("Tline", Tline)
cv2.waitKey(0)

#Ratio calculation. Background intensity is substracted from C- and T-line's intensity and all of
#them are turned around by substracting them from 255 so that more standard C-line can be used as
#divider even though it's usually darker and therefore lower intensity.
bg_div = avg_bg /100
avg_bg = (255 - avg_bg) /bg_div
avg_C = (255 - avg_C) /bg_div - avg_bg
avg_T = (255 - avg_T) /bg_div - avg_bg
print 'C', avg_C
print 'T',avg_T


#Check if T-line is strong enough. If it's very dim, ignore it outright.
#If it's a little bit strong but not clear enough then check if it is actually a line with template.
if avg_T < 0.1:
    locT = 0
    size = 0
    avg_T = 0
    print 'No T-line found'
elif avg_T < 1.0:

    Tline = clahe.apply(Tline)
    #Tline = cv2.equalizeHist(Tline)
    alpha = np.array([1.55])
    beta = np.array([-50.0])

    # add a beta value to every pixel 
    Tline = cv2.add(Tline, beta)                                       

    # multiply every pixel value by alpha  
    Tline = cv2.multiply(Tline, alpha)
    #Tline = cv2.bilateralFilter(Tline,9,75,75)
    #Tline = cv2.blur(Tline,(1,5))
    cv2.imshow("T line", Tline)
    cv2.waitKey(0)
    TsumYSize = np.shape(Tline)
    print TsumYSize
    TlineY = Tline[0:TsumYSize[0],int(TsumYSize[1]*0.3):int(TsumYSize[1]*0.7)]
    TsumYSize = np.shape(TlineY)
    TsumY = np.sum(TlineY, axis=1)
    
    template = cv2.resize(template,(w,TsumYSize[0]))
    res = cv2.matchTemplate(TlineY,template,cv2.TM_CCOEFF_NORMED)

    min_val, max_val, min_locC, max_locC = cv2.minMaxLoc(res)
    print 'T-max_val', max_val
    if max_val < 0.5:
        avg_T = 0
        locT = 0
        size = 0
        print 'No T-line found'
    else:
        cv2.rectangle(cropedcolor,top_leftT, bottom_rightT, 255, 2)    
else:
    cv2.rectangle(cropedcolor,top_leftT, bottom_rightT, 255, 2)

cv2.imwrite('res.png',cropedcolor)  
#print avg_C
print avg_T
#print avg_bg


ratio = avg_T/avg_C

print "ratio:", ratio