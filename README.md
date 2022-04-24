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

## Useage
### Parallax Background Generation
### Graphcut Texture Generation
To use the texture generation portion of the pipeline by itself, `graphCut.py` can be called directly with the following signature.
```bash
python graphCut.py [path_in] [path_out] [mode] [patch_factor] [direction] [height_out] [width_out]
```
For example:
```bash
python graphCut.py mountainPatch.png mountainOutput.png 0 4 1 300 2000
```

## Attribution
### Graphcut Texture Generation
Method is from "Graphcut Textures: Image and Video Synthesis Using Graph Cuts",  Kwatra et al., SIGGRAPH 2003
Implementation by [Yezhen Cong](https://github.com/THU17cyz/GraphCut) & [Niranjan Thakurdesai](github.com/niranjantdesai/image-blending-graphcuts)

