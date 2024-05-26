import os

def find_png_images(directory, ext = '.png'):
    png_images = {}

    for root, dirs, files in os.walk(directory):
        for dir in dirs:
            png_images[dir] = []
        for file in files:
            if file.lower().endswith(ext):
                png_images[os.path.basename(root)].append(os.path.join(root, file)[1::].replace("\\", "/"))

    return png_images