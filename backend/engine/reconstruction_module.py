import json
import os
import svgwrite
from PIL import Image
import cairosvg
import tempfile

class VisualReconstructionEngine:
    def __init__(self, json_payload):
        """
        Initializes the engine with the extracted JSON payload.
        The payload is expected to be a dictionary or a JSON string.
        """
        if isinstance(json_payload, str):
            self.data = json.loads(json_payload)
        else:
            self.data = json_payload
            
        self.width = self.data.get("width", 800)
        self.height = self.data.get("height", 600)
        self.elements = self.data.get("elements", [])

    def reconstruct_svg(self, output_svg_path):
        """
        Re-builds and renders a complete CAD/SVG drawing strictly from the extracted JSON output.
        """
        dwg = svgwrite.Drawing(output_svg_path, size=(self.width, self.height))
        
        # Adding a white background for better visibility
        dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'), rx=None, ry=None, fill='white'))

        for elem in self.elements:
            etype = elem.get("type")
            if etype == "line":
                dwg.add(dwg.line(
                    start=(elem["start_x"], elem["start_y"]),
                    end=(elem["end_x"], elem["end_y"]),
                    stroke=elem.get("color", "black"),
                    stroke_width=elem.get("stroke_width", 1)
                ))
            elif etype == "rect":
                dwg.add(dwg.rect(
                    insert=(elem["x"], elem["y"]),
                    size=(elem["width"], elem["height"]),
                    fill=elem.get("fill", "none"),
                    stroke=elem.get("color", "black"),
                    stroke_width=elem.get("stroke_width", 1)
                ))
            elif etype == "circle":
                dwg.add(dwg.circle(
                    center=(elem["cx"], elem["cy"]),
                    r=elem["r"],
                    fill=elem.get("fill", "none"),
                    stroke=elem.get("color", "black"),
                    stroke_width=elem.get("stroke_width", 1)
                ))
            elif etype == "text":
                dwg.add(dwg.text(
                    elem["text"],
                    insert=(elem["x"], elem["y"]),
                    fill=elem.get("color", "black"),
                    font_size=elem.get("font_size", 12)
                ))
        
        dwg.save()
        return output_svg_path

    def reconstruct_png(self, output_png_path):
        """
        Renders the reconstructed SVG to a PNG file.
        """
        with tempfile.NamedTemporaryFile(suffix=".svg", delete=False) as temp_svg:
            temp_svg_path = temp_svg.name
            
        self.reconstruct_svg(temp_svg_path)
        
        # Convert SVG to PNG
        cairosvg.svg2png(url=temp_svg_path, write_to=output_png_path)
        
        os.remove(temp_svg_path)
        return output_png_path

    def generate_comparison(self, original_image_path, output_comparison_path):
        """
        Generates side-by-side comparison images (Panel 1: Original Ingested Blueprint vs Panel 2: Reconstructed Drawing).
        """
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_png:
            reconstructed_png_path = temp_png.name
            
        self.reconstruct_png(reconstructed_png_path)
        
        try:
            original_img = Image.open(original_image_path).convert("RGBA")
        except Exception as e:
            print(f"Failed to load original image: {e}")
            original_img = Image.new("RGBA", (self.width, self.height), "white")
            
        reconstructed_img = Image.open(reconstructed_png_path).convert("RGBA")
        
        # Resize reconstructed image to match original image height if needed
        # Or place side by side directly
        width1, height1 = original_img.size
        width2, height2 = reconstructed_img.size
        
        max_height = max(height1, height2)
        total_width = width1 + width2
        
        comparison_img = Image.new("RGBA", (total_width, max_height), "white")
        comparison_img.paste(original_img, (0, 0))
        comparison_img.paste(reconstructed_img, (width1, 0))
        
        comparison_img.save(output_comparison_path)
        
        os.remove(reconstructed_png_path)
        return output_comparison_path
