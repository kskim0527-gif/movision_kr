from PIL import Image, ImageDraw, ImageFont

font = ImageFont.truetype("C:/Windows/Fonts/georgia.ttf", 170)
img = Image.new('RGB', (466, 466), (0,0,0))
d = ImageDraw.Draw(img)

def check_offset(text):
    bbox = d.textbbox((233, 233), text, font=font, anchor="mm")
    center_y = (bbox[1] + bbox[3]) / 2
    print(f"'{text}' bbox center Y:", center_y)
    
check_offset("12")
check_offset("3")
check_offset("6")
check_offset("9")
