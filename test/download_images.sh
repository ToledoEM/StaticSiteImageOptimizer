#!/bin/bash
# Download the demo images from Wikimedia Commons and resize them to web size
# (max 1600 px on the long side). Colour profiles and EXIF are kept, so the
# wide-gamut images still exercise ssio's colour handling.

set -e

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MAX_SIZE=1600

mkdir -p "$ROOT/test/img"
cd "$ROOT/test/img"

# Wikimedia rejects requests without a descriptive User-Agent.
UA="ssio-test-downloader (https://github.com/ToledoEM/StaticSiteImageOptimizer)"

fetch() {
    echo "Downloading $1..."
    curl -fsSL -A "$UA" -o "$1" "$2"
}

fetch "Eye_of_the_Bird.jpg" "https://upload.wikimedia.org/wikipedia/commons/0/0a/Arara-vermelha_-_PARNA_da_Serra_da_Capivara_-_LeonardoRamos%28001%29.jpg"
fetch "Raya_de_arrecife.jpg" "https://upload.wikimedia.org/wikipedia/commons/d/d6/Raya_de_arrecife_%28Taeniura_lymma%29%2C_mar_Rojo%2C_Egipto%2C_2023-04-14%2C_DD_64.jpg"
fetch "Val_Montanaia.jpg" "https://upload.wikimedia.org/wikipedia/commons/9/90/Val_Montanaia.jpg"
fetch "Jupiter.png" "https://upload.wikimedia.org/wikipedia/commons/3/34/Jupiter_accurate_colour.png"

echo "Resizing to max ${MAX_SIZE}px..."
uv run --quiet --project "$ROOT" python - "$MAX_SIZE" Eye_of_the_Bird.jpg Raya_de_arrecife.jpg Val_Montanaia.jpg Jupiter.png <<'EOF'
import sys
from PIL import Image

max_size = int(sys.argv[1])
for path in sys.argv[2:]:
    with Image.open(path) as im:
        im.load()
        extra = {k: im.info[k] for k in ("icc_profile", "exif") if im.info.get(k)}
        im.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        if path.endswith(".jpg"):
            im.save(path, "JPEG", quality=92, subsampling=0, **extra)
        else:
            im.save(path, "PNG", optimize=True, **extra)
        print(f"  {path}: {im.width}x{im.height}")
EOF

echo "Images saved to test/img/"
