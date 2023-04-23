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
    out = remove(_image, session=session, alpha_matting=True, alpha_matting_erode_size=15)
    result.paste(out, mask=out)
    return result


def rotate(input_file):
    _image = cv2.imread(input_file)
    # print(_image)
    _Gray = cv2.cvtColor(_image, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(_Gray, 245, 247, cv2.THRESH_BINARY_INV)
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
                while x < int(xs) / 2:
                    weight = 0
                    y = 0
                    while y < ys:
                        weight += rotate_img[x][y]
                        y += 10

                    if weight > 1000:
                        xmin = x
                        break

                    x += 10

                x = xs - 1
                while x > int(xs) / 2:
                    weight = 0
                    y = 0
                    while y < ys:
                        weight += rotate_img[x][y]
                        y += 10

                    if weight > 1000:
                        xmax = x
                        break

                    x -= 10

                if xmax - xmin < minh:
                    minh = xmax - xmin
                    ang = rangle

    rotate_img = ndimage.rotate(_image, ang, reshape=True, cval=246)
    cv2.imwrite(f"{input_file}", rotate_img)


rsession = new_session("u2net")
AI_ACTIVE = False
AI_PHOTO_COUNT = 2

WORKING_PATH = "./ДЛЯТРЕНИРОВОЧКИ/"
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

            if product_id != "":
                current_queue.pop()
                print(f"[INFO] [{get_time()}] Файл {file} содержит штрихкод: {product_id}")
                log.write(f"[INFO] [{get_time()}] Файл {file} содержит штрихкод: {product_id}\n")
                product_images = current_queue
                current_queue = []

                print(f"[INFO] [{get_time()}] Формируется папка {product_id}...")
                log.write(f"[INFO] [{get_time()}] Формируется папка {product_id}...\n")

                mkdir(f"{OUTPUT_PATH}{product_id}")
                index = 0
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

                        rotate(new_path)

                        print(f"[INFO] [{get_time()}] AI-обработка изображения {index} для товара {product_id} завершена")
                        log.write(f"[INFO] [{get_time()}] AI-обработка изображения {index} для товара {product_id} завершена\n")

                print(f"[INFO] [{get_time()}] Папка {product_id} сформирована")
                log.write(f"[INFO] [{get_time()}] Папка {product_id} сформирована\n")
