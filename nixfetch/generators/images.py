"""
Image generators for visualizing flake information
"""
from pathlib import Path


class ImageGenerator:
    """Base class for image generation"""
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)


class ColorPaletteGenerator(ImageGenerator):
    """Generates color palette images from base16 color schemes"""
    
    def generate(self, colors: dict[str, str], name: str = "palette") -> Path | None:
        """Generate a color palette image"""
        try:
            from PIL import Image, ImageDraw, ImageFont
        except ImportError:
            # Pillow not available, skip image generation
            return None
        
        # Create image with color swatches
        swatch_width = 100
        swatch_height = 80
        cols = 4
        rows = (len(colors) + cols - 1) // cols
        
        img_width = swatch_width * cols
        img_height = swatch_height * rows
        
        img = Image.new('RGB', (img_width, img_height), color='white')
        draw = ImageDraw.Draw(img)
        
        sorted_colors = sorted(colors.items())
        
        for idx, (color_name, color_value) in enumerate(sorted_colors):
            row = idx // cols
            col = idx % cols
            
            x = col * swatch_width
            y = row * swatch_height
            
            # Draw color swatch
            try:
                color_hex = f"#{color_value}" if not color_value.startswith("#") else color_value
                draw.rectangle(
                    [x, y, x + swatch_width, y + swatch_height],
                    fill=color_hex,
                    outline='black'
                )
                
                # Add label (use contrasting color)
                # Simple heuristic: use white text for dark colors, black for light
                rgb = tuple(int(color_value[i:i+2], 16) for i in (0, 2, 4))
                brightness = sum(rgb) / 3
                text_color = 'white' if brightness < 128 else 'black'
                
                # Draw text in center
                text = color_name
                try:
                    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
                except:
                    font = ImageFont.load_default()
                
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                text_x = x + (swatch_width - text_width) // 2
                text_y = y + (swatch_height - text_height) // 2
                
                draw.text((text_x, text_y), text, fill=text_color, font=font)
            except:
                pass
        
        output_path = self.output_dir / f"{name}.png"
        img.save(output_path)
        return output_path
