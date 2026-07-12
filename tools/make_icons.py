"""Generate PWA icons: saffron rounded square with white 'GG' letters."""
from PIL import Image, ImageDraw, ImageFont
import os

SAFFRON = (200, 107, 31, 255)   # #c86b1f
WHITE = (253, 248, 242, 255)    # #fdf8f2 warm white
OUT = os.path.join(os.path.dirname(__file__), '..', 'icons')

FONT_CANDIDATES = [
    r'C:\Windows\Fonts\georgiab.ttf',   # Georgia Bold
    r'C:\Windows\Fonts\playfair.ttf',
    r'C:\Windows\Fonts\timesbd.ttf',    # Times New Roman Bold
    r'C:\Windows\Fonts\georgia.ttf',
]

def pick_font(size):
    for p in FONT_CANDIDATES:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    raise SystemExit('No serif font found')

def make(size, maskable=False, radius_ratio=0.22):
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if maskable:
        # full-bleed background, content within 80% safe zone
        d.rectangle([0, 0, size, size], fill=SAFFRON)
        text_size = int(size * 0.34)
    else:
        r = int(size * radius_ratio)
        d.rounded_rectangle([0, 0, size - 1, size - 1], radius=r, fill=SAFFRON)
        text_size = int(size * 0.42)
    font = pick_font(text_size)
    text = 'GG'
    bbox = d.textbbox((0, 0), text, font=font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = (size - w) / 2 - bbox[0]
    y = (size - h) / 2 - bbox[1]
    d.text((x, y), text, font=font, fill=WHITE)
    return img

os.makedirs(OUT, exist_ok=True)
make(192).save(os.path.join(OUT, 'icon-192.png'))
make(512).save(os.path.join(OUT, 'icon-512.png'))
make(512, maskable=True).save(os.path.join(OUT, 'maskable-512.png'))
print('Icons written: icon-192.png, icon-512.png, maskable-512.png')
