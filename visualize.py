import numpy as np
from PIL import Image
from matplotlib import pyplot as plt

if __name__ == "__main__":
    img = Image.open("own.jpg")
    img = img.load()
    data = np.load("new_model/62.npy")
    new_img = Image.new("RGB", (96, 96))
    for x in range(96):
        for y in range(96):
            if 10 >= data[y, x] > 0:
                new_img.putpixel((x, y), (0, 255, 0, 0))
            elif 20 >= data[y, x] > 10:
                new_img.putpixel((x, y), (0, 0, 255, 0))
            elif data[y, x] > 20:
                new_img.putpixel((x, y), (255, 0, 0, 0))
            else:
                new_img.putpixel((x, y), img[x, y])
    new_img.save("vvv_new.png")
