from os import listdir, mkdir
from os.path import isfile, join
import time
from shutil import copy2

from functions import get_time
from barcode_reader import read_barcode

print("[SETUP] Введите адрес папки, в которую попадают фото при съемке: ")
WORKING_PATH = input()
if WORKING_PATH == "":
    WORKING_PATH = "./"

print("[SETUP] Введите адрес папки для выходных данных. Оставьте пустым, чтобы выгрузить отсортированные фотографии к несортированным: ")
OUT_PATH = input()
if OUT_PATH == "":
    OUT_PATH = WORKING_PATH

if WORKING_PATH[-1] != "/":
    WORKING_PATH += "/"

if OUT_PATH[-1] != "/":
    OUT_PATH += "/"

try:
    mkdir(OUT_PATH)
except:
    pass

with open("logs.txt", "a", encoding="UTF-8") as log:
    old_files = [f for f in listdir(WORKING_PATH) if isfile(join(WORKING_PATH, f))]
    CURRENT_VOLUME = len(old_files)

    print(f"[INFO] [{get_time()}] Процессор запущен. Можно приступать к работе")
    log.write(f"[INFO] [{get_time()}] Процессор запущен\n")

    current_queue = []

    while True:
        time.sleep(.3)
        files = [f for f in listdir(WORKING_PATH) if isfile(join(WORKING_PATH, f))]
        if len(files) > CURRENT_VOLUME:
            CURRENT_VOLUME = len(files)
            new_file = ""
            for file in files:
                if file not in old_files:
                    print(f"[INFO] [{get_time()}] Добавлен файл: {file}")
                    log.write(f"[INFO] [{get_time()}] Добавлен файл: {file}\n")
                    old_files.append(file)

                    if file.split(".")[-1] in [
                        "jpg",
                        "jpeg",
                        "png"
                    ]:
                        current_queue.append(file)
                        product_id = read_barcode(file)
                        try:
                            product_id = bytes(product_id).decode('ASCII')
                            if len(product_id) > 8:
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

                            mkdir(f"{OUT_PATH}{product_id}")
                            index = 0
                            for image in product_images:
                                index += 1
                                new_img_name = f"{index}.{image.split('.')[-1]}"
                                print(f"[INFO] [{get_time()}] Копирование {image} в ./{product_id}/{new_img_name}")
                                log.write(f"[INFO] [{get_time()}] Копирование {image} в ./{product_id}/{new_img_name}\n")
                                copy2(
                                    f"{WORKING_PATH}{image}",
                                    f"{OUT_PATH}{product_id}/{new_img_name}"
                                )

                            print(f"[INFO] [{get_time()}] Папка {product_id} сформирована")
                            log.write(f"[INFO] [{get_time()}] Папка {product_id} сформирована\n")
