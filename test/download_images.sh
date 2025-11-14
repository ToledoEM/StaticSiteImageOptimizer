#!/bin/bash

set -e

mkdir -p img
cd img

echo "Downloading test images..."

echo "Downloading Eye of the Bird..."
curl -L -o "3240px-Eye_of_the_Bird.jpg" "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7d/Eye_of_the_Bird.jpg/3240px-Eye_of_the_Bird.jpg"

echo "Downloading Raya de arrecife..."
curl -L -o "3240px-Raya_de_arrecife_(Taeniura_lymma),_mar_Rojo,_Egipto,_2023-04-14,_DD_64.jpg" "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d6/Raya_de_arrecife_%28Taeniura_lymma%29%2C_mar_Rojo%2C_Egipto%2C_2023-04-14%2C_DD_64.jpg/3240px-Raya_de_arrecife_%28Taeniura_lymma%29%2C_mar_Rojo%2C_Egipto%2C_2023-04-14%2C_DD_64.jpg"

echo "Downloading Val Montanaia..."
curl -L -o "Val_Montanaia.jpg" "https://upload.wikimedia.org/wikipedia/commons/9/90/Val_Montanaia.jpg"

echo "Downloading Jupiter..."
curl -L -o "Jupiter_accurate_colour.jpg" "https://upload.wikimedia.org/wikipedia/commons/3/34/Jupiter_accurate_colour.png"

echo "Download complete!"
echo "Images saved to img/"
