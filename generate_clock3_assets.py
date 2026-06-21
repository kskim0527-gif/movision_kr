import os
from PIL import Image, ImageDraw, ImageFont

def create_clock3_assets():
    out_dir = "main/flash_data/clock_3"
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    w, h = 466, 466
    cx, cy = w // 2, h // 2

    # 1. Background (466x466)
    bg = Image.new('RGB', (w, h), (0, 0, 0)) # True black
    draw_bg = ImageDraw.Draw(bg, 'RGBA')
    
    font_color = (195, 195, 195, 255) # Bright Grey
    font_size = 176 # Decreased by 20%
    
    # Try to load Georgia, fallback to Times, or default
    font_paths = [
        "C:/Windows/Fonts/georgia.ttf",
        "C:/Windows/Fonts/times.ttf",
        "C:/Windows/Fonts/arial.ttf"
    ]
    font = None
    for path in font_paths:
        if os.path.exists(path):
            font = ImageFont.truetype(path, font_size)
            print(f"Using font: {path}")
            break
            
    if font:
        def draw_centered_text(text, target_x, target_y):
            # To visually center the text perfectly, find exact ink bounding box
            temp = Image.new("L", (1000, 1000), 0)
            dtemp = ImageDraw.Draw(temp)
            dtemp.text((500, 500), text, font=font, fill=255, anchor="mm")
            bbox = temp.getbbox()
            if bbox:
                cx = (bbox[0] + bbox[2]) / 2.0
                cy = (bbox[1] + bbox[3]) / 2.0
                off_x = 500 - cx
                off_y = 500 - cy
                draw_bg.text((target_x + off_x, target_y + off_y), text, font=font, fill=font_color, anchor="mm")
            else:
                draw_bg.text((target_x, target_y), text, font=font, fill=font_color, anchor="mm")

        # Moved an additional 30pt towards the center
        draw_centered_text("12", cx, cy - 121)
        draw_centered_text("3", cx + 130, cy)
        draw_centered_text("6", cx, cy + 110)
        draw_centered_text("9", cx - 129, cy)
    else:
        print("Could not load a suitable font!")

    bg.save(os.path.join(out_dir, "screen.png"))

    hour_color = (237, 206, 139, 255) # #EDCE8B Light beige/yellow
    minute_outline = (255, 255, 255, 255) # White

    def draw_smooth_rounded_rectangle(size, rect, radius, fill=None, outline=None, width=0):
        scale = 4
        large_size = (size[0] * scale, size[1] * scale)
        large_rect = [r * scale for r in rect]
        large_radius = radius * scale
        large_width = width * scale
        
        img = Image.new('RGBA', large_size, (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle(large_rect, radius=large_radius, fill=fill, outline=outline, width=large_width)
        return img.resize(size, Image.Resampling.LANCZOS)

    # 2. Hour Hand (27 x 210)
    hour = draw_smooth_rounded_rectangle((27, 210), [1, 29, 26, 160], 12, fill=hour_color)
    hour_shadow = draw_smooth_rounded_rectangle((27, 210), [1, 29, 26, 160], 12, fill=(0, 0, 0, 100))
    hour.save(os.path.join(out_dir, "hour.png"))
    hour_shadow.save(os.path.join(out_dir, "hour_shadow.png"))

    # 3. Minute Hand (23 x 275)
    minute = draw_smooth_rounded_rectangle((23, 275), [1, 35, 22, 225], 10, outline=minute_outline, width=3)
    minute_shadow = draw_smooth_rounded_rectangle((23, 275), [1, 35, 22, 225], 10, outline=(0, 0, 0, 100), width=3)
    minute.save(os.path.join(out_dir, "minute.png"))
    minute_shadow.save(os.path.join(out_dir, "minute_shadow.png"))

    # 4. Second Hand (15 x 260)
    second = Image.new('RGBA', (15, 260), (0, 0, 0, 0))
    draw_second = ImageDraw.Draw(second)
    sec_color = (255, 140, 0, 255) # Orange/Amber
    
    # Main needle: x=6 to 8 (3 px wide), y=7 to 234.
    draw_second.rectangle([6, 7, 8, 234], fill=sec_color)
    
    # Pivot hollow circle: x=1 to 13 (13 px). Center = 7. y=234 to 246 (13 px). Center = 240.
    draw_second.ellipse([1, 234, 13, 246], outline=sec_color, width=2)
    
    second.save(os.path.join(out_dir, "second.png"))

    # 5. Center Dot (32 x 32)
    # In this design, the center dot is transparent because the second hand has a hollow pivot ring.
    center = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
    center.save(os.path.join(out_dir, "center.png"))

    print("Typography Assets generated successfully.")

if __name__ == "__main__":
    create_clock3_assets()
