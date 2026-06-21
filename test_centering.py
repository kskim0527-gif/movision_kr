from PIL import Image, ImageDraw, ImageFont

font = ImageFont.truetype("C:/Windows/Fonts/georgia.ttf", 170)

def draw_centered_text(text, target_x, target_y):
    temp = Image.new("L", (1000, 1000), 0)
    dtemp = ImageDraw.Draw(temp)
    dtemp.text((500, 500), text, font=font, fill=255, anchor="mm")
    bbox = temp.getbbox()
    if bbox:
        cx = (bbox[0] + bbox[2]) / 2.0
        cy = (bbox[1] + bbox[3]) / 2.0
        off_x = 500 - cx
        off_y = 500 - cy
        print(f"'{text}' offset: x={off_x}, y={off_y}")
        return off_x, off_y
    return 0, 0

draw_centered_text("12", 233, 233)
draw_centered_text("3", 233, 233)
draw_centered_text("6", 233, 233)
draw_centered_text("9", 233, 233)
