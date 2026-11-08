# Test Directory

This directory contains test files for the static-site-image-optimizer.

## Setup

Download test images:

```bash
./download_images.sh
```

## Test Images

The test uses the following images from Wikimedia Commons, resized to max 1600 px on the long side by `download_images.sh`:

- [Eye of the Bird](https://commons.wikimedia.org/wiki/File:Arara-vermelha_-_PARNA_da_Serra_da_Capivara_-_LeonardoRamos(001).jpg) (4244 × 2829 px, 6.63 MB) saved as `img/Eye_of_the_Bird.jpg`
- [Raya de arrecife](https://commons.wikimedia.org/wiki/File:Raya_de_arrecife_(Taeniura_lymma),_mar_Rojo,_Egipto,_2023-04-14,_DD_64.jpg) (7465 × 4977 px, 8.76 MB) saved as `img/Raya_de_arrecife.jpg`
- [Jupiter](https://commons.wikimedia.org/wiki/File:Jupiter_accurate_colour.png) (2232 × 2160 px, 2.58 MB) saved as `img/Jupiter.png`
- [Val Montanaia](https://commons.wikimedia.org/wiki/File:Val_Montanaia.jpg) (9557 × 6336 px, 38.04 MB) saved as `img/Val_Montanaia.jpg`

## Running Tests

```bash
uv run test_conversion.py
```

This will convert the images to WebP format and update references in `index.html`.
