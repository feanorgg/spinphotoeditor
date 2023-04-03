from os import listdir, mkdir
from os.path import isfile, join, getmtime
from shutil import copy2
from datetime import datetime
import cv2
from pyzbar.pyzbar import decode


def get_time():
    now = datetime.now()
    dt_string = now.strftime("%d.%m.%Y %H:%M:%S")
    return dt_string


def read_barcode(image):
    img = cv2.imread(image)
    detected_barcodes = decode(img)
    if not detected_barcodes:
        return ""
    else:
        bc = detected_barcodes[0]
        return bc.data


WORKING_PATH = "./"
OUTPUT_PATH = "./"
print("Loading...")

with open("logs.txt", "a", encoding="UTF-8") as log:
    print(f"[INFO] [{get_time()}] Процессор запущен. Чтение файлов из папки...")
    log.write(f"[INFO] [{get_time()}] Процессор запущен. Чтение файлов из папки....\n")

    files = [f for f in listdir(WORKING_PATH) if isfile(join(WORKING_PATH, f))]
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
            product_id = read_barcode(f"{WORKING_PATH}{file}")
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
                    copy2(
                        f"{WORKING_PATH}{image}",
                        f"{OUTPUT_PATH}{product_id}/{new_img_name}"
                    )

                print(f"[INFO] [{get_time()}] Папка {product_id} сформирована")
                log.write(f"[INFO] [{get_time()}] Папка {product_id} сформирована\n")
