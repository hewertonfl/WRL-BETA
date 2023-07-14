
import cv2
from ultralytics import YOLO
import numpy as np
import pandas as pd
import math
import os

def calc_center(mask):
    M = cv2.moments(mask)
    cX = int(M["m10"] / M["m00"])
    cY = int(M["m01"] / M["m00"])
    center = cX,cY
    print("Centro do contorno: ({}, {})".format(cX, cY))
    return center
    
def sort_holes(mask):
    print(mask)

def calc_diameter(mask):
    area = cv2.contourArea(mask)
    diameter = round(math.sqrt((area*4)/(math.pi)),2)
    return diameter

def segment(image):
    # Load the YOLOv8 model
    root = os.path.dirname(__file__)
    path = '../weights/best.onnx'
    path2 = '/home/hewerton/Documentos/WRL_BETA/weights/best.onnx' #os.path.dirname(os.path.join(root,path)

    model = YOLO(path2,task='segment')
    # results = model(os.path.dirname(os.path.abspath(__file__))+'/test.png')
    # img = cv2.imread(os.path.dirname(os.path.abspath(__file__))+'/test.png')
    results = model(image)
    diameters = np.array([])

    for result in results:
        for i in range(len(result)):
            mask = result[i].masks.xy
            mask = np.array(mask, np.int32)
            diameter = calc_diameter(mask)
            np.append(diameters,diameter)
            print(diameter)
            text_center = calc_center(mask)[0]-10,calc_center(mask)[1]+10            
            mask = mask.reshape((-1,1,2))
            annotated_frame = cv2.drawContours(image,[mask],-1,(0,255,255),5)
            annotated_frame = cv2.putText(annotated_frame,str(diameter),text_center ,cv2.FONT_HERSHEY_SIMPLEX,1,(0, 255, 0),3,cv2.LINE_AA )

    return annotated_frame,diameters,True

if __name__ =='__main__':
    root = os.path.dirname('WRLSegmentationScreen.py')
    # path = '../weights/best.onnx'
    # print(os.path.join(root,path))
    print(root)