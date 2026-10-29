"""
Asset generation utility for RAFAI Technologies Certificate Generator.
Programmatically creates high-resolution, professional default assets if custom
images (logo, signature, seal, template) are not provided by the user.
"""

from pathlib import Path
import math
from PIL import Image, ImageDraw, ImageFont
import config


def _get_font(font_name: str, size: int) -> ImageFont.ImageFont:
    """
    Safely load a TrueType font or fallback to system default.
    Tries common Windows/Linux fonts before falling back.
    """
    font_candidates = [
        font_name,
        "georgia.ttf",
        "arial.ttf",
        "calibri.ttf",
        "times.ttf",
        "segoeui.ttf",
        "C:\\Windows\\Fonts\\georgia.ttf",
        "C:\\Windows\\Fonts\\arial.ttf",
        "C:\\Windows\\Fonts\\calibri.ttf",
    ]
    for candidate in font_candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except Exception:
            continue
    return ImageFont.load_default()


def create_default_logo(output_path: Path) -> Path:
    """
    Generates an enterprise-grade corporate logo for RAFAI TECHNOLOGIES.
    Returns the path to the saved PNG.
    """
    width, height = 700, 200
    img = Image.new("RGBA", (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    # 1. Draw Geometric Emblem (Diamond / Hexagon with stylized 'R' & Neural Nodes)
    cx, cy = 90, 100
    size = 55

    # Outer hexagon in Deep Navy
    hex_points = [
        (cx + size * math.cos(math.radians(a)), cy + size * math.sin(math.radians(a)))
        for a in range(30, 390, 60)
    ]
    draw.polygon(hex_points, fill="#0F2854", outline="#C5A059", width=3)

    # Inner Gold Diamond
    inner_size = 35
    diamond_points = [
        (cx, cy - inner_size),
        (cx + inner_size, cy),
        (cx, cy + inner_size),
        (cx - inner_size, cy),
    ]
    draw.polygon(diamond_points, fill="#FAF6EE", outline="#C5A059", width=2)

    # Stylized 'R' inside emblem
    font_r = _get_font("georgia.ttf", 46)
    draw.text((cx, cy - 2), "R", fill="#0F2854", font=font_r, anchor="mm")

    # Corner AI Nodes (Small gold circles)
    for px, py in hex_points[::2]:
        draw.ellipse([px - 4, py - 4, px + 4, py + 4], fill="#C5A059", outline="#FFFFFF")

    # 2. Brand Name Typography
    font_title = _get_font("georgia.ttf", 48)
    font_sub = _get_font("arial.ttf", 20)

    # "RAFAI" in Deep Navy with letter spacing
    draw.text((180, 75), "RAFAI", fill="#0F2854", font=font_title, anchor="lm")

    # Thin Gold Accent Bar
    draw.line([(180, 105), (550, 105)], fill="#C5A059", width=2)

    # "TECHNOLOGIES" in elegant gold-dark typography
    draw.text((182, 126), "TECHNOLOGIES", fill="#9A7B38", font=font_sub, anchor="lm")
    draw.text((375, 126), "•  AI EXCELLENCE", fill="#64748B", font=font_sub, anchor="lm")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, "PNG")
    return output_path


def create_default_signature(output_path: Path) -> Path:
    """
    Generates an authentic, fluid cursive signature graphic for Vinod Patil/Mahesh Kodchawadkar.
    """
    width, height = 500, 160
    img = Image.new("RGBA", (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    # Smooth curve coordinates simulating a real pen stroke
    strokes = [
        # Capital 'M' & 'R' flourish
        [(50, 110), (70, 45), (95, 120), (120, 50), (145, 105)],
        # Cursive Rafai loop
        [(145, 105), (170, 70), (190, 100), (220, 65), (250, 95), (280, 70), (320, 100)],
        # Elegant sweeping flourish underline
        [(60, 130), (150, 125), (260, 135), (380, 115), (420, 95)],
        # Pen dots & accent
        [(340, 55), (342, 57)],
    ]

    stroke_color = "#0B2246"
    for stroke in strokes:
        if len(stroke) == 2 and stroke[0] == stroke[1]:
            draw.ellipse([stroke[0][0] - 2, stroke[0][1] - 2, stroke[0][0] + 2, stroke[0][1] + 2], fill=stroke_color)
        else:
            # Draw line segments with rounded joins
            for i in range(len(stroke) - 1):
                draw.line([stroke[i], stroke[i + 1]], fill=stroke_color, width=3)
                draw.ellipse([stroke[i][0] - 1.5, stroke[i][1] - 1.5, stroke[i][0] + 1.5, stroke[i][1] + 1.5], fill=stroke_color)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, "PNG")
    return output_path


def create_default_seal(output_path: Path) -> Path:
    """
    Generates a luxury gold embossed verification seal badge.
    """
    size = 400
    img = Image.new("RGBA", (size, size), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    cx, cy = size // 2, size // 2

    # Outer sunburst serrations
    num_teeth = 48
    outer_r = 185
    inner_r = 168
    teeth_points = []
    for i in range(num_teeth * 2):
        angle = math.pi * i / num_teeth
        r = outer_r if (i % 2 == 0) else inner_r
        teeth_points.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    draw.polygon(teeth_points, fill="#C5A059")

    # Main Circular Medallion in Rich Royal Gold
    draw.ellipse([cx - 165, cy - 165, cx + 165, cy + 165], fill="#DFB76C", outline="#8B6C24", width=3)

    # Inset White/Cream Ring
    draw.ellipse([cx - 150, cy - 150, cx + 150, cy + 150], outline="#9A7B38", width=2)
    draw.ellipse([cx - 110, cy - 110, cx + 110, cy + 110], fill="#0F2854", outline="#C5A059", width=3)

    # Draw 3 crisp vector gold stars in the upper emblem
    def _draw_star(scx, scy, r_outer, r_inner, fill):
        pts = []
        for i in range(10):
            ang = math.pi * i / 5 - math.pi / 2
            r = r_outer if i % 2 == 0 else r_inner
            pts.append((scx + r * math.cos(ang), scy + r * math.sin(ang)))
        draw.polygon(pts, fill=fill)

    _draw_star(cx - 40, cy - 35, 12, 5, "#E9D29B")
    _draw_star(cx, cy - 42, 16, 7, "#FFFFFF")
    _draw_star(cx + 40, cy - 35, 12, 5, "#E9D29B")

    font_text = _get_font("arial.ttf", 16)
    font_bold = _get_font("georgia.ttf", 20)

    draw.text((cx, cy + 2), "VERIFIED", fill="#FFFFFF", font=font_bold, anchor="mm")
    draw.text((cx, cy + 28), "EXCELLENCE", fill="#E9D29B", font=font_text, anchor="mm")
    draw.text((cx, cy + 50), "• 2026 •", fill="#E9D29B", font=font_text, anchor="mm")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, "PNG")
    return output_path


def create_default_template(output_path: Path, width: int = 2000, height: int = 1414) -> Path:
    """
    Generates a stunning, executive certificate background template.
    Features:
    - Cream / parchment textured base (#FCFAF7)
    - Double gold & deep navy perimeter borders
    - Ornate geometric gold corner brackets
    - Subtle watermark radial design
    - Header & footer decorative dividers
    """
    img = Image.new("RGBA", (width, height), (252, 250, 247, 255))
    draw = ImageDraw.Draw(img)

    # 1. Subtle Radial Background Glow / Guilloché Lines
    cx, cy = width // 2, height // 2
    for r in range(250, 850, 50):
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(238, 230, 215, 60), width=1)

    # 2. Main Outer Deep Navy Border (Inset 35px)
    navy_inset = 35
    draw.rectangle(
        [(navy_inset, navy_inset), (width - navy_inset, height - navy_inset)],
        outline="#0F2854",
        width=8
    )

    # 3. Outer Gold Pinstripe (Inset 50px)
    draw.rectangle(
        [(50, 50), (width - 50, height - 50)],
        outline="#C5A059",
        width=2
    )

    # 4. Inner Gold Frame (Inset 65px)
    draw.rectangle(
        [(65, 65), (width - 65, height - 65)],
        outline="#C5A059",
        width=4
    )

    # 5. Inner Pinstripe (Inset 75px)
    draw.rectangle(
        [(75, 75), (width - 75, height - 75)],
        outline="#E9D29B",
        width=1
    )

    # 6. Ornate Gold Corner Brackets
    corners = [
        (65, 65, 1, 1),           # Top-left
        (width - 65, 65, -1, 1),   # Top-right
        (65, height - 65, 1, -1),  # Bottom-left
        (width - 65, height - 65, -1, -1), # Bottom-right
    ]
    bracket_len = 80
    for x, y, dx, dy in corners:
        # Triangular corner fill
        draw.polygon([(x, y), (x + dx * bracket_len, y), (x, y + dy * bracket_len)], fill="#C5A059")
        # Inset corner line
        draw.polygon(
            [(x + dx * 8, y + dy * 8), (x + dx * (bracket_len - 15), y + dy * 8), (x + dx * 8, y + dy * (bracket_len - 15))],
            fill="#FAF6EE"
        )
        # Inner corner square accent
        x_pt1, y_pt1 = x + dx * 20, y + dy * 20
        x_pt2, y_pt2 = x + dx * 35, y + dy * 35
        draw.rectangle(
            [(min(x_pt1, x_pt2), min(y_pt1, y_pt2)), (max(x_pt1, x_pt2), max(y_pt1, y_pt2))],
            fill="#0F2854",
            outline="#C5A059",
            width=2
        )

    # 7. Subtle Accent Bars (moved away from center logo)
    draw.line([(180, 180), (380, 180)], fill="#C5A059", width=2)
    draw.line([(width - 380, 180), (width - 180, 180)], fill="#C5A059", width=2)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, "PNG")
    return output_path


def ensure_default_assets():
    """
    Checks and generates all default assets if they do not exist.
    """
    if not config.DEFAULT_LOGO_PATH.exists():
        create_default_logo(config.DEFAULT_LOGO_PATH)
    if not config.DEFAULT_SIGNATURE_PATH.exists():
        create_default_signature(config.DEFAULT_SIGNATURE_PATH)
    if not config.DEFAULT_SEAL_PATH.exists():
        create_default_seal(config.DEFAULT_SEAL_PATH)
    if not config.DEFAULT_TEMPLATE_PATH.exists():
        create_default_template(config.DEFAULT_TEMPLATE_PATH)


if __name__ == "__main__":
    ensure_default_assets()
    print("Default assets created successfully in", config.ASSETS_DIR)
