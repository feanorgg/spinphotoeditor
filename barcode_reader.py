import cv2
from pyzbar.pyzbar import decode


def read_barcode_example(image):
    img = cv2.imread(image)

    # Decode the barcode image
    detected_barcodes = decode(img)

    # If not detected then print the message
    if not detected_barcodes:
        print("Barcode Not Detected or your barcode is blank/corrupted!")
    else:

        # Traverse through all the detected barcodes in image
        for barcode in detected_barcodes:

            # Locate the barcode position in image
            (x, y, w, h) = barcode.rect

            # Put the rectangle in image using
            # cv2 to highlight the barcode
            cv2.rectangle(img, (x - 10, y - 10),
                          (x + w + 10, y + h + 10),
                          (255, 0, 0), 2)

            if barcode.data != "":
                # Print the barcode data
                print(barcode.data)
                print(barcode.type)

    # Display the image
    cv2.imshow("Image", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def read_barcode(image):
    img = cv2.imread(image)
    detected_barcodes = decode(img)
    if not detected_barcodes:
        return ""
    else:
        bc = detected_barcodes[0]
        return bc.data


print("[STARTING] Модуль считывания штрихкода подключен")
