from PIL import Image, ImageDraw, ImageFont

font = ImageFont.truetype("C:/Windows/Fonts/georgia.ttf", 170)
img = Image.new('RGB', (466, 466), (0,0,0))
d = ImageDraw.Draw(img)

# anchor 'mm' test
cx, cy = 233, 233
bbox = d.textbbox((cx, cy), "12", font=font, anchor="mm")
print("12 bbox with mm:", bbox)
print("height:", bbox[3] - bbox[1])
print("bbox center Y:", (bbox[1] + bbox[3]) / 2)

# Get precise ink mask bounding box
mask = font.getmask("12")
print("Ink bounding box:", mask.getbbox())
