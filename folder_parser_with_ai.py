import os
from os import listdir, mkdir
from os.path import isfile, join, getmtime
from shutil import copy2
from datetime import datetime
import cv2
from pyzbar.pyzbar import decode
from rembg import new_session, remove
from PIL import Image
import scipy.ndimage as ndimage
import numpy as np
import time


def get_time():
    now = datetime.now()
    dt_string = now.strftime("%d.%m.%Y %H:%M:%S")
    return dt_string


def read_barcode(_image):
    img = cv2.imread(_image)
    detected_barcodes = decode(img)
    if not detected_barcodes:
        return ""
    else:
        bc = detected_barcodes[0]
        return bc.data


def process(session, _image, *, size=None, bgcolor='#f6f6f6'):
    if size is not None:
        _image = _image.resize(size)
    else:
        size = _image.size
    result = Image.new("RGB", size, bgcolor)
    out = remove(_image, session=session, alpha_matting=True, alpha_matting_erode_size=3)
    result.paste(out, mask=out)
    return result


def rotate(input_file):
    _image = cv2.imread(input_file)
    _Gray = cv2.cvtColor(_image, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(_Gray, 245, 247, cv2.THRESH_BINARY_INV)
    # cv2.imshow("bin", binary)
    # contours, hierarchy = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2:]

    minh = 10000
    ang = 0
    __ang = -20

    # for i in range(len(contours)):
    for i in range(80):
        # rect = cv2.minAreaRect(contours[i])
        # angle = rect[2]
        angle = __ang
        __ang += 0.5
        if angle != 0 and abs(angle) < 25:
            # rwidth, rheight = rect[0]
            # if rheight > rwidth:
            rangle = angle
            # else:
            #     rangle = 90 - abs(angle)

            # M = cv2.moments(contours[i])

            if abs(rangle) < 25: # and M["m00"] > 0:
                rotate_img = ndimage.rotate(binary, rangle, reshape=False)
                xs, ys = rotate_img.shape

                xmin = 0
                xmax = xs

                x = 0
                while x < int(xs) / 2:
                    weight = 0
                    y = 0
                    while y < ys:
                        weight += rotate_img[x][y]
                        y += 8

                    if weight > 1000:
                        xmin = x
                        break

                    x += 5

                x = xs - 1
                while x > int(xs) / 2:
                    weight = 0
                    y = 0
                    while y < ys:
                        weight += rotate_img[x][y]
                        y += 8

                    if weight > 1000:
                        xmax = x
                        break

                    x -= 5

                # print(f"iteration: height {minh}, angle {rangle}")

                if xmax - xmin < minh:
                    minh = xmax - xmin

                    ang = rangle
                elif (xmax - xmin) - minh > 20 and abs(__ang - ang) > 5:
                    break

    rotate_img = ndimage.rotate(_image, ang, reshape=False, cval=246)
    # cv2.imshow("image", rotate_img)
    # cv2.waitKey(0)
    cv2.imwrite(f"{input_file}", rotate_img)


def center(input_file):
    _image = cv2.imread(input_file)
    _Gray = cv2.cvtColor(_image, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(_Gray, 245, 247, cv2.THRESH_BINARY_INV)
    # cv2.imshow("centering input", binary)
    # cv2.waitKey(0)

    M = cv2.moments(binary)

    cy = int(M['m10'] / M['m00'])
    cx = int(M['m01'] / M['m00'])

    num_rows, num_cols = _image.shape[:2]

    imx = int(num_rows/2)
    imy = int(num_cols/2)

    # print(f"Object center: x: {cx}, y: {cy}")
    # print(f"Image center: x: {imx}, y: {imy}")

    shiftx = imx - cx
    shifty = imy - cy

    # _image = cv2.circle(_image, (cy, cx), 10, (0, 0, 255), 10)
    # _image = cv2.circle(_image, (imy, imx), 10, (0, 0, 255), 10)

    # print(f"Shifting: x: {shiftx}, y: {shifty}")

    translation_matrix = np.float32([[1, 0, shifty], [0, 1, shiftx]])
    shifted_image = cv2.warpAffine(_image, translation_matrix, (num_cols, num_rows),
                              borderMode=cv2.BORDER_CONSTANT,
                              borderValue=(246, 246, 246))

    # cv2.imshow("centering output", shifted_image)
    # cv2.waitKey(0)
    cv2.imwrite(f"{input_file}", shifted_image)


rsession = new_session("u2net")
AI_ACTIVE = False
AI_PHOTO_COUNT = 2

WORKING_PATH = "./input/"
OUTPUT_PATH = "./output/"
print("Loading...")

print("[SETUP] Укажите, будет ли использоваться REMBG. 1 - да, 0 - нет:")
ans = input()
if ans == "1":
    AI_ACTIVE = True
elif ans == "0":
    AI_ACTIVE = False
else:
    print("[SETUP] Некорректный формат ответа. Установлено значение по умолчанию: REMBG не используется")

if AI_ACTIVE:
    print("[SETUP] Укажите количество фотографий для товара, которые будут обработаны REMBG:")
    ans = input()
    limit = int(ans)
    AI_PHOTO_COUNT = limit
    print(f"[SETUP] Установлен лимит {AI_PHOTO_COUNT}")

with open("ai_logs.txt", "a", encoding="UTF-8") as log:
    print(f"[INFO] [{get_time()}] Процессор запущен. Используется AI: {AI_ACTIVE}. Чтение файлов из папки...")
    log.write(f"[INFO] [{get_time()}] Процессор запущен. Используется AI: {AI_ACTIVE}. Чтение файлов из папки....\n")

    files = [f for f in listdir(WORKING_PATH) if isfile(join(WORKING_PATH, f))]
    files = [join(WORKING_PATH, f) for f in files]
    files.sort(key=lambda x: getmtime(x))

    print(files)
    print(f"[INFO] [{get_time()}] Обнаружено {len(files)} файлов. Обработка...")
    log.write(f"[INFO] [{get_time()}] Обнаружено {len(files)} файлов. Обработка...\n")

    current_queue = []

    for file in files:
        new_file = ""

        if file.split(".")[-1] in [
            "jpg",
            "jpeg",
            "png"
        ]:
            print(f"[INFO] [{get_time()}] Добавлен файл: {file}")
            log.write(f"[INFO] [{get_time()}] Добавлен файл: {file}\n")

            current_queue.append(file)
            product_id = read_barcode(file)
            try:
                product_id = bytes(product_id).decode('ASCII')
                product_id = product_id[7:]
            except:
                pass

            # ADD / DELETE THIS
            # product_id = "test"

            if product_id != "":
                # COMMENT/UNCOMMENT THIS
                current_queue.pop()

                print(f"[INFO] [{get_time()}] Файл {file} содержит штрихкод: {product_id}")
                log.write(f"[INFO] [{get_time()}] Файл {file} содержит штрихкод: {product_id}\n")
                product_images = current_queue
                current_queue = []

                print(f"[INFO] [{get_time()}] Формируется папка {product_id}...")
                log.write(f"[INFO] [{get_time()}] Формируется папка {product_id}...\n")

                mkdir(f"{OUTPUT_PATH}{product_id}")
                index = 0
                print(product_images)
                for image in product_images:
                    index += 1
                    new_img_name = f"{index}.{image.split('.')[-1]}"
                    print(f"[INFO] [{get_time()}] Копирование {image} в ./{product_id}/{new_img_name}")
                    log.write(f"[INFO] [{get_time()}] Копирование {image} в ./{product_id}/{new_img_name}\n")

                    new_path = f"{OUTPUT_PATH}{product_id}/{new_img_name}"

                    copy2(
                        image,
                        new_path
                    )
                    # os.system(f"rm {image}")

                    if index-1 < AI_PHOTO_COUNT and AI_ACTIVE:
                        print(f"[INFO] [{get_time()}] Запущена AI-обработка изображения {index} для товара {product_id}...")
                        log.write(f"[INFO] [{get_time()}] Запущена AI-обработка изображения {index} для товара {product_id}...\n")

                        img = Image.open(new_path)
                        res = process(rsession, img, size=img.size, bgcolor="#F6F6F6")
                        res.save(new_path)

                        print(
                            f"[INFO] [{get_time()}] Запущена центровка изображения {index} для товара {product_id}...")
                        log.write(
                            f"[INFO] [{get_time()}] Запущена центровка изображения {index} для товара {product_id}...\n")
                        center(new_path)

                        time.sleep(1)

                        print(
                            f"[INFO] [{get_time()}] Запущено выравнивание изображения {index} для товара {product_id}...")
                        log.write(
                            f"[INFO] [{get_time()}] Запущено выравнивание изображения {index} для товара {product_id}...\n")
                        rotate(new_path)

                        print(f"[INFO] [{get_time()}] AI-обработка изображения {index} для товара {product_id} завершена")
                        log.write(f"[INFO] [{get_time()}] AI-обработка изображения {index} для товара {product_id} завершена\n")

                print(f"[INFO] [{get_time()}] Папка {product_id} сформирована")
                log.write(f"[INFO] [{get_time()}] Папка {product_id} сформирована\n")
