from time import sleep
import cv2
import numpy as np
import utils
from datetime import datetime


########################################################################
webCamFeed = False

pathImage = "10.jpg"
threshold =130

# REMEMBER TO ROTATE THE CAMERA IN ADVANCED SETTINGS IN YOUR WEBCAM SERVER
cap = cv2.VideoCapture(0)
address = "http://192.168.1.4:8080/video"
cap.open(address)

cap.set(10,160)
heightImg = 720
widthImg  = 500
questions=15
choices=5
ans= [0,0,2,0,0,2,4,1,2,1,1,2,3,4,0]
########################################################################



while True:
    if webCamFeed:
        success, img = cap.read()
    else:
        img = cv2.imread(pathImage)
    # sleep(1.0)
    img = cv2.resize(img, (widthImg, heightImg)) # RESIZE IMAGE
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) # CONVERT IMAGE TO GRAY SCALE
    imgBlur = cv2.GaussianBlur(imgGray, (5, 5), 1) # ADD GAUSSIAN BLUR
    imgCanny = cv2.Canny(imgBlur,85,255) # APPLY CANNY 

    try:
        # FIND ALL COUNTOURS AND WARP
        contours, hierarchy = cv2.findContours(imgCanny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE) # FIND ALL CONTOURS
        rectCon = utils.rectContour(contours) # FILTER FOR RECTANGLE CONTOURS
        if(len(rectCon)==1):
            biggestPoints= utils.getCornerPoints(rectCon[0]) # GET CORNER POINTS OF THE BIGGEST RECTANGLE
            biggestPoints=utils.reorder(biggestPoints) # REORDER FOR WARPING
            pts1 = np.float32(biggestPoints) # PREPARE POINTS FOR WARP
            pts2 = np.float32([[0, 0],[widthImg, 0], [0, heightImg],[widthImg, heightImg]]) # PREPARE POINTS FOR WARP
            matrix = cv2.getPerspectiveTransform(pts1, pts2) # GET TRANSFORMATION MATRIX
            imgWarped = cv2.warpPerspective(img, matrix, (widthImg, heightImg)) # APPLY WARP PERSPECTIVE       
            # REPEAT PROCESS
            imgFinal = imgWarped.copy()
            imgBlank = np.zeros((heightImg,widthImg, 3), np.uint8) # CREATE A BLANK IMAGE FOR TESTING DEBUGGING IF REQUIRED
            imgGray = cv2.cvtColor(imgWarped, cv2.COLOR_BGR2GRAY) # CONVERT IMAGE TO GRAY SCALE
            imgBlur = cv2.GaussianBlur(imgGray, (5, 5), 1) # ADD GAUSSIAN BLUR
            imgCanny = cv2.Canny(imgBlur,10,70) # APPLY CANNY 
            imgContours = imgWarped.copy() # COPY IMAGE FOR DISPLAY PURPOSES
            imgBigContour = imgWarped.copy() # COPY IMAGE FOR DISPLAY PURPOSES
            contours, hierarchy = cv2.findContours(imgCanny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE) # FIND ALL CONTOURS
            cv2.drawContours(imgContours, contours, -1, (0, 255, 0), 5) # DRAW ALL DETECTED CONTOURS
            rectCon = utils.rectContour(contours) # FILTER FOR RECTANGLE CONTOURS
            biggestPoints= utils.getCornerPoints(rectCon[0]) # GET CORNER POINTS OF THE BIGGEST RECTANGLE
            gradePoints = utils.getCornerPoints(rectCon[1]) # GET CORNER POINTS OF THE SECOND BIGGEST RECTANGLE
        else:
            imgWarped =img.copy() 
            imgFinal = imgWarped.copy()
            imgBlank = np.zeros((heightImg,widthImg, 3), np.uint8) # CREATE A BLANK IMAGE FOR TESTING DEBUGGING IF REQUIRED
            imgGray = cv2.cvtColor(imgWarped, cv2.COLOR_BGR2GRAY) # CONVERT IMAGE TO GRAY SCALE
            imgBlur = cv2.GaussianBlur(imgGray, (5, 5), 1) # ADD GAUSSIAN BLUR
            imgCanny = cv2.Canny(imgBlur,85,255) # APPLY CANNY 
            imgContours = imgWarped.copy() # COPY IMAGE FOR DISPLAY PURPOSES
            imgBigContour = imgWarped.copy() # COPY IMAGE FOR DISPLAY PURPOSES
            contours, hierarchy = cv2.findContours(imgCanny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE) # FIND ALL CONTOURS
            cv2.drawContours(imgContours, contours, -1, (0, 255, 0), 5) # DRAW ALL DETECTED CONTOURS
            rectCon = utils.rectContour(contours) # FILTER FOR RECTANGLE CONTOURS
            biggestPoints= utils.getCornerPoints(rectCon[0]) # GET CORNER POINTS OF THE BIGGEST RECTANGLE
            gradePoints = utils.getCornerPoints(rectCon[1]) # GET CORNER POINTS OF THE SECOND BIGGEST RECTANGLE
            # print('biggestPoints',biggestPoints)
        

        if biggestPoints.size != 0 and gradePoints.size != 0:

            # BIGGEST RECTANGLE WARPING
            # print('biggest points before reorder',biggestPoints)
            biggestPoints=utils.reorder(biggestPoints) # REORDER FOR WARPING
            # print('biggest points after reorder',biggestPoints)
            cv2.drawContours(imgBigContour, biggestPoints, -1, (0, 255, 0), 20) # DRAW THE BIGGEST CONTOUR
            pts1 = np.float32(biggestPoints) # PREPARE POINTS FOR WARP
            pts2 = np.float32([[0, 0],[widthImg, 0], [0, heightImg],[widthImg, heightImg]]) # PREPARE POINTS FOR WARP
            # print('pts1, pts2', pts1,pts2)
            matrix = cv2.getPerspectiveTransform(pts1, pts2) # GET TRANSFORMATION MATRIX
            imgWarpColored = cv2.warpPerspective(imgWarped, matrix, (widthImg, heightImg)) # APPLY WARP PERSPECTIVE

            # SECOND BIGGEST RECTANGLE WARPING
            cv2.drawContours(imgBigContour, gradePoints, -1, (0, 255, 0), 20) # DRAW THE BIGGEST CONTOUR
            gradePoints = utils.reorder(gradePoints) # REORDER FOR WARPING
            ptsG1 = np.float32(gradePoints)  # PREPARE POINTS FOR WARP
            ptsG2 = np.float32([[0, 0], [700, 0], [0, 150], [700, 150]])  # PREPARE POINTS FOR WARP
            matrixG = cv2.getPerspectiveTransform(ptsG1, ptsG2)# GET TRANSFORMATION MATRIX
            imgGradeDisplay = cv2.warpPerspective(imgWarped, matrixG, (325, 150)) # APPLY WARP PERSPECTIVE
            
            # APPLY THRESHOLD
            imgWarpGray = cv2.cvtColor(imgWarpColored,cv2.COLOR_BGR2GRAY) # CONVERT TO GRAYSCALE
            imgThresh = cv2.threshold(imgWarpGray, threshold, 255,cv2.THRESH_BINARY_INV )[1] # APPLY THRESHOLD AND INVERSE
            boxes = utils.splitBoxes(imgThresh) # GET INDIVIDUAL BOXES
            countR=0
            countC=0
            myPixelVal = np.zeros((questions,choices)) # TO STORE THE NON ZERO VALUES OF EACH BOX
            kernelErosion = np.ones((10,10),np.uint8)
            
            # APPLY EROSION METHOD AND FIND THE MOST NON-ZERO AREA
            for image in boxes:
                image=cv2.erode(image,kernelErosion,iterations=1)
                totalPixels = cv2.countNonZero(image)
                myPixelVal[countR][countC]= totalPixels
                countC += 1
                if (countC==choices):countC=0;countR +=1

            # FIND THE USER ANSWERS AND PUT THEM IN A LIST
            myIndex=[]
            for x in range (0,questions):
                userChoices = []
                arr = myPixelVal[x]
                averageVal=250


                # Find user choices
                for z in range(0,5):
                    if (arr[z] >averageVal):
                        userChoices.append(arr[z])
                
                if (len(userChoices) == 0 ): # No choice
                    myIndex.append(5)
                elif (len(userChoices) >= 2 ): # More than one choice
                    myIndex.append(6)
                else: # One choice
                    myIndexVal = np.where(arr == np.amax(arr))
                    myIndex.append(myIndexVal[0][0])
            # print(myIndex)
            # COMPARE THE VALUES TO FIND THE CORRECT ANSWERS
            grading=[]
            for x in range(0,questions):
                if ans[x] == myIndex[x]:
                    grading.append(1)
                else:grading.append(0)
            score = (sum(grading)/questions)*100 # FINAL GRADE

            # DISPLAYING ANSWERS
            utils.showAnswers(imgWarpColored,myIndex,grading,ans) # DRAW DETECTED ANSWERS
            utils.drawGrid(imgWarpColored) # DRAW GRID
            imgRawDrawings = np.zeros_like(imgWarpColored) # NEW BLANK IMAGE WITH WARP IMAGE SIZE
            utils.showAnswers(imgRawDrawings, myIndex, grading, ans) # DRAW ON NEW IMAGE
            invMatrix = cv2.getPerspectiveTransform(pts2, pts1) # INVERSE TRANSFORMATION MATRIX
            imgInvWarp = cv2.warpPerspective(imgRawDrawings, invMatrix, (widthImg, heightImg)) # INV IMAGE WARP

            # DISPLAY GRADE
            imgRawGrade = np.zeros_like(imgGradeDisplay,np.uint8) # NEW BLANK IMAGE WITH GRADE AREA SIZE
            cv2.putText(imgRawGrade,str(int(score))+"%",(70,100)
                        ,cv2.FONT_HERSHEY_COMPLEX,2,(0,0,255),3) # ADD THE GRADE TO NEW IMAGE
            invMatrixG = cv2.getPerspectiveTransform(ptsG2, ptsG1) # INVERSE TRANSFORMATION MATRIX
            imgInvGradeDisplay = cv2.warpPerspective(imgRawGrade, invMatrixG, (widthImg, heightImg)) # INV IMAGE WARP
            # SHOW ANSWERS AND GRADE ON FINAL IMAGE
            imgFinal = cv2.addWeighted(imgFinal, 1, imgInvWarp, 1,0)
            imgFinal = cv2.addWeighted(imgFinal, 1, imgInvGradeDisplay, 1,0)

            # IMAGE ARRAY FOR DISPLAY
            imageArray = ([img,imgGray,imgCanny,imgContours],
                          [imgBigContour,imgThresh,imgWarpColored,imgFinal])
            cv2.imshow("Final Result", imgFinal)
    except:
        imageArray = ([img,imgGray,imgCanny,imgContours],
                      [imgBlank, imgBlank, imgBlank, imgBlank])

    # LABELS FOR DISPLAY
    lables = [["Original","Gray and Warped","Edges","Contours"],
              ["Biggest Contour","Threshold","Display Answers","Final"]]

    stackedImage = utils.stackImages(imageArray,0.5,lables)
    cv2.imshow("Result",stackedImage)
    # SAVE IMAGE WHEN 's' key is pressed
    now = datetime.now()
    dt_string = now.strftime("%d-%m-%Y-%H-%M-%S")
    if cv2.waitKey(1) & 0xFF == ord('s'):
        cv2.imwrite("C:/Users/Tri Hoang/Desktop/XLA/model/Optical-Mark-Recognition-OPENCV/__pycache__/myImage"+dt_string+".jpg",imgFinal)
        cv2.rectangle(stackedImage, ((int(stackedImage.shape[1] / 2) - 230), int(stackedImage.shape[0] / 2) + 50),
                      (1100, 350), (0, 255, 0), cv2.FILLED)
        cv2.putText(stackedImage, "Scan Saved", (int(stackedImage.shape[1] / 2) - 200, int(stackedImage.shape[0] / 2)),
                    cv2.FONT_HERSHEY_DUPLEX, 3, (0, 0, 255), 5, cv2.LINE_AA)
        cv2.imshow('Result', stackedImage)
        cv2.waitKey(300)
