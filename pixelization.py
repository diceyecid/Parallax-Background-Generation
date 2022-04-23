import cv2
import numpy as np
from sklearn.cluster import KMeans


# get palette colours using k-mean
def getPalette( image, nColours ):
    # reshape image into 1-D array of pixels with input channels
    pixels = image.copy()
    pixels = image.reshape( ( -1, image.shape[2] ) )

    # k-mean clustering
    km = KMeans( n_clusters = nColours )
    km.fit( pixels )

    # put palette colours into an array
    colours = np.asarray( km.cluster_centers_, dtype = 'uint8' )

    return colours, km.labels_


# fit image with only the palette colours
def reduceColour( image, colours, pixelMap ):
    pixels = image.copy()
    pixels = pixels.reshape( ( -1, image.shape[2] ) )
    
    for px in range( pixels.shape[0] ):
        for ix in range( colours.shape[0] ):
            pixels[px] = colours[pixelMap[px]]

    result = pixels.reshape( image.shape )
    return result


# smooth image by using bilateral filter
def smoothenImage( image ):
    result = image.copy()

    # convert image into 3 channels if it has an alpha channel
    if image.shape[2] == 4:
        result = cv2.cvtColor( result, cv2.COLOR_BGRA2BGR )

    # blur
    result = cv2.bilateralFilter( result, 9, 100, 100 )

    # add alpha channel back if it had one
    if image.shape[2] == 4:
        result = cv2.cvtColor( result, cv2.COLOR_BGR2BGRA )
        result[ :, :, 3 ] = image[ :, :, 3 ]

    return result


# pixelize by downsizing and upscaling
def pixelateImage( image, superpixelSize ):
    # get image dimention
    height, width, _ = image.shape

    # downsize
    downWidth = width // superpixelSize 
    downHeight = height // superpixelSize 
    downImage = cv2.resize( image, ( downWidth, downHeight ), interpolation = cv2.INTER_LINEAR  )

    # upscale
    result = cv2.resize( downImage, ( width, height ), interpolation = cv2.INTER_NEAREST )

    return result


# main execution
def pixelize( image, nColours, superpixelSize ):
    colours, pixelMap = getPalette( image, nColours )
    lessColourImage = reduceColour( image, colours, pixelMap )
    blurredImage = smoothenImage( lessColourImage )
    pixelizedImage = pixelateImage( blurredImage, superpixelSize )

    return pixelizedImage
