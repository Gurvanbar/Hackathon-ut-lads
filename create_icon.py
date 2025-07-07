from PIL import Image, ImageDraw
import os

def create_app_icon():
    """Create a simple application icon"""
    # Create a 32x32 icon
    icon_size = 32
    image = Image.new('RGBA', (icon_size, icon_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # Draw a mail envelope shape
    # Background circle
    draw.ellipse([2, 2, icon_size-2, icon_size-2], fill=(40, 167, 69, 255), outline=(255, 255, 255, 255), width=1)
    
    # Mail envelope
    envelope_coords = [8, 12, 24, 12, 24, 20, 8, 20, 8, 12]
    draw.polygon(envelope_coords, fill=(255, 255, 255, 255))
    
    # Mail flap
    flap_coords = [8, 12, 16, 16, 24, 12]
    draw.polygon(flap_coords, fill=(255, 255, 255, 255))
    
    # Save as ICO file
    image.save('app_icon.ico', format='ICO')
    print("Icon created successfully!")

if __name__ == "__main__":
    create_app_icon()
