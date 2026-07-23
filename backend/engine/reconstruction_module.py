import json
import os
import tempfile
import svgwrite
from PIL import Image, ImageDraw, ImageFont

try:
    import cairosvg
except ImportError:
    cairosvg = None

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None


class VisualReconstructionEngine:
    def __init__(self, json_payload=None):
        """
        Initializes the engine with the extracted JSON payload.
        The payload can be a dictionary, list, or JSON string.
        """
        if isinstance(json_payload, str):
            self.data = json.loads(json_payload)
        elif isinstance(json_payload, dict):
            self.data = json_payload
        elif isinstance(json_payload, list):
            self.data = {"elements": json_payload}
        else:
            self.data = {"elements": []}
            
        self.width = self.data.get("width", 800)
        self.height = self.data.get("height", 600)
        self.elements = self.data.get("elements", [])

    def render_svg(self) -> str:
        """Renders the reconstructed SVG drawing as an in-memory SVG XML string."""
        dwg = svgwrite.Drawing(size=(self.width, self.height))
        dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'), fill='#0a0f1e'))

        for gx in range(50, int(self.width), 100):
            dwg.add(dwg.line(start=(gx, 0), end=(gx, self.height), stroke='#1e293b', stroke_width=0.5))
        for gy in range(50, int(self.height), 100):
            dwg.add(dwg.line(start=(0, gy), end=(self.width, gy), stroke='#1e293b', stroke_width=0.5))

        for elem in self.elements:
            etype = elem.get("type", "rect")
            color = elem.get("color") or elem.get("stroke") or "#3b82f6"
            if etype == "footing": color = "#3b82f6"
            elif etype == "column": color = "#f59e0b"
            elif etype == "beam": color = "#eab308"
            elif etype == "slab": color = "#22c55e"
            elif etype == "chb_wall": color = "#06b6d4"

            x = elem.get("x", 50)
            y = elem.get("y", 50)
            w = elem.get("width", 60)
            h = elem.get("height", 60)

            dwg.add(dwg.rect(
                insert=(x, y),
                size=(w, h),
                fill=color,
                fill_opacity=0.2,
                stroke=color,
                stroke_width=elem.get("stroke_width", 1.5),
                rx=2
            ))

            lbl = elem.get("label") or elem.get("id") or etype.upper()
            dwg.add(dwg.text(
                lbl,
                insert=(x + 4, max(12, y - 5)),
                fill='#ffffff',
                font_size=9,
                font_weight='bold',
                font_family='JetBrains Mono, monospace'
            ))

        return dwg.tostring()

    def reconstruct_svg(self, output_svg_path, json_payload=None):

        """
        Re-builds and renders a complete CAD/SVG drawing strictly from the extracted JSON output.
        """
        if json_payload:
            self.__init__(json_payload)

        dwg = svgwrite.Drawing(output_svg_path, size=(self.width, self.height))
        dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'), fill='#0a0f1e'))

        # Render grid lines
        for gx in range(50, int(self.width), 100):
            dwg.add(dwg.line(start=(gx, 0), end=(gx, self.height), stroke='#1e293b', stroke_width=0.5))
        for gy in range(50, int(self.height), 100):
            dwg.add(dwg.line(start=(0, gy), end=(self.width, gy), stroke='#1e293b', stroke_width=0.5))

        for elem in self.elements:
            etype = elem.get("type", "rect")
            color = elem.get("color") or elem.get("stroke") or "#3b82f6"
            if etype == "footing": color = "#3b82f6"
            elif etype == "column": color = "#f59e0b"
            elif etype == "beam": color = "#eab308"
            elif etype == "slab": color = "#22c55e"
            elif etype == "chb_wall": color = "#06b6d4"

            x = elem.get("x", 50)
            y = elem.get("y", 50)
            w = elem.get("width", 60)
            h = elem.get("height", 60)

            # Draw structural box
            dwg.add(dwg.rect(
                insert=(x, y),
                size=(w, h),
                fill=color,
                fill_opacity=0.2,
                stroke=color,
                stroke_width=elem.get("stroke_width", 1.5),
                rx=2
            ))

            # Draw rebar lines if present
            rebars = elem.get("rebar", [])
            for r in rebars:
                rtype = r.get("type")
                rc = r.get("color", "#ef4444")
                cnt = r.get("count", 3)

                if rtype == "horizontal":
                    for i in range(cnt):
                        yp = y + (h * (i + 1)) / (cnt + 1)
                        dwg.add(dwg.line(start=(x + 2, yp), end=(x + w - 2, yp), stroke=rc, stroke_width=1, stroke_opacity=0.7))
                elif rtype == "vertical":
                    for i in range(cnt):
                        xp = x + (w * (i + 1)) / (cnt + 1)
                        dwg.add(dwg.line(start=(xp, y + 2), end=(xp, y + h - 2), stroke=rc, stroke_width=1, stroke_opacity=0.7))
                elif rtype == "dowel":
                    for i in range(cnt):
                        xp = x + (w * (i + 1)) / (cnt + 1)
                        dwg.add(dwg.line(start=(xp, y + 2), end=(xp, y + h - 2), stroke=rc, stroke_width=1.2, stroke_dasharray="3,3", stroke_opacity=0.6))
                elif rtype in ("dots", "main"):
                    for px, py in [[0.2, 0.2], [0.8, 0.2], [0.2, 0.8], [0.8, 0.8]]:
                        dwg.add(dwg.circle(center=(x + w * px, y + h * py), r=2.5, fill=rc))

            # Draw label text
            lbl = elem.get("label") or elem.get("id") or etype.upper()
            dwg.add(dwg.text(
                lbl,
                insert=(x + 4, max(12, y - 5)),
                fill='#ffffff',
                font_size=9,
                font_weight='bold',
                font_family='JetBrains Mono, monospace'
            ))

        dwg.save()
        return output_svg_path

    def reconstruct_png(self, output_png_path, json_payload=None):
        """
        Renders the reconstructed SVG or payload directly to a PNG image file.
        """
        if json_payload:
            self.__init__(json_payload)

        # 1. Try cairosvg if available
        if cairosvg:
            with tempfile.NamedTemporaryFile(suffix=".svg", delete=False, mode='w', encoding='utf-8') as temp_svg:
                temp_svg_path = temp_svg.name
            self.reconstruct_svg(temp_svg_path)
            try:
                cairosvg.svg2png(url=temp_svg_path, write_to=output_png_path)
                os.remove(temp_svg_path)
                return output_png_path
            except Exception:
                pass

        # 2. Native PIL rendering fallback
        img = Image.new("RGBA", (int(self.width), int(self.height)), (10, 15, 30, 255))
        draw = ImageDraw.Draw(img)

        # Draw grid
        for gx in range(50, int(self.width), 100):
            draw.line([(gx, 0), (gx, self.height)], fill=(30, 41, 59, 255), width=1)
        for gy in range(50, int(self.height), 100):
            draw.line([(0, gy), (self.width, gy)], fill=(30, 41, 59, 255), width=1)

        color_map = {
            "footing": (59, 130, 246), "column": (245, 158, 11),
            "beam": (234, 179, 8), "slab": (34, 197, 94), "chb_wall": (6, 182, 212)
        }

        for elem in self.elements:
            etype = elem.get("type", "rect")
            rgb = color_map.get(etype, (168, 85, 247))
            x, y = int(elem.get("x", 50)), int(elem.get("y", 50))
            w, h = int(elem.get("width", 60)), int(elem.get("height", 60))

            draw.rectangle([x, y, x + w, y + h], outline=rgb + (255,), fill=rgb + (50,), width=2)
            lbl = elem.get("label") or elem.get("id") or etype.upper()
            draw.text((x + 4, max(4, y - 14)), lbl, fill=(255, 255, 255, 255))

        img.save(output_png_path)
        return output_png_path


