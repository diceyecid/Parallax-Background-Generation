import os
import sys
import cv2
import glob
import argparse
from tqdm import tqdm
from graphCut import graphCut
from graphEnums import GenDirection, GenMethod
from pixelization import pixelize, pixelizeP1, pixelizeP2


#---------- constants ----------#


VALID_EXTENSIONS = [ 'png', 'jpg', 'jpeg' ]


#---------- functions ----------#


# construct arguments for the pipeline
def getArguments():
    parser = argparse.ArgumentParser( description = 'Generate parallax background' )

    parser.add_argument( '-i', '--input', type = str, required = True,
            help =  'the image or directory with images to be used (this is a required argument)' )

    parser.add_argument( '-o', '--output_dir', type = str, default = './output',
            help =  'the directory where resulting images are to be saved' )

    parser.add_argument( '--output_width_factor', type = float, default = 4,
            help =  'the scale factor to determine the width of resulting image' )
    
    parser.add_argument( '--output_height_factor', type = float, default = 1,
            help =  'the scale factor to determine the height of resulting image' )
    
    parser.add_argument( '--output_width', type = int,
            help =  'the width of resulting image (setting this will ignore \'output_width_factor\')' )
    
    parser.add_argument( '--output_height', type = int,
            help =  'the height of resulting image (setting this will ignore \'output_height_factor\')' )
    
    parser.add_argument( '--n_colors', type = int, default = 8,
            help =  'the number of dominate colours to be extracted as a palette for the image(s)' )

    parser.add_argument( '--recolor', action = 'store_true', default = False, 
            help =  'the option to turn on palette recolouring for the image(s)' )
    
    parser.add_argument( '--superpixel_size', type = int, default = 3,
            help =  'the size of a \'pixel\' after pixelization' )

    parser.add_argument( '--pixelization_only', action = 'store_true', default = False,
            help =  'the option to run only the pixelization and recolouring part' )
    
    parser.add_argument( '--direction', type = int, default = 0, choices = [ 0, 1 ],
            help =  'the direction of texture generation; ' +
                    '0 for horizontal; ' + 
                    '1 for bi-directional' )
    
    parser.add_argument( '--patch_factor', type = int, default = 8,
            help = 'the factor to determine size of patches used during generation' )
    
    parser.add_argument( '--generation_mode', type = int, default = 2, choices = [ 1, 2, 3 ],
            help =  'the mode for texture generation; ' +
                    '1 for global subpatch best matching; ' + 
                    '2 for row-by-row subpatch best matching; ' +
                    '3 for row-by-row best matching' )

    parser.add_argument( '--generation_only', action = 'store_true', default = False,
            help =  'the option to run only the Graphcut generation part' )
    
    return parser.parse_args()


# get image from system argument
def getImages( path ):
    imagePaths = [];
    imageSubpaths = [];
    images = [];

    # get all image paths
    if os.path.isdir( path ):
        # get all paths with valid extension
        for ext in VALID_EXTENSIONS:
            imagePaths.extend( glob.glob( os.path.join( path, f'**/*.{ ext }' ), recursive = True ) )

        # get all images and names from the path list
        for p in imagePaths:
            # read image from path
            im = cv2.imread( p, cv2.IMREAD_UNCHANGED ) 

            # if image does not exist, log and skip this image
            if im is None:
                print( f'{ p } does not exist' )

            else:
                images.append( im )
                imageSubpaths.append( os.path.relpath( p, path ) )

    # there is only one image inputed
    else:
        im = cv2.imread( path, cv2.IMREAD_UNCHANGED )

        # if image does not exist, log and skip this image
        if im is None:
            print( f'{ path } does not exist' )

        else:
            images.append( im )
            imageSubpaths.append( os.path.basename( path ) )

    return images, imageSubpaths


# determine output image width and height
def getOutputSize( image, args, downsized = False ):
    width, height = args.output_width, args.output_height

    if width is None:
        width = image.shape[1] * args.output_width_factor

    if height is None:
        height = image.shape[0] * args.output_height_factor

    if downsized:
        width, height = width // args.superpixel_size, height // args.superpixel_size 

    return width, height


# main execution
def main():
    # get input arguments
    args = getArguments()

    # get all images
    images, imageSubpaths = getImages( args.input )

    # create output directory to save output images
    if not os.path.exists( args.output_dir ):
        os.makedirs( args.output_dir )

    # pixelize images and save them to output directory
    progressBar = tqdm( zip( images, imageSubpaths ), desc = 'Generating pixelized background', total = len( images ) )
    for im, sp in progressBar:
        # pixelization only
        if args.pixelization_only:
            result = pixelize( im, args.n_colors, args.recolor, args.superpixel_size )

        # generation only
        elif args.generation_only:
            outputWidth, outputHeight = getOutputSize( im, args, downsized = False )
            result = graphCut( im, GenDirection( args.direction ), args.patch_factor,
                                GenMethod( args.generation_mode ), outputHeight, outputWidth )

        # pixelization and generation
        else:
            # pixelize image (part 1)
            result = pixelizeP1( im, args.n_colors, args.recolor, args.superpixel_size )

            # texture generation
            outputWidth, outputHeight = getOutputSize( im, args, downsized = True )
            result = graphCut( result, GenDirection( args.direction ), args.patch_factor,
                                GenMethod( args.generation_mode ), outputHeight, outputWidth )

            # pixelize image (part 2)
            outputWidth, outputHeight = getOutputSize( im, args, downsized = False )
            result = pixelizeP2( result, outputWidth, outputHeight )

        # create subdirectories to match input directory structure if necessary
        saveDir = os.path.join( args.output_dir, os.path.dirname( sp ) )
        if not os.path.exists( saveDir ):
            os.makedirs( saveDir )
        
        # save image
        cv2.imwrite( os.path.join( args.output_dir, sp ), result )
    progressBar.close()

    return 


if __name__ == '__main__':
    main()
