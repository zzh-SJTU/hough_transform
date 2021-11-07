#!/usr/bin/env python3
import cv2
import numpy as np
import math


def detect_edges(image):
  """Find edge points in a grayscale image.

  Args:
  - image (2D uint8 array): A grayscale image.

  Return:
  - edge_image (2D float array): A heat map where the intensity at each point
      is proportional to the edge magnitude.
  """
  image = image.astype(np.float64)
  kernel_x_1 = np.array(([-1,0,1],[-2,0,2],[-1,0,1]),dtype = np.float64)
  kernel_y_1 = np.array(([1,2,1],[0,0,0],[-1,-2,-1]),dtype = np.float64)
  detect_x_1 = cv2.filter2D(image, -1, kernel_x_1)
  detect_y_1 = cv2.filter2D(image, -1, kernel_y_1)
  detect_edge = detect_x_1 * detect_x_1 + detect_y_1*detect_y_1
  detect_edge = np.sqrt(detect_edge)
  
  return detect_edge

def hough_circles(edge_image, ther, radius_values):
  """Threshold edge image and calculate the Hough transform accumulator array.

  Args:
  - edge_image (2D float array): An H x W heat map where the intensity at each
      point is proportional to the edge magnitude.
  - edge_thresh (float): A threshold on the edge magnitude values.
  - radius_values (1D int array): An array of R possible radius values.

  Return:
  - thresh_edge_image (2D bool array): Thresholded edge image indicating
      whether each pixel is an edge point or not.
  - accum_array (3D int array): Hough transform accumulator array. Should have
      shape R x H x W.
  """
  for i in range(edge_image.shape[0]):
     
      for j in range(edge_image.shape[1]):
          if edge_image[i][j] < ther:
              edge_image[i][j] = 0
          else:
              edge_image[i][j] = 255
  accum_array = np.zeros((len(radius_values),edge_image.shape[0],edge_image.shape[1]))
  for i in range(edge_image.shape[0]):
     for j in range(edge_image.shape[1]):
         if edge_image[i][j] != 0:
            for r in range(len(radius_values)):
                x_down = max(i-2*radius_values[r],0)
                x_up = min(i+2*radius_values[r],edge_image.shape[0])
                y_down = max(j-2*radius_values[r],0)
                y_up = min(j+2*radius_values[r],edge_image.shape[1])
                for a in range(x_down,x_up):
                    for b in range(y_down,y_up):
                        temp =math.sqrt((a-i)*(a-i)+(b-j)*(b-j))
                        if round(temp-radius_values[r])==0:
                            accum_array[r][a][b] += 1
  
  
  return edge_image, accum_array
                          
      
              
  
    


def find_circles(image, accum_array, radius_values, hough_thresh):
  """Find circles in an image using output from Hough transform.

  Args:
  - image (3D uint8 array): An H x W x 3 BGR color image. Here we use the
      original color image instead of its grayscale version so the circles
      can be drawn in color.
  - accum_array (3D int array): Hough transform accumulator array having shape
      R x H x W.
  - radius_values (1D int array): An array of R radius values.
  - hough_thresh (int): A threshold of votes in the accumulator array.

  Return:
  - circles (list of 3-tuples): A list of circle parameters. Each element
      (r, y, x) represents the radius and the center coordinates of a circle
      found by the program.
  - circle_image (3D uint8 array): A copy of the original image with detected
      circles drawn in color.
  """
  
  list_1 = []
  for r in range(len(radius_values)):
      radius = radius_values[r]
      for a in range(image.shape[0]):
          for b in range(image.shape[1]):
              if accum_array[r][a][b]>hough_thresh:
                  list_1.append([radius,a,b,accum_array[r][a][b],1])              
  list_final= []
  #非极大值抑制
  for i in range(len(list_1)):
      r = list_1[i][0]
      x = list_1[i][1]
      y = list_1[i][2]  
      value = list_1[i][3] 
      for j in range(len(list_1)):
          if j == i:
              continue
          r1 = list_1[j][0]
          x1 = list_1[j][1]
          y1 = list_1[j][2] 
          value1 = list_1[j][3]
          flag_r = abs(r-r1)
          if flag_r<3 and (x-x1)*(x-x1)+(y-y1)*(y-y1)<10:
              if value1 > value:
                  list_1[i][4] = 0
              else:
                  list_1[j][4] = 0   
          else:
              continue
  for item in list_1:
      if item[4] == 1:
          list_final.append((item[0],item[1],item[2]))
  circles = list_final
            
  circle_image = image  
  for item in list_final:
      cv2.circle(circle_image,(item[2],item[1]),item[0], color=(0, 255, 0), thickness=2)
                
  return  circles,circle_image
              
   #TODO

img = cv2.imread('data/' + 'coins' + '.png', cv2.IMREAD_COLOR)
gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
edge = detect_edges(gray_image)

cv2.imwrite('output/'   + "edge.png", edge )
r_range =[]
for i in range(10):
    r_range.append(i+22)  
thresh_edge_image, accum_array = hough_circles(edge,300,r_range)
cv2.imwrite('output/'   + "coins_edges.png", thresh_edge_image )
circles,circle_image = find_circles(img, accum_array, r_range, 100) 
cv2.imwrite('output/'   + "coins_circles.png", circle_image )

