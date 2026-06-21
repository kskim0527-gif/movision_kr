from PIL import Image, ImageDraw, ImageFont
import math

font = ImageFont.truetype("C:/Windows/Fonts/georgia.ttf", 170)

def find_max_r():
    # We want to find the maximum `r` for "12", "3", "6", "9" 
    # such that no ink is drawn outside a circle of radius 233 centered at (233, 233).
    # Since we use draw_centered_text, the text is perfectly visually centered at the target coordinates.
    
    # Pre-calculate the exact ink mask and center offset for each text
    text_info = {}
    temp = Image.new("L", (1000, 1000), 0)
    dtemp = ImageDraw.Draw(temp)
    for text in ["12", "3", "6", "9"]:
        dtemp.rectangle([0,0,1000,1000], fill=0)
        dtemp.text((500, 500), text, font=font, fill=255, anchor="mm")
        bbox = temp.getbbox()
        if not bbox: continue
        cx = (bbox[0] + bbox[2]) / 2.0
        cy = (bbox[1] + bbox[3]) / 2.0
        off_x = 500 - cx
        off_y = 500 - cy
        
        # Crop the mask to just the ink to make testing faster
        mask = temp.crop(bbox)
        text_info[text] = {
            'mask': mask,
            'off_x': off_x,
            'off_y': off_y,
            'w': bbox[2] - bbox[0],
            'h': bbox[3] - bbox[1]
        }

    # Now, for a given r, we place the text and check if any pixel > 0 is outside r=233.
    # To do this, we can draw the text on a 466x466 canvas and check pixels.
    # Actually, a simpler way: iterate r from 180 down to 100.
    
    def check_fit(text, r):
        info = text_info[text]
        # target coordinates
        if text == "12": target = (233, 233 - r)
        elif text == "3": target = (233 + r, 233)
        elif text == "6": target = (233, 233 + r)
        elif text == "9": target = (233 - r, 233)
        
        # the center of the ink is exactly at target
        # so the top-left of the mask is at:
        # target_x - w/2, target_y - h/2
        left = target[0] - info['w'] / 2.0
        top = target[1] - info['h'] / 2.0
        
        # Iterate over all pixels in the mask
        pixels = info['mask'].load()
        for y in range(info['h']):
            for x in range(info['w']):
                if pixels[x, y] > 0:
                    px = left + x
                    py = top + y
                    # Distance from center (233, 233)
                    dist_sq = (px - 233)**2 + (py - 233)**2
                    if dist_sq > 232**2: # allow 1 pixel margin
                        return False
        return True

    for text in ["12", "3", "6", "9"]:
        # Find max r
        for r in range(233, 0, -1):
            if check_fit(text, r):
                print(f"Max r for '{text}' is {r}")
                break

find_max_r()
