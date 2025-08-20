import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os
from typing import Tuple, List
import random

class PixelArtGenerator:
    def __init__(self, pixel_size: int = 8):
        """Initialize pixel art generator with customizable pixel size"""
        self.pixel_size = pixel_size
        
        # Kawaii/cute color palette inspired by the cat image
        self.cute_palette = [
            (45, 45, 55),     # Dark purple/black for outlines
            (75, 75, 95),     # Medium dark for shadows
            (120, 85, 140),   # Purple for main subjects
            (160, 120, 180),  # Light purple
            (255, 220, 180),  # Cream for highlights
            (255, 180, 120),  # Peach
            (255, 140, 140),  # Pink
            (140, 200, 120),  # Light green (like background)
            (100, 180, 100),  # Green
            (180, 220, 255),  # Light blue
            (255, 255, 255),  # White for eyes/highlights
            (255, 200, 0),    # Golden yellow for eyes
        ]
        
    def reduce_colors(self, image: Image.Image, num_colors: int = 12) -> Image.Image:
        """Reduce image to limited color palette"""
        # Convert to P mode with our cute palette
        palette_img = Image.new('P', (16, 16))
        
        # Flatten palette for PIL
        flat_palette = []
        for color in self.cute_palette[:num_colors]:
            flat_palette.extend(color)
        
        # Pad palette to 256 colors
        while len(flat_palette) < 768:
            flat_palette.extend([0, 0, 0])
        
        palette_img.putpalette(flat_palette)
        
        # Quantize image to our palette
        quantized = image.quantize(palette=palette_img, dither=Image.Dither.FLOYDSTEINBERG)
        return quantized.convert('RGB')
    
    def pixelate_image(self, image: Image.Image) -> Image.Image:
        """Convert image to pixel art style"""
        width, height = image.size
        
        # Calculate new dimensions
        new_width = width // self.pixel_size
        new_height = height // self.pixel_size
        
        # Resize down then up to create pixel effect
        small_image = image.resize((new_width, new_height), Image.Resampling.NEAREST)
        
        # Reduce colors for pixel art look
        small_image = self.reduce_colors(small_image, num_colors=12)
        
        # Scale back up with nearest neighbor for crisp pixels
        pixel_art = small_image.resize((width, height), Image.Resampling.NEAREST)
        
        return pixel_art
    
    def add_pixel_birthday_message(self, image: Image.Image, name: str = "Afshah") -> Image.Image:
        """Add cute pixel-style birthday message"""
        draw = ImageDraw.Draw(image)
        width, height = image.size
        
        # Create message
        message = f"Happy Birthday {name}! 🎂"
        
        # Try to load pixel-style font or use default
        try:
            # You can add a pixel font file here if available
            font_size = max(12, width // 40)
            font = ImageFont.load_default()
        except:
            font = ImageFont.load_default()
        
        # Calculate text position
        bbox = draw.textbbox((0, 0), message, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Position at bottom with cute background
        margin = 20
        bg_x = (width - text_width) // 2 - margin
        bg_y = height - text_height - margin * 2
        bg_width = text_width + margin * 2
        bg_height = text_height + margin
        
        # Draw cute rounded rectangle background
        self.draw_pixel_rect(draw, bg_x, bg_y, bg_width, bg_height, 
                           fill_color=(255, 255, 255, 200), 
                           border_color=(45, 45, 55))
        
        # Draw text with pixel outline effect
        text_x = bg_x + margin
        text_y = bg_y + margin // 2
        
        # Outline
        for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1), (-1, 0), (1, 0), (0, -1), (0, 1)]:
            draw.text((text_x + dx, text_y + dy), message, font=font, fill=(45, 45, 55))
        
        # Main text
        draw.text((text_x, text_y), message, font=font, fill=(255, 140, 140))
        
        return image
    
    def draw_pixel_rect(self, draw, x, y, width, height, fill_color, border_color):
        """Draw a pixel-style rectangle with rounded corners"""
        # Main rectangle
        draw.rectangle([x + 2, y, x + width - 2, y + height], fill=fill_color)
        draw.rectangle([x, y + 2, x + width, y + height - 2], fill=fill_color)
        
        # Rounded corners (pixel style)
        corner_points = [
            (x + 1, y + 1), (x + width - 1, y + 1),
            (x + 1, y + height - 1), (x + width - 1, y + height - 1)
        ]
        for point in corner_points:
            draw.point(point, fill=fill_color)
        
        # Border
        draw.rectangle([x, y, x + width, y + height], outline=border_color, width=2)
    
    def add_cute_decorations(self, image: Image.Image) -> Image.Image:
        """Add cute pixel decorations around the image"""
        draw = ImageDraw.Draw(image)
        width, height = image.size
        
        # Add pixel hearts and stars
        decorations = ['💖', '⭐', '🌟', '✨', '💫']
        
        # Top decorations
        for i in range(0, width, 80):
            if random.random() > 0.5:
                x = i + random.randint(-10, 10)
                y = random.randint(5, 25)
                self.draw_pixel_decoration(draw, x, y, random.choice(decorations))
        
        # Side decorations
        for i in range(40, height - 40, 60):
            if random.random() > 0.6:
                # Left side
                x = random.randint(5, 25)
                y = i + random.randint(-10, 10)
                self.draw_pixel_decoration(draw, x, y, random.choice(decorations))
                
                # Right side
                x = width - random.randint(5, 25)
                y = i + random.randint(-10, 10)
                self.draw_pixel_decoration(draw, x, y, random.choice(decorations))
        
        return image
    
    def draw_pixel_decoration(self, draw, x, y, decoration_type):
        """Draw cute pixel decorations"""
        colors = [(255, 140, 140), (255, 180, 120), (255, 220, 180), (180, 220, 255)]
        color = random.choice(colors)
        
        if decoration_type in ['💖', '❤️']:
            # Pixel heart
            self.draw_pixel_heart(draw, x, y, color)
        else:
            # Pixel star
            self.draw_pixel_star(draw, x, y, color)
    
    def draw_pixel_heart(self, draw, x, y, color):
        """Draw a cute pixel heart"""
        # Simple 5x5 pixel heart
        heart_pixels = [
            (1, 0), (2, 0), (4, 0), (5, 0),
            (0, 1), (3, 1), (6, 1),
            (0, 2), (6, 2),
            (1, 3), (5, 3),
            (2, 4), (4, 4),
            (3, 5)
        ]
        
        for hx, hy in heart_pixels:
            draw.rectangle([x + hx * 2, y + hy * 2, x + hx * 2 + 1, y + hy * 2 + 1], 
                         fill=color)
    
    def draw_pixel_star(self, draw, x, y, color):
        """Draw a cute pixel star"""
        # Simple 5x5 pixel star
        star_pixels = [
            (2, 0),
            (1, 1), (2, 1), (3, 1),
            (0, 2), (1, 2), (2, 2), (3, 2), (4, 2),
            (1, 3), (2, 3), (3, 3),
            (2, 4)
        ]
        
        for sx, sy in star_pixels:
            draw.rectangle([x + sx * 2, y + sy * 2, x + sx * 2 + 1, y + sy * 2 + 1], 
                         fill=color)
    
    def generate_pixel_art(self, input_path: str, output_path: str, 
                          pixel_size: int = 8, name: str = "Afshah") -> bool:
        """Main function to generate pixel art birthday image"""
        try:
            # Load image
            print(f"🎮 Loading image: {input_path}")
            image = Image.open(input_path)
            
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize if too large
            max_size = 800
            if image.width > max_size or image.height > max_size:
                ratio = min(max_size / image.width, max_size / image.height)
                new_size = (int(image.width * ratio), int(image.height * ratio))
                image = image.resize(new_size, Image.Resampling.LANCZOS)
            
            print(f"📐 Processing size: {image.size}")
            
            # Apply pixel art effect
            print("🎨 Converting to pixel art...")
            self.pixel_size = pixel_size
            pixel_art = self.pixelate_image(image)
            
            # Add birthday message
            print(f"🎂 Adding birthday message for {name}...")
            pixel_art = self.add_pixel_birthday_message(pixel_art, name)
            
            # Add cute decorations
            print("✨ Adding cute decorations...")
            pixel_art = self.add_cute_decorations(pixel_art)
            
            # Save result
            pixel_art.save(output_path, 'PNG', quality=95)
            print(f"✅ Pixel art saved: {output_path}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error generating pixel art: {e}")
            return False