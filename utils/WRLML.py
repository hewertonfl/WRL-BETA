
import cv2
from ultralytics import YOLO
import numpy as np
import pandas as pd
import math
import os
from . import perspective

class detectorInterface:
    def __init__(self):
        self.root = os.path.dirname(os.path.abspath(__file__))
        self.weightPath = os.path.join(self.root,'../weights/best.onnx')
        self.imagePath = os.path.join(self.root,'../test.png')
        self.model = YOLO(self.weightPath,task='segment')

    def mask2segments(self,masks):
        segments = []
        for x in masks:
            x = x.astype('uint8')
            c = cv2.findContours(x, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
            c = np.array(c[np.array([len(x) for x in c]).argmax()]).reshape(-1, 2)
            segments.append(c.astype('float32'))
        return segments

    def getMaskPerspective(self,masks,centers):
        perspectiveMasks = []
        for i,mask in enumerate(masks):
            mask = perspective.six_points_transform(masks[i],centers)
            perspectiveMasks.append(mask)
        return perspectiveMasks

    def calc_centers(self,masks):   
        centers = np.empty((0, 2))
        segments = self.mask2segments(masks)
        for segment in segments:
            segment = np.array(segment, np.int32)
            M = cv2.moments(segment)
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            center = cX,cY
            centers = np.vstack((centers,center))
        return centers

    def calc_diameters(self,masks):
        diameters = np.array([])
        segments = self.mask2segments(masks)
        for segment in segments:
            mask = np.array(segment, np.int32)

            area = cv2.contourArea(mask)
            diameter = round(math.sqrt((area*4)/(math.pi)),2)
            diameters = np.append(diameters,diameter)
        return diameters

    def order(self,image,centers,compass):
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


    def segment(self,image):
        """Função que segmenta e calcula os diâmetros"""
        #image = cv2.imread(self.imagePath)
        image = cv2.resize(image, (768,768), interpolation = cv2.INTER_AREA)
        results = self.model.predict(image, save=False, imgsz=768, conf=0.25,max_det=7,task='segment')[0]

        masks = results.masks.data.cpu().numpy()
        diameters = self.calc_diameters(masks)
        centers = self.calc_centers(masks)
        
        # Encontrando o indice do diametro máximo 
        d_max_index = np.argmax(diameters)
        d_max_mask = masks[d_max_index]

        # Removendo os elementos correspondentes ao diâmetro máximo
        centers = np.delete(centers,d_max_index,axis=0)
        masks = np.delete(masks,d_max_index,axis=0)

        angle = np.pi/2
        holes_order = self.order(image,centers,angle)
        holes_order_list = holes_order.tolist()

        #Ordenação das máscaras e centros
        masks = masks[holes_order_list]
        centers = centers[holes_order_list]
        
        # Adição do maior bocal
        masks = np.insert(masks, 0, d_max_mask, axis=0)

        # Transformação perspectiva
        annotated_frame = perspective.six_points_transform(image,centers)
        perspectiveMasks =  self.getMaskPerspective(masks,centers)
        perspectiveMasks = np.array(perspectiveMasks)

        # Calculos dos diametros e centros
        perspectiveDiameters = self.calc_diameters(perspectiveMasks)
        perspectiveCenters = self.calc_centers(perspectiveMasks)

        # Exibição da imagem
        for i,mask in enumerate(perspectiveMasks):
            mask = np.array(mask,np.uint8)
            center = perspectiveCenters[i]
            text_center = int(center[0])-10,int(center[1])+10
            text = None if i == 0 else str(i)
            contour = cv2.findContours(mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)[0]
            annotated_frame = cv2.drawContours(annotated_frame,contour,-1,(0,255,255),4)
            annotated_frame = cv2.putText(annotated_frame,text,text_center ,cv2.FONT_HERSHEY_SIMPLEX,1,(0, 255, 0),2,cv2.LINE_AA )

        annotated_frame = cv2.resize(annotated_frame, (640,640), interpolation = cv2.INTER_AREA)
        # cv2.imshow('teste',annotated_frame)
        # cv2.waitKey(0)    

        return annotated_frame,perspectiveDiameters,True

if __name__ =='__main__':
    detect = detectorInterface().segment()