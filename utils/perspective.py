import numpy as np
import cv2
import os
offsetX = 450#590
offsetY = 0#170
im_dst_shape = (1080, 1080)

root = os.path.dirname(os.path.abspath(__file__))
imagePath = os.path.join(root,'../test.png')
imageBasePath = os.path.join(root,'../perspective_images/')

def sort_array_by_second_element(arr):
    # Obtendo os índices após a ordenação da segunda coluna
    indices_sorted = np.argsort(arr[:, 1])

    # Reorganizando o array de acordo com a ordenação dos índices
    sorted_array = arr[indices_sorted]

    return sorted_array 
	  
def four_points_transform(image, pts):
    # Read source image. (Imagem a ser transformada)
    im_src = image
    # Source image's points
    pts_src = pts

    # Read destination image. (Imagem de modelo para a transformação)
    im_dst = cv2.imread(imageBasePath+'sqr.png')
    im_dst = im_dst[170:910, 590:1330]
    # Destination images's points.
    pts_dst = np.array([[734-offsetX,722-offsetY],[734-offsetX,317-offsetY],[1139-offsetX,316-offsetY],[1139-offsetX,723-offsetY]]) 

    # Calculate Homography
    h, status = cv2.findHomography(pts_src, pts_dst)

    # Warp source image to destination based on homography
    im_out = cv2.warpPerspective(im_src, h, (im_dst_shape[1],im_dst_shape[0]))
    return im_out  
     
def six_points_transform(image, pts):
    # Read source image. (Imagem a ser transformada)
    im_src = image
    # Source image's points
    pts_src = sort_array_by_second_element(pts)

    # Read destination image. (Imagem de modelo para a transformação)
    im_dst = cv2.imread(imageBasePath+'hex.jpg')
    im_dst = im_dst[156:924, 576:1344]
    # Destination images's points.
    pts_dst = np.array([[1260-offsetX,550-offsetY],[1112-offsetX,298-offsetY],[1112-offsetX,802-offsetY],[820-offsetX,298-offsetY],[672-offsetX,550-offsetY],[820-offsetX,802-offsetY]])
    pts_dst =sort_array_by_second_element(pts_dst)

    # Calculate Homography
    h, status = cv2.findHomography(pts_src, pts_dst)

    # Warp source image to destination based on homography
    im_out = cv2.warpPerspective(im_src, h, (im_dst_shape[1],im_dst_shape[0]))
    return im_out
    
def five_points_transform(image, pts):
    # Read source image. (Imagem a ser transformada)
    im_src = image
    # Source image's points
    pts_src = sort_array_by_second_element(pts)

    # Read destination image. (Imagem de modelo para a transformação)
    im_dst = cv2.imread(imageBasePath+'pen.png')
    im_dst = im_dst[170:910, 590:1330]
    # Destination images's points.
    pts_dst = np.array([[643-offsetX, 432-offsetY],[965-offsetX,199-offsetY],[1286-offsetX,432-offsetY],[1163-offsetX,810-offsetY],[767-offsetX,810-offsetY]])

    # Calculate Homography
    h, status = cv2.findHomography(pts_src, pts_dst)

    # Warp source image to destination based on homography
    im_out = cv2.warpPerspective(im_src, h, (im_dst_shape[1],im_dst_shape[0]))
    print(im_out)
    print(im_out)
    print(im_out)
    return im_out
	
def do(image, centros):
    if(len(centros)==6):
        pts = np.float32([(centros[0]), (centros[1]), (centros[2]), (centros[3]), (centros[4]), (centros[5])])
        # apply the four points tranform to obtain a "birds eye view" of the image   
        warped = six_points_transform(image, pts)
    elif(len(centros)==4):
        pts = np.float32([(centros[0]), (centros[1]), (centros[2]), (centros[3])])
        # apply the four points tranform to obtain a "birds eye view" of the image   
        warped = four_points_transform(image, pts)
    elif(len(centros)==5):
        pts = np.float32([(centros[0]), (centros[1]), (centros[2]), (centros[3]), (centros[4])])
        # apply the four points tranform to obtain a "birds eye view" of the image   
        warped = five_points_transform(image, pts)
    else:
        # apply the four point tranform to obtain a "birds eye view" of the image   
        warped = image
    
    
    #cv2.imshow("Original", image)
    
    return(warped)
    
# def sort_holes(image,centers,arrayToOrder,reference):
#     y,x,_ = image.shape
#     y//=2
#     x//=2
#     angles = np.array([])

#     # Calcule dos ângulos
#     for i,center in enumerate(centers):
#         angles= np.append(angles,np.arctan(abs(y-center[1])/abs(x-center[0])))
#     angles = np.abs(angles-reference)
#     print('Angulos Calculados:',angles)
#     primary_index = int(np.argmin(angles))
#     print(primary_index)
#     print('\nArray Antigo:\n',arrayToOrder)
#     slice1 = arrayToOrder[primary_index:]
#     slice2 = arrayToOrder[0:primary_index]
#     # print('slice1:',slice1)
#     # print('slice2:',slice2)
#     result = np.concatenate((slice1,slice2),axis=0)
#     print('\nArray Ordenado\n',result)

#     return result
  

# img = cv2.imread(imagePath, 1)
# points=np.array([[303,116],[417,111],[250,248],[477,241],[310,377],[424,373]])
# img = six_points_transform(img,points)
# print(img.shape)
# cv2.imshow('image', img)
# cv2.waitKey(0)
# cv2.destroyAllWindows()
# array = np.array([[303,114],[250,245],[309,373],[417,109],[421,371],[475,238]])
# array2 = np.array([[303,114],[250,245],[309,373],[417,109],[421,371],[475,238]])
# #print(sort_array_by_second_element(array))
# sort_holes(img,array,array2,0.5)

# # importing the module
# import cv2
   
# # function to display the coordinates of
# # of the points clicked on the image 
# def click_event(event, x, y, flags, params):
  
#     # checking for left mouse clicks
#     if event == cv2.EVENT_LBUTTONDOWN:
  
#         # displaying the coordinates
#         # on the Shell
#         print(x, ' ', y)
  
#         # displaying the coordinates
#         # on the image window
#         font = cv2.FONT_HERSHEY_SIMPLEX
#         cv2.putText(img, str(x) + ',' +
#                     str(y), (x,y), font,
#                     1, (255, 0, 0), 2)
#         cv2.imshow('image', img)
  
#     # checking for right mouse clicks     
#     if event==cv2.EVENT_RBUTTONDOWN:
  
#         # displaying the coordinates
#         # on the Shell
#         print(x, ' ', y)
  
#         # displaying the coordinates
#         # on the image window
#         font = cv2.FONT_HERSHEY_SIMPLEX
#         b = img[y, x, 0]
#         g = img[y, x, 1]
#         r = img[y, x, 2]
#         cv2.putText(img, str(b) + ',' +
#                     str(g) + ',' + str(r),
#                     (x,y), font, 1,
#                     (255, 255, 0), 2)
#         cv2.imshow('image', img)
  
# # driver function
# if __name__=="__main__":
  
#     # reading the image
#     img = cv2.imread(imagePath, 1)
  
#     # displaying the image
#     cv2.imshow('image', img)
  
#     # setting mouse handler for the image
#     # and calling the click_event() function
#     cv2.setMouseCallback('image', click_event)
  
#     # wait for a key to be pressed to exit
#     cv2.waitKey(0)
  
#     # close the window
#     cv2.destroyAllWindows()
