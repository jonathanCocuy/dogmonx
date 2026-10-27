"""
Genera todos los íconos necesarios para la app DogMonX.
Requiere: pip install Pillow
"""
from PIL import Image, ImageDraw
import os, math

ASSETS = os.path.join(os.path.dirname(__file__), "..", "assets", "images")
os.makedirs(ASSETS, exist_ok=True)

BG      = (10, 10, 10, 255)
CYAN    = (0, 194, 255, 255)
CYAN_DK = (0, 136, 187, 255)
BLACK   = (10, 10, 10, 255)
WHITE   = (255, 255, 255, 255)
TRANS   = (0, 0, 0, 0)

def draw_dog_monitor(draw: ImageDraw.ImageDraw, cx: float, cy: float, r: float, fg: tuple):
    # outer ring
    draw.ellipse([cx-r, cy-r, cx+r, cy+r], outline=fg, width=max(2, int(r*0.045)))
    # dashed outer ring (simplified: 12 short arcs as dots)
    dash_r = r * 1.12
    for i in range(12):
        angle = math.radians(i * 30)
        dx = cx + math.cos(angle) * dash_r
        dy = cy + math.sin(angle) * dash_r
        dr = max(2, int(r * 0.035))
        draw.ellipse([dx-dr, dy-dr, dx+dr, dy+dr], fill=fg)
    # inner circle (lens)
    ir = r * 0.80
    draw.ellipse([cx-ir, cy-ir, cx+ir, cy+ir], fill=(17, 17, 17, 255))
    # dog head (oval)
    dh_rx = r * 0.34
    dh_ry = r * 0.30
    draw.ellipse([cx-dh_rx, cy-dh_ry*0.2, cx+dh_rx, cy+dh_ry*1.8], fill=fg)
    # ears
    ear_w, ear_h = r*0.27, r*0.40
    # left ear
    lx, ly = cx - r*0.38, cy - r*0.32
    draw.ellipse([lx, ly, lx+ear_w, ly+ear_h], fill=fg)
    # right ear
    rx2, ry2 = cx + r*0.10, cy - r*0.32
    draw.ellipse([rx2, ry2, rx2+ear_w, ry2+ear_h], fill=fg)
    # snout
    sn_rx, sn_ry = r*0.20, r*0.15
    draw.ellipse([cx-sn_rx, cy+r*0.28, cx+sn_rx, cy+r*0.28+sn_ry*2], fill=CYAN_DK if fg == CYAN else (200,200,200,255))
    # nose
    ns = r * 0.07
    draw.ellipse([cx-ns, cy+r*0.22, cx+ns, cy+r*0.22+ns*2], fill=(10,10,10,255))
    # eyes
    ey = cy + r * 0.05
    eye_r = r * 0.055
    draw.ellipse([cx-r*0.16-eye_r, ey-eye_r, cx-r*0.16+eye_r, ey+eye_r], fill=(10,10,10,255))
    draw.ellipse([cx+r*0.16-eye_r, ey-eye_r, cx+r*0.16+eye_r, ey+eye_r], fill=(10,10,10,255))
    # corner brackets
    br = r * 1.30
    bl = max(2, int(r * 0.04))
    bs = r * 0.22
    for (bx, by, signs) in [
        (cx-br, cy-br, (1,1)),
        (cx+br, cy-br, (-1,1)),
        (cx-br, cy+br, (1,-1)),
        (cx+br, cy+br, (-1,-1)),
    ]:
        sx, sy = signs
        draw.line([bx, by, bx+sx*bs, by], fill=fg, width=bl)
        draw.line([bx, by, bx, by+sy*bs], fill=fg, width=bl)

def make_icon(size: int, transparent_bg=False) -> Image.Image:
    bg = TRANS if transparent_bg else BG
    img = Image.new("RGBA", (size, size), bg)
    draw = ImageDraw.Draw(img)
    r = size * 0.30
    draw_dog_monitor(draw, size/2, size/2 + size*0.02, r, CYAN)
    return img

def save_png(img: Image.Image, name: str):
    path = os.path.join(ASSETS, name)
    img.save(path, "PNG")
    print(f"  ✓  {name}  ({img.size[0]}×{img.size[1]})")

print("Generando íconos DogMonX...")

save_png(make_icon(1024), "icon.png")
save_png(make_icon(1024, transparent_bg=True), "android-icon-foreground.png")
save_png(Image.new("RGBA", (1024, 1024), BG), "android-icon-background.png")

mono = make_icon(1024, transparent_bg=True)
# recolor to white for monochrome
pixels = mono.load()
for y in range(1024):
    for x in range(1024):
        r2,g,b,a = pixels[x,y]
        if a > 0:
            pixels[x,y] = (255,255,255,a)
save_png(mono, "android-icon-monochrome.png")

save_png(make_icon(1024), "splash-icon.png")
save_png(make_icon(1024).resize((64,64), Image.LANCZOS), "favicon.png")

print("\nListo! Archivos guardados en assets/images/")
