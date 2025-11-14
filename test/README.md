# Test Directory

This directory contains test files for the static-site-image-optimizer.

## Setup

Download test images:

```bash
./download_images.sh
```

## Test Images

The test uses the following images from Wikimedia Commons:

- [Eye of the Bird](https://upload.wikimedia.org/wikipedia/commons/thumb/7/7d/Eye_of_the_Bird.jpg/3240px-Eye_of_the_Bird.jpg)
- [Raya de arrecife](https://upload.wikimedia.org/wikipedia/commons/thumb/d/d6/Raya_de_arrecife_%28Taeniura_lymma%29%2C_mar_Rojo%2C_Egipto%2C_2023-04-14%2C_DD_64.jpg/3240px-Raya_de_arrecife_%28Taeniura_lymma%29%2C_mar_Rojo%2C_Egipto%2C_2023-04-14%2C_DD_64.jpg)
- [Val Montanaia](https://upload.wikimedia.org/wikipedia/commons/9/90/Val_Montanaia.jpg)

## Running Tests

```bash
uv run test_conversion.py
```

This will convert the images to WebP format and update references in `index.html`.
