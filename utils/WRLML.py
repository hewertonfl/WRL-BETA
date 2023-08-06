
import cv2
from ultralytics import YOLO
from ultralytics.yolo.utils.ops import masks2segments
import numpy as np
import pandas as pd
import math
import os
import perspective

def normalize_masks(mask):
    segments = []
    for x in mask.astype('uint8'):
        c = cv2.findContours(x, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
        if c:
            c = np.array(c[np.array([len(x) for x in c]).argmax()]).reshape(-1, 2)
        else:
            c = np.zeros((0, 2))  # no segments found
        segments.append(c.astype('float32'))
    return segments

def calc_centers(results):
    centers = np.empty((0, 2))
    for i in range(len(results)):
        mask = results[i].data
        mask = masks2segments(mask)
        mask = np.array(mask, np.int32)

        M = cv2.moments(mask)
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])
        center = cX,cY
        centers = np.vstack((centers,center))
    return centers

def calc_diameters(results):
    diameters = np.array([])
    for i in range(len(results)):
        mask = results[i].data
        mask = masks2segments(mask)
        mask = np.array(mask, np.int32)

        area = cv2.contourArea(mask)
        diameter = round(math.sqrt((area*4)/(math.pi)),2)
        diameters = np.append(diameters,diameter)

    return diameters

def order(image,centers,compass):
    """ Função que ordena um array de acordo com o ângulo
        params:
            - Image é um numpy array correspondente a imagem
            - Centers é um numpy array com as coordenadas dos centros
            - Compass é um valor de ângulo em radianos
    """
    y,x,_ = image.shape
    y/=2
    x/=2
    angles = np.array([])
    order = np.array([])
    pi = np.pi

    # Calculo dos ângulos
    for center in centers:
        deltaX=center[0]-x
        deltaY=center[1]-y
        angle= np.arctan(deltaY/deltaX)

        # Quadrante 1
        if(deltaY<0 and deltaX>0):
            angle = angle*(-1)
            print('Q1:',angle*180/pi)

        # Quadrante 2
        elif(deltaY<0 and deltaX<0):
            angle = pi-angle
            print('Q2:',angle*180/pi)
        
        # Quadrante 3
        elif(deltaY>0 and deltaX<0):
            angle = angle+pi
            print('Q3:',angle*180/pi)
        
        # Quadrante 4
        elif(deltaY>0 and deltaX>0):
            angle = angle*(-1)+2*pi
            print('Q4:',angle*180/pi)
        

        angles = np.append(angles,angle)

    # Ordenação
    orderAux = np.argsort(angles)
    angleRef = np.abs(angles[orderAux]-compass)
    angleIndex = int(np.argmin(angleRef))

    slice_1 = orderAux[angleIndex:]
    slice_2 = orderAux[0:angleIndex]

    order = np.concatenate((slice_1,slice_2))
 
    return order


def segment():
    # Paths
    root = os.path.dirname(os.path.abspath(__file__))
    weighstPath = os.path.join(root,'../weights/best.onnx')
    imagePath = os.path.join(root,'../test.png')

    # Load the YOLOv8 model
    model = YOLO(weighstPath,task='segment')
    results = model(imagePath)[0]
    image = cv2.imread(imagePath)
    image = cv2.resize(image, (640,640), interpolation = cv2.INTER_AREA)
    #results = model(image)

    masks = results.masks
    diameters = calc_diameters(masks)
    centers = calc_centers(masks)
    
    # Encontrando o indice do diametro máximo 
    d_max_index = np.argmax(diameters)
    d_max = np.array(diameters[d_max_index])
    d_max_mask = masks.data[d_max_index]
    center_max = centers[d_max_index]

    # Removendo os elementos correspondentes ao diâmetro máximo
    centers = np.delete(centers,d_max_index,axis=0)
    masks.data = np.delete(masks.data,d_max_index,axis=0)

    angle = 1.047
    holes_order = order(image,centers,angle)
    holes_order_list = holes_order.tolist()

    #Ordenação das máscaras e centros
    masks.data = masks.data[holes_order_list]
    centers = centers[holes_order_list]
    
    # Adição do maior bocal
    maskAux = np.copy(masks.data.cpu().numpy())
    centers2 = np.copy(centers)
    masks.data = np.insert(masks.data, 0, d_max_mask, axis=0)
    centers = np.insert(centers,0, center_max, axis=0)

    # Transformação das máscaras de acordo com a perspectiva
    maskAux = np.moveaxis(maskAux, 0, -1) # masks, (H, W, N)
    print(maskAux.shape)
    # masksPerspective = []

    # centers = calc_centers(masks)
    # diameters = calc_diameters(masks)

    # Exibição da imagem
    image = cv2.resize(image, (640,640), interpolation = cv2.INTER_AREA)
    #image = perspective.six_points_transform(image,centers2)
    for i,mask in enumerate(masks):
        mask = mask.data.numpy()
        #mask = np.array([perspective.six_points_transform(maskAux[i],centers2)],np.float32)
        mask = normalize_masks(mask)
        mask = np.array(mask,np.int32)
        if i != 0:
            center = centers[i]
            # text_center = int(center[0])-10,int(center[1])+10
            text = str(i)
            annotated_frame = cv2.drawContours(image,[mask],-1,(0,255,255),4)
            # annotated_frame = cv2.putText(image,text,text_center ,cv2.FONT_HERSHEY_SIMPLEX,1,(0, 255, 0),2,cv2.LINE_AA )
        else:
            annotated_frame = cv2.drawContours(image,[mask],-1,(0,255,255),4)

    annotated_frame = cv2.resize(image, (640,640), interpolation = cv2.INTER_AREA)
    cv2.imshow('teste',annotated_frame)
    cv2.waitKey(0)    

    # return annotated_frame,diameters,True

if __name__ =='__main__':
    segment()