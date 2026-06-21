from PIL import Image, ImageDraw, ImageFont

font = ImageFont.truetype("C:/Windows/Fonts/georgia.ttf", 170)
img = Image.new('RGB', (466, 466), (0,0,0))
d = ImageDraw.Draw(img)

# Try drawing at 233, 233-13
cx, cy = 233, 233
bbox = d.textbbox((cx, cy - 13), "12", font=font, anchor="mm")
print("New bbox center Y:", (bbox[1] + bbox[3]) / 2)
