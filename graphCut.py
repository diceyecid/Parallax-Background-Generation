# Used and modified with permission from https://github.com/THU17cyz/GraphCut
import sys
import time
import numpy as np
import cv2

from graph import Graph
from custom_io import debug_out, increment_status_message
from graphEnums import GenDirection, GenMethod

def main():
    path_in = sys.argv[1] if len(sys.argv) > 1 else quit()
    path_out = sys.argv[2] if len(sys.argv) > 2 else "./"
    pattern = cv2.imread(path_in)
    h, w = pattern.shape[:2]

    direction = GenDirection(int(sys.argv[3])) if len(sys.argv) > 3 else GenDirection.HORIZONAL
    patchFactor =  int(sys.argv[4]) if len(sys.argv) > 4 else 8
    mode = GenMethod(int(sys.argv[5]) if len(sys.argv) > 5 else 2)

    target_h = int(sys.argv[6]) if len(sys.argv) > 6 else int(2*h)
    target_w = int(sys.argv[7]) if len(sys.argv) > 7 else int(2*w)

    debug_out("path in: %s, path out: %s, direction: %s, factor: %i, mode: %s, height: %i, width: %i\n", path_in, path_out, direction.name, patchFactor, mode.name, target_h, target_w)

    image_out = graphCut( pattern, direction, patchFactor, mode, target_h, target_w)
    cv2.imwrite(path_out, image_out)

def graphCut( image_in, direction = GenDirection.HORIZONAL, patchFactor = 8, mode = GenMethod.SUBBLOCK_ROW, h_out = 0, w_out = 0):
    # def graphCut(inputImage.int32 direction patchFactor mode[1-3] outputWidth outputHeight):
    # parameters:
    # inputImage -> cv2.imread(path)
    # direction -> horizontal or bi-directional generation (enum style?)
    # patchFactor -> determines size of patches used during generation
    #                   width only for horizontal generation
    # mode -> int value from 1 to 3, using the starter code
    # outputWidth, outputHeight -> outputHeight equals inputHeight for horizontal generation

    if (h_out is 0) and (w_out is 0):
        return image_in

    image_in = image_in.astype(np.int32)
    h_in, w_in = image_in.shape[:2]
    PATCH_H_RATIO = 1 if direction is GenDirection.HORIZONAL else patchFactor
    PATCH_W_RATIO = patchFactor
    sub_patch_size = (h_in//PATCH_H_RATIO, w_in//PATCH_W_RATIO)

    g = Graph(h_out, w_out)
    max = g.w*g.h
    counter = 0
    debug_out("channels in: %i, channels out: %i\n", image_in.shape[2], g.canvas.shape[2])

    # Generate Texture in Random Order using Sub Patches
    if mode is GenMethod.SUBBLOCK_RANDOM:
        g.init_graph(image_in, new_pattern_size=sub_patch_size)
        while g.filled.sum() < max:
            counter = increment_status_message(counter)
            g.blend(
                g.match_patch(
                    image_in, mode='opt_sub', k=1, new_pattern_size=sub_patch_size))
        sys.stdout.write('\n')

    # Generate Texture Row-by-Row using Sub Patches (Preferred)
    elif mode is GenMethod.SUBBLOCK_ROW:
        g.init_graph(image_in, new_pattern_size=sub_patch_size)
        start_row = 0
        local_k = 100
        while g.filled.sum() < max:
            while g.filled.sum() < (start_row+(h_in//PATCH_H_RATIO))*g.w:
                counter = increment_status_message(counter)
                g.blend(
                    g.match_patch(
                        image_in, mode='opt_sub', k=local_k, row=start_row, new_pattern_size=sub_patch_size))
            if g.h-(h_in//PATCH_H_RATIO)-start_row < h_in//(PATCH_H_RATIO*2):
                start_row = g.h-(h_in//PATCH_H_RATIO)
            else:
                pattern_info = g.match_patch(
                    image_in, mode='opt_sub', k=local_k, new_pattern_size=sub_patch_size)
                g.blend(pattern_info) 
                start_row = pattern_info[0]
        sys.stdout.write('\n')

    # Generate Texture Row-by-Row using Full Size Patches
    elif mode is GenMethod.GLOBAL_ROW:
        g.init_graph(image_in)
        start_row = 0
        local_k = 10
        while g.filled.sum() < max:
            while g.filled.sum() < (start_row+h_in)*g.w:
                counter = increment_status_message(counter)
                g.blend(
                    g.match_patch(
                        image_in, mode='opt_whole', k=local_k, row=start_row, new_pattern_size=sub_patch_size))
            if g.h-h_in-start_row < h_in//2:
                start_row = g.h-h_in
            else:
                pattern_info = g.match_patch(
                    image_in, mode='opt_whole', k=local_k)
                g.blend(pattern_info)
                start_row = pattern_info[0]
        sys.stdout.write('\n')

    return g.canvas.astype(np.uint8)
    

if __name__ == '__main__':
    start = time.time()
    main()
    print('time consumed', time.time()-start)

