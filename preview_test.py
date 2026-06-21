import os
import math
from PIL import Image

def paste_rotated(bg, fg, pivot_x, pivot_y, angle):
    # Rotate the foreground image around the pivot
    # Pillow's rotate does counter-clockwise by default, LVGL does clockwise.
    # So we use -angle.
    # Center of rotation is pivot_x, pivot_y.
    # To do this, we translate the image so pivot is at center, rotate, then translate back.
    w, h = fg.size
    
    # Create a larger canvas to avoid clipping during rotation
    max_dim = int(math.ceil(math.sqrt(w*w + h*h)))
    temp = Image.new('RGBA', (max_dim, max_dim), (0, 0, 0, 0))
    
    # Paste fg onto temp such that pivot is at temp's center
    cx, cy = max_dim // 2, max_dim // 2
    paste_x = cx - pivot_x
    paste_y = cy - pivot_y
    temp.paste(fg, (paste_x, paste_y))
    
    # Rotate around center
    temp = temp.rotate(-angle, resample=Image.BICUBIC, center=(cx, cy))
    
    # Now paste temp onto bg such that temp's center is at bg's center
    bg_w, bg_h = bg.size
    bg_cx, bg_cy = bg_w // 2, bg_h // 2
    
    final_x = bg_cx - cx
    final_y = bg_cy - cy
    bg.alpha_composite(temp, (final_x, final_y))

def make_preview():
    base_dir = "main/flash_data/clock_3"
    bg = Image.open(os.path.join(base_dir, "screen.png")).convert("RGBA")
    hour = Image.open(os.path.join(base_dir, "hour.png")).convert("RGBA")
    minute = Image.open(os.path.join(base_dir, "minute.png")).convert("RGBA")
    second = Image.open(os.path.join(base_dir, "second.png")).convert("RGBA")
    center = Image.open(os.path.join(base_dir, "center.png")).convert("RGBA")
    
    # 12:00
    paste_rotated(hour, 15, 140, 0)
    paste_rotated(minute, 12, 190, 0)
    paste_rotated(second, 7, 190, 0)
    
    bg_w, bg_h = bg.size
    cx, cy = bg_w // 2, bg_h // 2
    bg.alpha_composite(center, (cx - 16, cy - 16))
    
    bg.save("preview_clock_1200.png")

    # 3:15
    bg2 = Image.open(os.path.join(base_dir, "screen.png")).convert("RGBA")
    paste_rotated(hour, 15, 140, 90)
    paste_rotated(minute, 12, 190, 90)
    paste_rotated(second, 7, 190, 90)
    bg2.alpha_composite(center, (cx - 16, cy - 16))
    bg2.save("preview_clock_315.png")

if __name__ == "__main__":
    make_preview()
