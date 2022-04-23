import os
import sys
import cv2
import glob
from tqdm import tqdm
from pixelization import pixelize


#---------- constants ----------#


EXTEXSIONS = [ 'png' ]
OUTPUT_DIR = './output'


#---------- functions ----------#


# get image from system argument
def getImages( path ):
    imagePaths = [];
    imageSubpaths = [];
    images = [];

    # get all image paths
    if os.path.isdir( path ):
        for ext in EXTEXSIONS:
            imagePaths.extend( glob.glob( os.path.join( path, f'**/*.{ ext }' ), recursive = True ) )
    else:
        imagePaths.append( path )

    # get all images and names from the path list
    for p in imagePaths:
        # read image from path
        im = cv2.imread( p, cv2.IMREAD_UNCHANGED ) 

        # if image does not exist, log and skip this image
        if im is None:
            print( f'{ p } does not exist' )

        else:
            imageSubpaths.append( os.path.relpath( p, path ) )
            images.append( im )

    return images, imageSubpaths


# main execution
def main():
    # get all images
    path = sys.argv[1]
    images, imageSubpaths = getImages( path )

    # create output directory to save output images
    if not os.path.exists( OUTPUT_DIR ):
        os.makedirs( OUTPUT_DIR )

    # pixelize images and save them to output directory
    progressBar = tqdm( zip( images, imageSubpaths ), desc = 'Pixelizing', total = len( images ) )
    for im, sp in progressBar:
        # pixelize image
        pixelized = pixelize( im )

        # create subdirectories to match input directory structure if necessary
        saveDir = os.path.join( OUTPUT_DIR, os.path.dirname( sp ) )
        if not os.path.exists( saveDir ):
            os.makedirs( saveDir )
        
        # save image
        cv2.imwrite( os.path.join( saveDir, os.path.basename( sp ) ), pixelized )
    progressBar.close()

    return 


if __name__ == '__main__':
    main()
