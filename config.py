"""
Configuration module for RAFAI Technologies Certificate Generator.
Contains global settings, path definitions, and certificate design specifications.
"""

from pathlib import Path
from dataclasses import dataclass, field
from typing import Tuple

# Base Directories
BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
FONTS_DIR = ASSETS_DIR / "fonts"
DEFAULT_OUTPUT_DIR = BASE_DIR / "output"
SAMPLE_DATA_DIR = BASE_DIR / "sample_data"

# Create directories if they do not exist
ASSETS_DIR.mkdir(parents=True, exist_ok=True)
FONTS_DIR.mkdir(parents=True, exist_ok=True)
DEFAULT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
SAMPLE_DATA_DIR.mkdir(parents=True, exist_ok=True)

# Default Asset Paths
DEFAULT_LOGO_PATH = ASSETS_DIR / "rafai_logo.png"
DEFAULT_SIGNATURE_PATH = ASSETS_DIR / "instructor_signature.png"
DEFAULT_SEAL_PATH = ASSETS_DIR / "official_seal.png"
DEFAULT_TEMPLATE_PATH = ASSETS_DIR / "certificate_template.png"

# Application Metadata
APP_TITLE = "RAFAI Technologies - AI Foundation Certificate Generator"
APP_SUBTITLE = "Enterprise-Grade Dynamic Bulk Certificate Generation System"
APP_ICON = "🎓"
COMPANY_NAME_DEFAULT = "RAFAI TECHNOLOGIES"
COURSE_NAME_DEFAULT = "AI Foundation-Artificial Intelligence | Machine Learning Basics | Generative AI | Prompt Engineering | ChatGPT & Gemini | AI Project Implementation"
INSTRUCTOR_NAME_DEFAULT = "Mahesh Kodchawadkar"
INSTRUCTOR_TITLE_DEFAULT = "Lead AI Instructor"
PREFIX_DEFAULT = "RAFAI-AI-2026"
START_NUMBER_DEFAULT = 1
DATE_FORMAT_DEFAULT = "%d-%b-%Y"

# Certificate Canvas Specifications (A4 Landscape at 300 DPI high resolution)
CANVAS_WIDTH = 2000
CANVAS_HEIGHT = 1414
ASPECT_RATIO = CANVAS_WIDTH / CANVAS_HEIGHT

# Palette Specifications (Refined Navy & Royal Gold aesthetic)
COLOR_NAVY_DEEP = "#071329"
COLOR_NAVY_PRIMARY = "#0F2854"
COLOR_NAVY_ACCENT = "#1B4380"
COLOR_GOLD_DARK = "#9A7B38"
COLOR_GOLD_PRIMARY = "#C5A059"
COLOR_GOLD_LIGHT = "#E9D29B"
COLOR_GOLD_CREAM = "#FAF6EE"
COLOR_WHITE = "#FFFFFF"
COLOR_TEXT_PRIMARY = "#0F172A"
COLOR_TEXT_SECONDARY = "#475569"
COLOR_TEXT_MUTED = "#64748B"
COLOR_BORDER_FRAME = "#C5A059"

# Required and Supported Data Columns
COLUMN_STUDENT_NAME = "Student Name"
COLUMN_COLLEGE = "College"
COLUMN_COURSE = "Course"
COLUMN_COMPLETION_DATE = "Completion Date"
COLUMN_EMAIL = "Email"
COLUMN_CERTIFICATE_ID = "Certificate ID"

EXPECTED_COLUMNS = [
    COLUMN_STUDENT_NAME,
    COLUMN_COLLEGE,
    COLUMN_COURSE,
    COLUMN_COMPLETION_DATE,
    COLUMN_EMAIL,
]


@dataclass
class CertificateConfig:
    """Configuration class for certificate generation batch."""
    company_name: str = COMPANY_NAME_DEFAULT
    course_name: str = COURSE_NAME_DEFAULT
    instructor_name: str = INSTRUCTOR_NAME_DEFAULT
    instructor_title: str = INSTRUCTOR_TITLE_DEFAULT
    completion_date_str: str = "08-Oct-2026"
    prefix: str = PREFIX_DEFAULT
    start_number: int = START_NUMBER_DEFAULT
    logo_path: Path = DEFAULT_LOGO_PATH
    signature_path: Path = DEFAULT_SIGNATURE_PATH
    seal_path: Path = DEFAULT_SEAL_PATH
    template_path: Path = DEFAULT_TEMPLATE_PATH
    output_dir: Path = DEFAULT_OUTPUT_DIR
    generate_png: bool = True
    generate_pdf: bool = True
