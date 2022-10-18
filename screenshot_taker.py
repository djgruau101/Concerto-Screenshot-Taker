import webbrowser
import cv2
import pyautogui
from pytube import YouTube
import numpy as np
import time
import os
import sys

forbidden_chars_dir = '\/:*?"<>|'
dir_made = False
url = ""
destination = ""

for arg in sys.argv:
    if "www.youtube.com/watch" in arg:
        url = arg
    elif os.path.isdir(arg):
        destination = arg

if url == "" and destination == "":
    raise ValueError("Please provide a YouTube link and a path.")
if url == "":
    raise ValueError("Please provide a YouTube link.")
if destination == "":
    raise ValueError("Please provide a path.")

webbrowser.open_new(url)
yt = YouTube(url)
video_length = yt.length
title = yt.title
for char in forbidden_chars_dir:
    title = title.replace(char, '')
title = title.replace('/', '')  # to avoid a directory error

if destination[-1] != '/':
    destination += '/'
destination += f"Screenshots {title}/"
tmp_screenshot = None


def mse(imageA, imageB):
	'''Metric that evaluates the similarity between imageA and imageB. The lower the value, the more similar the images are.'''
	err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
	err /= float(imageA.shape[0] * imageA.shape[1])
	return err


def crop_top_bottom(img_list):
    '''Crops the top and bottom paddings of an image represented by img_list.'''
    index1 = 0
    index2 = 0
    # crop from top
    for i, row in enumerate(img_list):
        if row.count(255) > len(row)/2 or i == len(img_list)-1:
            index1 = i
            break
    # crop from bottom
    for i, row in enumerate(reversed(img_list)):
        if row.count(255) > len(row)/2:
            index2 = len(row) - i  # ith row from end: -i (include it)
            break
    return img_list[index1:index2], index1, index2  # crop from top and bottom: will cut off the black


def crop_sides(img_list):
    '''Crops the left and right paddings of an image represented by img_list.'''
    index1 = 0
    index2 = 0
    # crop from left
    for i in range(len(img_list[0])):
        column = [row[i] for row in img_list]
        if column.count(255) > len(column)/2 or i == len(img_list[0])-1:
            index1 = i
            break
    # crop from right
    for i in reversed(range(len(img_list[0]))):
        column = [row[i] for row in img_list]
        if column.count(255) > len(column)/2:
            index2 = i + 1
            break
    return [col[index1:index2] for col in img_list], index1, index2


def remove_padding(img):
    '''Removes the black padding from an image.'''
    im_list = img.tolist()
    index1 = 0
    index2 = 0
    index3 = 0
    index4 = 0
    im_list, index1, index2 = crop_top_bottom(im_list)
    # print(index2)
    if index2 == 0:
        im_list = img.tolist()  # restore
        im_list, index3, index4 = crop_sides(im_list)
        im_list, index1, index2 = crop_top_bottom(im_list)
    else:
        im_list, index3, index4 = crop_sides(im_list)
    if index2 != 0 and index4 != 0:
        # if img[index1: index2, index3: index4] is not None:
        #     print(index1, index2, index3, index4)
        return img[index1: index2, index3: index4]


print("Start!")
capture = 0
while capture <= video_length:
    time.sleep(1)
    image = pyautogui.screenshot()
    image = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2GRAY)
    if tmp_screenshot is None:
        tmp_screenshot = image
    if mse(image, tmp_screenshot) > 100:  # we have changed part
        tmp_screenshot = image
        if not dir_made:
            if not os.path.isdir(destination):
                os.mkdir(destination)
            else:
                duplicate = 2 
                while os.path.isdir(destination[:-1] + f" ({duplicate})/"):
                    duplicate += 1
                destination = destination[:-1] + f" ({duplicate})/"
                os.mkdir(destination)
            dir_made = True
        # crop the black paddings on the screenshot if there are any
        cropped_screenshot = remove_padding(tmp_screenshot)
        if cropped_screenshot is not None:
            cv2.imwrite(destination+str(capture)+".jpeg", cropped_screenshot)
            capture += 1
