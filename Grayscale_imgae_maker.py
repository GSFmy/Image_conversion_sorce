import cv2
import numpy as np

# Get path of original image.
im_path = input("Please enter the path of the image you want to convert to grayscale.\n")

# Install originl image as array
im=cv2.imread(im_path)

# Convert to grayscale image
im_gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)

# Get path of grayscal image.
im_gray_path = input("Please enter the path where the converted image will be saved.\n")

# Save grayscal image.
cv2.imwrite(im_gray_path, im_gray)

# print("This is test\n")