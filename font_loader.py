"""
Cross-Platform Font Loading Engine for RAFAI Technologies Certificate Generator.
Ensures identical, high-fidelity font rendering across Windows, macOS, Linux,
Docker, and Streamlit Cloud environments.

Eliminates the "tiny text / font shrinking" issue on Streamlit Cloud by:
1. Prioritizing bundled open-source luxury fonts in assets/fonts/
2. Searching standard Linux, macOS, and Windows system font directories
3. Mapping requested fonts to cross-platform open-source equivalents
4. Utilizing ReportLab's bundled TrueType fonts as guaranteed universal fallback
5. Safely sizing PIL's load_default() if no TrueType file is accessible
"""

import os
from pathlib import Path
from typing import List, Union, Tuple, Optional
from functools import lru_cache
from PIL import ImageFont
import reportlab

import config

# Search directories across operating systems
FONT_SEARCH_DIRS = [
    config.FONTS_DIR,
    config.ASSETS_DIR,
    Path(__file__).resolve().parent / "assets" / "fonts",
    Path("assets/fonts"),
    # Linux / Streamlit Cloud / Debian paths
    Path("/usr/share/fonts/truetype"),
    Path("/usr/share/fonts/truetype/dejavu"),
    Path("/usr/share/fonts/truetype/liberation"),
    Path("/usr/share/fonts/truetype/freefont"),
    Path("/usr/share/fonts"),
    Path("/usr/local/share/fonts"),
    Path.home() / ".fonts",
    Path.home() / ".local/share/fonts",
    # Windows system font paths
    Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts",
    Path("C:/Windows/Fonts"),
    # macOS system font paths
    Path("/Library/Fonts"),
    Path("/System/Library/Fonts"),
    Path.home() / "Library/Fonts",
    # ReportLab bundled fonts (always present in any environment with reportlab)
    Path(reportlab.__file__).parent / "fonts",
]

# Aliases for cross-platform matching
FONT_ALIASES = {
    # Bold Serif
    "georgiab.ttf": ["PlayfairDisplay.ttf", "DejaVuSerif-Bold.ttf", "LiberationSerif-Bold.ttf", "timesbd.ttf", "FreeSerifBold.ttf", "VeraBd.ttf"],
    "timesbd.ttf": ["PlayfairDisplay.ttf", "DejaVuSerif-Bold.ttf", "LiberationSerif-Bold.ttf", "georgiab.ttf", "FreeSerifBold.ttf", "VeraBd.ttf"],
    # Regular Serif
    "georgia.ttf": ["PlayfairDisplay.ttf", "DejaVuSerif.ttf", "LiberationSerif-Regular.ttf", "times.ttf", "FreeSerif.ttf", "Vera.ttf"],
    "times.ttf": ["PlayfairDisplay.ttf", "DejaVuSerif.ttf", "LiberationSerif-Regular.ttf", "georgia.ttf", "FreeSerif.ttf", "Vera.ttf"],
    # Italic Serif
    "georgiai.ttf": ["PlayfairDisplay-Italic.ttf", "DejaVuSerif-Italic.ttf", "LiberationSerif-Italic.ttf", "timesi.ttf", "FreeSerifItalic.ttf", "VeraIt.ttf"],
    "timesi.ttf": ["PlayfairDisplay-Italic.ttf", "DejaVuSerif-Italic.ttf", "LiberationSerif-Italic.ttf", "georgiai.ttf", "FreeSerifItalic.ttf", "VeraIt.ttf"],
    # Regular Sans
    "arial.ttf": ["PlusJakartaSans.ttf", "DejaVuSans.ttf", "LiberationSans-Regular.ttf", "segoeui.ttf", "calibri.ttf", "FreeSans.ttf", "Vera.ttf"],
    "segoeui.ttf": ["PlusJakartaSans.ttf", "DejaVuSans.ttf", "LiberationSans-Regular.ttf", "arial.ttf", "calibri.ttf", "FreeSans.ttf", "Vera.ttf"],
    "calibri.ttf": ["PlusJakartaSans.ttf", "DejaVuSans.ttf", "LiberationSans-Regular.ttf", "arial.ttf", "segoeui.ttf", "FreeSans.ttf", "Vera.ttf"],
    # Bold Sans
    "arialbd.ttf": ["PlusJakartaSans.ttf", "DejaVuSans-Bold.ttf", "LiberationSans-Bold.ttf", "segoeuib.ttf", "calibrib.ttf", "FreeSansBold.ttf", "VeraBd.ttf"],
    "segoeuib.ttf": ["PlusJakartaSans.ttf", "DejaVuSans-Bold.ttf", "LiberationSans-Bold.ttf", "arialbd.ttf", "calibrib.ttf", "FreeSansBold.ttf", "VeraBd.ttf"],
    # Italic Sans
    "ariali.ttf": ["PlusJakartaSans-Italic.ttf", "DejaVuSans-Oblique.ttf", "LiberationSans-Italic.ttf", "calibrii.ttf", "VeraIt.ttf"],
}