def generate_comparison(original_blueprint_path: str, recon_payload: dict, output_comparison_path: str) -> str:
    """
    Generates side-by-side comparison image:
      Panel 1: Original Ingested Blueprint
      Panel 2: Reconstructed Drawing Generated from Extracted JSON Output
    """
    engine = VisualReconstructionEngine(recon_payload)
    
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_png:
        reconstructed_png_path = temp_png.name

    engine.reconstruct_png(reconstructed_png_path)

    # 1. Load original blueprint image
    orig_img = None
    if fitz and os.path.exists(original_blueprint_path) and original_blueprint_path.lower().endswith(".pdf"):
        try:
            doc = fitz.open(original_blueprint_path)
            pix = doc[0].get_pixmap(dpi=120)
            orig_img = Image.open(tempfile.NamedTemporaryFile(suffix=".png", delete=False))
            pix.save(orig_img.filename)
            orig_img = Image.open(orig_img.filename).convert("RGBA")
            doc.close()
        except Exception:
            pass

    if orig_img is None:
        if os.path.exists(original_blueprint_path):
            try:
                orig_img = Image.open(original_blueprint_path).convert("RGBA")
            except Exception:
                pass

    if orig_img is None:
        orig_img = Image.new("RGBA", (int(engine.width), int(engine.height)), (15, 23, 42, 255))
        d = ImageDraw.Draw(orig_img)
        d.text((20, 20), f"Original: {os.path.basename(original_blueprint_path)}", fill=(255, 255, 255, 255))

    recon_img = Image.open(reconstructed_png_path).convert("RGBA")

    # Resize recon_img to match orig_img height
    h1 = orig_img.height
    w1 = orig_img.width
    scale_y = h1 / float(max(1, recon_img.height))
    w2 = int(recon_img.width * scale_y)
    h2 = h1
    recon_img_resized = recon_img.resize((w2, h2), Image.Resampling.LANCZOS)

    # Build side-by-side comparison canvas
    comp_width = w1 + w2 + 20
    comp_height = h1 + 40
    comp_img = Image.new("RGBA", (comp_width, comp_height), (2, 6, 23, 255))

    # Paste panels
    comp_img.paste(orig_img, (0, 40))
    comp_img.paste(recon_img_resized, (w1 + 20, 40))

    # Header title bar
    draw = ImageDraw.Draw(comp_img)
    draw.rectangle([0, 0, comp_width, 36], fill=(15, 23, 42, 255))
    draw.text((20, 10), "1. ORIGINAL INGESTED BLUEPRINT", fill=(248, 250, 252, 255))
    draw.text((w1 + 40, 10), "2. RECONSTRUCTED DRAWING (FROM EXTRACTED JSON)", fill=(56, 189, 248, 255))

    os.makedirs(os.path.dirname(output_comparison_path), exist_ok=True)
    comp_img.save(output_comparison_path)

    try:
        os.remove(reconstructed_png_path)
    except Exception:
        pass

    return output_comparison_path
