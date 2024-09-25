import sys
import pathlib
import fitz
# Please install pymupdf to use fitz

# Get path of pdf.
pdf_path = input("Please enter the path and file name of the pdf you want to convert to jpeg.\n")

# opem pdf
pdf = fitz.open(pdf_path)

# Get name of jpeg.
jpeg_path = input("Please enter the path and name of jpeg will be saved. Don't enter extension.\n")

# Selet dpi or not.
dpi_s = input("If you want to select dpi, input 1. Else input 0.\n")
if int(dpi_s) > 0:
  dpi_num = input("input dpi.\n")

for i, page in enumerate(pdf):
  if int(dpi_s) > 0:
    pix=page.get_pixmap(dpi = int(dpi_num))
  else:
    pix = page.get_pixmap()
  image_path = jpeg_path+str(i).zfill(2) + '.jpg'
  pix.save(image_path)

pdf.close()