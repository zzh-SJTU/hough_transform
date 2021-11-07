#!/usr/bin/env python3
import cv2
import numpy as np
import sys
import math

sys.setrecursionlimit(10000)
def binarize(gray_image, thresh_val):
    binary_image = gray_image
    for i in range(binary_image.shape[0]):
        for j in range(binary_image.shape[1]):
            if binary_image[i][j]<thresh_val:
                binary_image[i][j]=0
            else:
                binary_image[i][j]= 255
  # TODO: 255 if intensity >= thresh_val else 0
  
    return binary_image

def label(binary_image):
    labeled_image = np.zeros((binary_image.shape[0],binary_image.shape[1]))
    for i in range(binary_image.shape[0]):
        for j in range(binary_image.shape[1]):
            if binary_image[i][j] >0:
                labeled_image[i][j] = -1
    def search(LB,label,i,j):
        LB[i][j] = label
        for m in [i-1,i,i+1]:
            for n in [j-1,j,j+1]:
                if LB[m][n] == -1:
                    search(LB, label, m, n)
    def find_comp(LB, label):
        for i in range(LB.shape[0]):
            for j in range(LB.shape[1]):
                if LB[i][j] == -1:
                    label+=40
                    search(LB,label,i,j)

    def recursive(LB, label):
        find_comp(LB,label)
        return LB
    label = 0
    labeled_image = recursive(labeled_image, label)
  # TODO
    return labeled_image

def get_attribute(labeled_image):
    x_dic = {}
    y_dic = {}
    label_list =[]
    for i in range(labeled_image.shape[0]):
        for j in range(labeled_image.shape[1]):
            if labeled_image[i][j]>0:
                if labeled_image[i][j] not in label_list:
                    label_list.append(labeled_image[i][j])
                    x_dic[labeled_image[i][j]] = []
                    y_dic[labeled_image[i][j]] = []
                    x_dic[labeled_image[i][j]].append(j)
                    y_dic[labeled_image[i][j]].append(labeled_image.shape[0]-i)
                else:
                    x_dic[labeled_image[i][j]].append(j)
                    y_dic[labeled_image[i][j]].append(labeled_image.shape[0]-i)
    
    center_x = {}
    center_y = {}
    for key, item in x_dic.items():
        center_x[key] = sum(item)/len(item)
    
    for key, item in y_dic.items():
        center_y[key] = sum(item)/len(item)
    x_dic_new ={}
    y_dic_new ={}
    for lb in label_list:
        origin_new_x = center_x[lb]
        origin_new_y = center_y[lb]
        x_dic_new[lb]=[]
        y_dic_new[lb]=[]
        for x in x_dic[lb]:
            x_dic_new[lb].append(x-origin_new_x)
        for y in y_dic[lb]:
            y_dic_new[lb].append(y-origin_new_y)                  
    ori_dict = {}
    round_dict ={}
    for lb in label_list:
        a=0
        b=0
        c=0
        if len(x_dic_new[lb]) < 20:
            continue
        for i in range(len(x_dic_new[lb])):
            a += x_dic_new[lb][i]*x_dic_new[lb][i]
            b += 2*x_dic_new[lb][i]*y_dic_new[lb][i]
            c += y_dic_new[lb][i]*y_dic_new[lb][i]
        theta = math.atan2(b, (a-c))/2
        theta_1 = theta+ math.pi/2
        ori_dict[lb] = theta
        E_min = a*np.sin(theta)*np.sin(theta)-b*np.sin(theta)*np.cos(theta)+c*np.cos(theta)*np.cos(theta)
        E_max = a*np.sin(theta_1)*np.sin(theta_1)-b*np.sin(theta_1)*np.cos(theta_1)+c*np.cos(theta_1)*np.cos(theta_1)
        round_dict[lb] = E_min/E_max    
    
    attribute_list = []
    for lb in label_list:
        dic ={}
        dic['position'] = (center_x[lb],center_y[lb])
        dic['roundness'] = round_dict[lb]
        dic['ori'] =ori_dict[lb]
        attribute_list.append(dic)
    return attribute_list

def main(argv):
  img_name = argv[0]
  thresh_val = int(argv[1])

  img = cv2.imread('data/' + img_name + '.png', cv2.IMREAD_COLOR)
  gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

  binary_image = binarize(gray_image, thresh_val=thresh_val)
  labeled_image = label(binary_image)
  attribute_list = get_attribute(labeled_image)

  cv2.imwrite('output/' + img_name + "_gray.png", gray_image)
  cv2.imwrite('output/' + img_name + "_binary.png", binary_image)
  cv2.imwrite('output/' + img_name + "_labeled.png", labeled_image)
  print(attribute_list)


if __name__ == '__main__':
  main(sys.argv[1:])
