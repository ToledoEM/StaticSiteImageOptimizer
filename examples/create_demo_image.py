from PIL import Image
import os

os.makedirs('examples/site/images', exist_ok=True)
img = Image.new('RGB', (100, 50), color=(73, 109, 137))
img.save('examples/site/images/example.jpg', quality=85)

# Simple HTML that references the image
os.makedirs('examples/site', exist_ok=True)
with open('examples/site/index.html', 'w', encoding='utf8') as fh:
    fh.write('<html>\n<body>\n<img src="images/example.jpg" alt="Demo">\n</body>\n</html>')
