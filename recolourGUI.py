import sys
import cv2
import tkinter as tk
from tkinter.colorchooser import askcolor
from PIL import Image, ImageTk

# process image to a ready-to-display image for tkinter
def getTkImage( image ):
    # crop image to the first 300 coloums
    im = image[ :, 0 : 300, : ]

    # convert image colour space to RGB(A)
    if image.shape[2] == 3:
        im = cv2.cvtColor( im, cv2.COLOR_BGR2RGB )
    elif image.shape[2] == 4:
        im = cv2.cvtColor( im, cv2.COLOR_BGRA2RGBA )

    # convert image to be displayable in tkinter
    im = Image.fromarray( im )
    im = ImageTk.PhotoImage( im )

    return im


# BGRA to Hex
def bgr2hex( colour ):
    return '#%02x%02x%02x' % tuple( colour[ 2 :: -1 ] )


# create colour block image using BGR colour
def createColourBlock( colour ):
    block = Image.new( mode = 'RGB', size = ( 50, 50 ), color = tuple( colour[ 2 :: -1 ] ) )
    block = ImageTk.PhotoImage( block )

    return block


# ask user to pick a colour
def pickColour( button, newColours, index ):
    colour = askcolor()[0]

    if colour is not None:
        # newColours is passed by reference, save picked colour in it
        newColours[ index ][ : 3 ] = colour

        # replace on colour block on button
        cBlock = createColourBlock( colour[ :: -1 ] )
        button.configure( image = cBlock )
        button.image = cBlock

    return


# action bar action
def action( window, resultColours, colours ):
    resultColours = colours[ : ]
    window.destroy()

    return


# main execution
def startGUI( image, colours ):
    window = tk.Tk()
    window.title( 'Recolouring image' )

    # display image
    im = getTkImage( image )
    imageLabel = tk.Label( window, image = im )
    imageLabel.image = im
    imageLabel.pack()

    # palette recolouring panels
    newColours = colours[ : ]
    for i, c in enumerate( colours ):
        frame = tk.Frame( window )
        frame.pack( side = tk.TOP )
        cBlock = createColourBlock( c )

        # display colours found
        label = tk.Label( frame, image = cBlock )
        label.image = cBlock
        label.pack( side = tk.LEFT )

        # display arrow
        arrow = tk.Label( frame, text = '→', font = ( 'Arial', 24 ), padx = 10, pady = 10 )
        arrow.pack( side = tk.LEFT )

        # create a button
        button = tk.Button( frame, image = cBlock, relief = tk.RAISED )
        button.image = cBlock

        # add color picker command to button
        cmd = lambda b = button, nc = newColours, index = i : pickColour( b, nc, index )
        button.configure( command = cmd )
        button.pack( side = tk.LEFT )

    # ok and cancel action bar
    resultColours = []
    actionBar = tk.Frame( window )
    actionBar.pack( side = tk.BOTTOM )

    # return new colours
    bindNewColours = lambda win = window, res = resultColours, c = newColours : action( win, res, c )
    okButton = tk.Button( actionBar, text = 'OK', font = ( 'Arial', 16 ), command = bindNewColours )
    okButton.pack( side = tk.RIGHT )

    # return old colours
    bindOldColours = lambda win = window, res = resultColours, c = colours : action( win, res, c )
    cancelButton = tk.Button( actionBar, text = 'Cancel', font = ( 'Arial', 16 ), command = bindOldColours )
    cancelButton.pack( side = tk.RIGHT )

    window.mainloop()

    # window closed without clicking ok or cancel
    if len( resultColours ) == 0:
        resultColours = colours[ : ]

    return resultColours
