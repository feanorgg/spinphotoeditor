import cv2
import numpy as np
import math


def center_image(image):
    img = cv2.imread(image)

    left = 0
    right = 0
    top = 0
    bottom = 0

    height = img.shape[0]
    width = img.shape[1]

    print(height)
    print(width)

    base = img[0][0]

    i = 100
    while i < width:
        stop = False
        for j in range(height):
            if math.sqrt((int(img[j][i][0])-int(base[0]))**2 + (int(img[j][i][1])-int(base[1]))**2 + (int(img[j][i][2])-int(base[2]))**2) > 50:
                left = i
                stop = True
                break

        if stop:
            break

        i += 10

    i = 100
    while i < width:
        stop = False
        for j in range(height):
            if math.sqrt((int(img[j][width-i][0])-int(base[0]))**2 + (int(img[j][width-i][1])-int(base[1]))**2 + (int(img[j][width-i][2])-int(base[2]))**2) > 50:
                right = width - i
                stop = True
                break

        if stop:
            break

        i += 10

    i = 100
    while i < height:
        stop = False
        for j in range(width):
            if math.sqrt((int(img[i][j][0]) - int(base[0])) ** 2 + (
                    int(img[i][j][1]) - int(base[1])) ** 2 + (
                                 int(img[i][j][2]) - int(base[2])) ** 2) > 50:
                top = i
                stop = True
                break

        if stop:
            break

        i += 10

    i = 100
    while i < height:
        stop = False
        for j in range(width):
            if math.sqrt((int(img[height-i][j][0]) - int(base[0])) ** 2 + (
                    int(img[height-i][j][1]) - int(base[1])) ** 2 + (
                                 int(img[height-i][j][2]) - int(base[2])) ** 2) > 30:
                bottom = height-i
                stop = True
                break

        if stop:
            break

        i += 10

    print(left)
    print(right)
    print(top)
    print(bottom)

    cv2.line(img, (left, 0), (left, height), (0, 0, 255), 2)
    cv2.line(img, (right, 0), (right, height), (0, 0, 255), 2)
    cv2.line(img, (0, top), (width, top), (0, 0, 255), 2)
    cv2.line(img, (0, bottom), (width, bottom), (0, 0, 255), 2)
    cv2.imshow("result", img)
    cv2.waitKey(0)


center_image("14 февраля9171.jpg")