def _resolve_candidates(font_names: Union[str, List[str]]) -> List[str]:
    """Expands requested font names with cross-platform equivalents and aliases."""
    if isinstance(font_names, str):
        requested = [font_names]
    else:
        requested = list(font_names)

    candidates: List[str] = []
    for name in requested:
        # Normalize name
        clean_name = Path(name).name.lower()
        if name not in candidates:
            candidates.append(name)
        # Check aliases
        if clean_name in FONT_ALIASES:
            for alias in FONT_ALIASES[clean_name]:
                if alias not in candidates:
                    candidates.append(alias)

    # Universal fallbacks
    for fallback in ["PlayfairDisplay.ttf", "PlusJakartaSans.ttf", "DejaVuSerif.ttf", "DejaVuSans.ttf", "Vera.ttf"]:
        if fallback not in candidates:
            candidates.append(fallback)

    return candidates


@lru_cache(maxsize=256)
def _load_font_cached(font_path_str: str, size: int) -> ImageFont.ImageFont:
    """Loads and caches TrueType font from an absolute or resolvable path."""
    return ImageFont.truetype(font_path_str, size)


def get_font(font_names: Union[str, List[str]], size: int) -> ImageFont.ImageFont:
    """
    Finds and loads the best matching font at the requested size.

    Searches:
    1. Direct paths / local files
    2. Assets fonts directory (assets/fonts/)
    3. OS system fonts (Linux / Windows / macOS)
    4. ReportLab bundled TrueType fonts
    5. PIL scaled default font (guaranteeing correct size even without TrueType)

    Args:
        font_names: A single font filename or a list of font names in preference order.
        size: Desired font size in points/pixels.

    Returns:
        ImageFont.ImageFont: An appropriately sized font instance.
    """
    candidates = _resolve_candidates(font_names)

    for cand in candidates:
        # 1. Direct path / filename
        cand_path = Path(cand)
        if cand_path.is_file():
            try:
                return _load_font_cached(str(cand_path.resolve()), size)
            except Exception:
                pass

        # 2. Search in registered font directories
        for search_dir in FONT_SEARCH_DIRS:
            if not search_dir.exists():
                continue
            full_path = search_dir / cand
            if full_path.is_file():
                try:
                    return _load_font_cached(str(full_path.resolve()), size)
                except Exception:
                    pass

        # 3. Direct PIL lookup (checks system fonts on some OS configurations)
        try:
            return _load_font_cached(cand, size)
        except Exception:
            pass

    # 4. Universal ReportLab font fallback (Bitstream Vera is guaranteed in pip environment)
    try:
        rl_dir = Path(reportlab.__file__).parent / "fonts"
        for rl_cand in ["VeraBd.ttf", "Vera.ttf", "VeraIt.ttf"]:
            rl_file = rl_dir / rl_cand
            if rl_file.is_file():
                return _load_font_cached(str(rl_file.resolve()), size)
    except Exception:
        pass

    # 5. Guaranteed scaled fallback (Pillow 10.1+ supports size argument)
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()

