# Used and modified with permission from https://github.com/THU17cyz/GraphCut
import imageio
import cv2
import numpy as np
from sys import stdout

def read_img(im_fn):
    im = cv2.imread(im_fn)
    if im is None:
        # print('{} cv2.imread failed'.format(im_fn))
        tmp = imageio.mimread(im_fn)
        if tmp is not None:
            imt = np.array(tmp)
            imt = imt[0]
            im = imt[:, :, [2, 1, 0]]
    return im

def show_img(im, name='image'):
    cv2.imshow(name, im.astype(np.uint8))
    cv2.waitKey()

def write_img(im, fn):
    cv2.imwrite(fn, im.astype(np.uint8))

def increment_status_message(counter):
    stdout.write('\r')
    stdout.write("interation number %i" % (counter))
    stdout.flush()
    counter += 1
    return counter
