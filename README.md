# Parallax-Background-Generation
A parallax background generation method for 2D side-scrollers.

Art assets for games can be time intensive to produce.
Whether it's a full 3D world, or simpler 2D background, creating good looking assets takes time and skills that are not always readily available.
Time can be saved by using repeating assets, but clear repetition hurts immersion. 
Procedural generation techniques can help make repetition less uniform, but doesn't remove it entirely.
Both cases leave noticeable levels of repetition in the world, and require significant time and skill investments to produce.
Video game developers in hobby, game jam, or early prototyping situations may not have access to the required time and skill.

We propose the use of computational photography to produce layered 2D backgrounds without the need for significant artist time or skill.
In our pipeline, the user provides segmented photographic input, instead of creating traditional art, and receives game-ready assets.
Most time spent is computational run-time, and frees up developers for other work.
Photograph inputs are used to move the artistic skill requirement away from the developer as well.

Our method is as follows:
+ Depth estimation informed interactive segmentation. (We used the GIMP magic wand.)
+ Palette simplification and editing through k-means colour clustering.
+ Graphcut texture generation to extend individual layers to desired lengths.
+ Optionally filtered down-scaling before generation and up-scaling after to produce a pixelated style.

(References at end of README)

## Video
<p align="center">
<a href="http://www.youtube.com/watch?feature=player_embedded&v=dQw4w9WgXcQ
" target="_blank"><img src="http://img.youtube.com/vi/dQw4w9WgXcQ/0.jpg" 
alt="Parallax-Background-Generation Video" width=80% height=auto border="10" /></a>
</p>

## Installation

1. Clone this repository

2. Run setup from the repository root directory

   ```bash
   bash setup.sh
   ```

3. Start Python virtual environment

   ```bash
   source ./venv/bin/activate
   ```

## Usage

### Parallax Pixel Art Background Generation

Use `generate.py` to perform pixelized background texture generation.
By default, it will transfer the input image(s) into pixel art style and
generate textures horizontally for outputs of 4 times in width.

To use it, it is required to pass in an input image or a directory of images:

```bash
python generate.py --input ./samples
```

Since there are many parameters that can be fine tuned to suit different images,
it provides a command line interface with many options available:

+ `--help` or simply `-h`
  shows a help message and exit.

+ `--input` or simply `-i`
  specifies the input of a image or a directory with images. This is required.

+ `--output_dir` or simply `-o`
  specifies the directory where resulting images are to be saved.

+ `--output_width_factor`
  specifies the scale factor to determine the width of resulting image(s).

+ `--output_height_factor`
  specifies the scale factor to determine the height of resulting image(s).

+ `--output_width`
  specifies the width of resulting image(s). (Setting this will ignore `output_width_factor`.)

+ `--output_height`
  specifies the height of resulting image(s). (Setting this will ignore `output_height_factor`.)

+ `--n_colors`
  speciies the number of dominate colours to be extracted as a palette for the image(s).

+ `--recolor`
  raises a flag option to turn on palette recolouring for input image(s).

+ `--superpixel_size`
  specifies the size of a 'pixel' after pixelization.

+ `--direction`
  specifies the direction of texture generation:

  + `0` for horizontal
  + `1` for bi-directional

+ `--patch_factor`
  specifies the factor to determine size of patches used during generation.
  See [below](#Graphcut-Texture-Generation) for more details

+ `--generation_mode`
  specifies the mode for texture generation:

  + `1` for global subpatch best matching
  + `2` for row-by-row subpatch best matching
  + `3` for row-by-row best matching

Pixel art background involves many artistic choices to suit your preference,
we encourage you to try experimenting different options yourself
to generate more interesting results.
Here is an example of using these options:

```bash
python generate.py \
    -i ./samples \
    -o ./output \
    --output_width_factor 4 \
    --output_height_factor 1 \
    --n_colors 8 \
    --recolor \
    --superpixel_size 3 \
    --direction 0 \
    --patch_factor 8 \
    --generation_mode 2
```

You may use the help command for an easy access to the explainations:

```bash
python generate.py --help
```

Have fun! :D

### Graphcut Texture Generation

To use the texture generation portion of the pipeline by itself, `graphCut.py` can be called directly with the following signature.
```bash
python graphCut.py path_in path_out direction patch_factor mode height_out width_out
```
+ `path_in` and `path_out` are the file paths, including file name and extention.

+ `direction` indicates if the texture generates only horizontally, or both horizontally and vertically.  
   + Horizontal works best and is `0`.  
   + Bidirectional is `1`.

+ `patch_factor` is used to choose the size of patches used during generation. 
   + A value of `8` indicates a subpatch with 1/8 times the width of the input image for horizontal generation.  
   + A value of `8` would indicate a subpatch with 1/8 times the width and height of the input image for bidirectional generation.

+ `mode` takes a value between 1 and 3 which relate to different methods of patch selection. 
   + A value of `1` means the output is built placing subpatches in a random order.  
   + A value of `2` means the output is built by placing subpatches row-by-row. 
   + A value of `3` means the output is built using the entire input patch being placed row-by-row.

+ `height_out` and `width_out` are in pixels and determine the output image dimensions.  `height_out` should match the input image height for horizontal generation.

For example:
```bash
python graphCut.py mountainPatch.png mountainOutput.png 0 4 1 300 2000
```

### Others

There is also a simple script to clean up the output directory
and the virtual environment for your convienience:

```bash
bash clean.sh
```

## Attribution
+ Depth Estimation method and implementation from
  ["Boosting Monocular Depth Estimation Models to High-Resolution via Content-Adaptive Multi-Resolution Merging", Miangoleh et al., CVPR 2021](https://github.com/compphoto/BoostingMonocularDepth)
  
+ Pixelization method inspired by
  [Convert Photo into Pixel Art using Python](https://towardsdatascience.com/convert-photo-into-pixel-art-using-python-d0b9bd235797)
  by Abhijith Chandradas

+ Palette extraction referenced
  [Dominant Color Extraction Dominance and Recoloring](https://github.com/srijannnd/Dominant-Color-Extraction-Dominance-and-Recoloring)
  by Srijan Anand

+ Texture generation method from
  ["Graphcut Textures: Image and Video Synthesis Using Graph Cuts",  Kwatra et al., SIGGRAPH 2003](https://www.cc.gatech.edu/cpl/projects/graphcuttextures/)
  + Implemented by [Yezhen Cong](https://github.com/THU17cyz/GraphCut) & [Niranjan Thakurdesai](https://github.com/niranjantdesai/image-blending-graphcuts)
+ Photos used in demo by [Ricardo Chiarini](https://unsplash.com/photos/2VDa8bnLM8c), [Liu Sicheng](https://unsplash.com/photos/4-KqFyHKRdo), [Jim Josef](https://unsplash.com/photos/0spOq1mYtZw), and [Cedric VT](https://unsplash.com/photos/ua0SnGdN-m8) on [Unsplash](https://unsplash.com/)
