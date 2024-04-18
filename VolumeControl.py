import cv2
import time
import mediapipe as mp
import math

from ctypes import cast, POINTER

import numpy
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import numpy as np

wCam,hCam = 640,480

cap = cv2.VideoCapture(0)

mpHands = mp.solutions.hands
hands = mpHands.Hands()
mpDraw=mp.solutions.drawing_utils


devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
# volume.GetMute()
# volume.GetMasterVolumeLevel()
volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]
volBar =0

cap.set(3,wCam)
cap.set(4,hCam)

# cTime = 0
pTime = 0

while True:
    success, img = cap.read()
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)
    # print(results.multi_hand_landmarks)

    if results.multi_hand_landmarks:
        for handlms in results.multi_hand_landmarks:
            lmList = []
            for id,lm in enumerate(handlms.landmark):
                # print(id,lm)
                h,w,c = img.shape
                cx,cy = int(lm.x*w) , int(lm.y*h)
                # if id==4 or id==8:
                lmList.append((id,cx,cy))
                if id==4 or id==8:
                    cv2.circle(img,(cx,cy),15,(255,0,255),cv2.FILLED)
                    # if len(lmList) != 0:
                        # print(lmList[0][2])
                    # print(lmList)
            if len(lmList) != 0:
                x1,y1 = lmList[4][1], lmList[4][2]
                x2,y2 = lmList[8][1], lmList[8][2]
                cx,cy = (x1+x2) //2 ,(y1+y2)//2
                cv2.line(img, (x1,y1), (x2,y2), (0, 0, 1), 3)
                length = math.hypot(x2-x1,y2-y1)
                # print(length)
                cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)
                vol = numpy.interp(length,[50,300],[minVol,maxVol])
                volBar = numpy.interp(length,[50,300],[400,150])
                volPer = numpy.interp(length,[50,300],[0,100])

                volume.SetMasterVolumeLevel(vol,None)

                # print(vol)


                if length<50:
                    cv2.circle(img, (cx, cy), 15, (0, 255, 0), cv2.FILLED)

            cv2.rectangle(img,(50,150),(85,400),(255,0,0),3)
            cv2.rectangle(img,(50,int(volBar)),(85,400),(255,0,0),cv2.FILLED)
            cv2.putText(img, f'{(int(volPer))} %', (40, 450), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)

            # if id == 8:
                #     print(id, cx, cy)
                #     cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)

            mpDraw.draw_landmarks(img, handlms, mpHands.HAND_CONNECTIONS)

    cTime=time.time()
    fps = 1/(cTime-pTime)
    pTime=cTime

    cv2.putText(img,f'Fps: {(int(fps))}',(40,50),cv2.FONT_HERSHEY_PLAIN,3,(255,0,0),3)

    cv2.imshow("Image", img)
    cv2.waitKey(1)
