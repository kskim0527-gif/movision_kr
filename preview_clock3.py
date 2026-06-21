import os
from PIL import Image

def preview_clock():
    out_dir = "main/flash_data/clock_3"
    
    # Load images
    bg = Image.open(os.path.join(out_dir, "screen.png")).convert("RGBA")
    hour = Image.open(os.path.join(out_dir, "hour.png")).convert("RGBA")
    hour_shadow = Image.open(os.path.join(out_dir, "hour_shadow.png")).convert("RGBA")
    minute = Image.open(os.path.join(out_dir, "minute.png")).convert("RGBA")
    minute_shadow = Image.open(os.path.join(out_dir, "minute_shadow.png")).convert("RGBA")
    second = Image.open(os.path.join(out_dir, "second.png")).convert("RGBA")
    center = Image.open(os.path.join(out_dir, "center.png")).convert("RGBA")
    
    # Angles for 10:10:35 (Classic watch display time)
    h_angle = (12 % 12) * 30 + 15 * 0.5
    m_angle = 15 * 6 + 30 * 0.1
    s_angle = 30 * 6
    
    def paste_rotated(hand, pivot_x, pivot_y, angle, offset_x=0, offset_y=0):
        temp = Image.new('RGBA', (466, 466), (0, 0, 0, 0))
        # Place hand such that its pivot is at 233, 233
        pos_x = 233 - pivot_x
        pos_y = 233 - pivot_y
        temp.paste(hand, (pos_x, pos_y))
        # Rotate clockwise
        temp = temp.rotate(-angle, resample=Image.Resampling.BICUBIC, center=(233, 233))
        
        if offset_x != 0 or offset_y != 0:
            temp2 = Image.new('RGBA', (466, 466), (0, 0, 0, 0))
            temp2.paste(temp, (offset_x, offset_y))
            bg.alpha_composite(temp2)
        else:
            bg.alpha_composite(temp)

    # Paste shadows with offsets
    paste_rotated(hour_shadow, 13, 180, h_angle, offset_x=4, offset_y=4)
    paste_rotated(minute_shadow, 11, 245, m_angle, offset_x=4, offset_y=4)

    # Paste actual hands
    paste_rotated(hour, 13, 180, h_angle)
    paste_rotated(minute, 11, 245, m_angle)
    paste_rotated(second, 7, 240, s_angle)
    
    # Center dot
    # Center dot size is 32x32, its center is 16, 16.
    bg.alpha_composite(center, (233 - 16, 233 - 16))
    
    preview_path = os.path.abspath(os.path.join("preview_clock.png"))
    flash_data_preview_path = os.path.abspath(os.path.join(out_dir, "preview_clock.png"))
    
    bg.save(preview_path)
    bg.save(flash_data_preview_path)
    
    print("Preview saved to:", preview_path)
    print("Preview saved to:", flash_data_preview_path)

if __name__ == "__main__":
    preview_clock()
