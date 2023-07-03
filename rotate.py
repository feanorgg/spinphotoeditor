import cv2
import scipy.ndimage as ndimage

input_file = "test_out/6.jpg"

image = cv2.imread(input_file)
Gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
_, binary = cv2.threshold(Gray, 245, 247, cv2.THRESH_BINARY_INV)
contours, hierarchy = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2:]

minh = 10000
ang = 0

for i in range(len(contours)):
    rect = cv2.minAreaRect(contours[i])
    angle = rect[2]
    if angle != 0 and abs(angle) < 25:
        rwidth, rheight = rect[0]
        if rheight > rwidth:
            rangle = angle
        else:
            rangle = 90 - abs(angle)

        if abs(rangle) < 25:
            rotate_img = ndimage.rotate(binary, rangle, reshape=True)
            xs, ys = rotate_img.shape

            xmin = 0
            xmax = xs

            x = 0
            while x < int(xs)/2:
                weight = 0
                y = 0
                while y < ys:
                    weight += rotate_img[x][y]
                    y += 10

                if weight > 1000:
                    xmin = x
                    break

                x += 10

            x = xs-1
            while x > int(xs)/2:
                weight = 0
                y = 0
                while y < ys:
                    weight += rotate_img[x][y]
                    y += 10

                if weight > 1000:
                    xmax = x
                    break

                x -= 10

            if xmax-xmin < minh:
                minh = xmax-xmin
                ang = rangle

rotate_img = ndimage.rotate(image, ang, reshape=True, cval=246)
cv2.imwrite(f"{input_file}_edit.jpg", rotate_img)

cv2.imshow("in", image)
cv2.imshow("out", rotate_img)
cv2.waitKey(0)
