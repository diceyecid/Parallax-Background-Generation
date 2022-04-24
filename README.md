# Parallax-Background-Generation

A parallax background generation method for 2D side-scrollers.

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
### Parallax Background Generation
### Graphcut Texture Generation
To use the texture generation portion of the pipeline by itself, `graphCut.py` can be called directly with the following signature.
```bash
python graphCut.py [path_in] [path_out] [direction] [patch_factor] [mode] [height_out] [width_out]
```
`path_in` and `path_out` are the file paths, including file name and extention.

`direction` indicates if the texture generates only horizontally, or both horizontally and vertically.  
+ Horizontal works best and is 0.  
+ Bidirectional is 1.

`patch_factor` is used to choose the size of patches used during generation. 
+ A value of 8 indicates a subpatch with 1/8 times the width of the input image for horizontal generation.  
+ A value of 8 would indicate a subpatch with 1/8 times the width and height of the input image for bidirectional generation.

`mode` takes a value between 1 and 3 which relate to different methods of patch selection. 
+ A value of 1 means the output is built placing subpatches in a random order.  
+ A value of 2 means the output is built by placing subpatches row-by-row. 
+ A value of 3 means the output is built using the entire input patch being placed row-by-row.

`height_out` and `width_out` are in pixels and determine the output image dimensions.  `height_out` should match the input image height for horizontal generation.

For example:
```bash
python graphCut.py mountainPatch.png mountainOutput.png 0 4 1 300 2000
```

## Attribution
### Graphcut Texture Generation
Method is from ["Graphcut Textures: Image and Video Synthesis Using Graph Cuts",  Kwatra et al., SIGGRAPH 2003](https://www.cc.gatech.edu/cpl/projects/graphcuttextures/)
Implementation by [Yezhen Cong](https://github.com/THU17cyz/GraphCut) & [Niranjan Thakurdesai](github.com/niranjantdesai/image-blending-graphcuts)

