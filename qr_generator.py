"""
QR Code Generator for RAFAI Technologies Certificates.
Generates high-resolution, branded verification QR codes containing verified certificate details.
"""

from typing import Optional
from io import BytesIO
from pathlib import Path
import qrcode
from qrcode.constants import ERROR_CORRECT_M, ERROR_CORRECT_H
from PIL import Image, ImageDraw


def generate_qr_payload(
    certificate_id: str,
    student_name: str,
    course_name: str,
    completion_date: str,
    company_name: str,
    verification_url: Optional[str] = None
) -> str:
    """
    Format structured certificate verification payload for the QR code.
    Contains clean, human and machine-readable verification data.
    """
    url_line = f"\nVerification URL: {verification_url}" if verification_url else ""
    payload = (
        f"CERTIFICATE VERIFICATION\n"
        f"Certificate ID: {certificate_id.strip()}\n"
        f"Recipient: {student_name.strip()}\n"
        f"Course: {course_name.strip()}\n"
        f"Completion Date: {completion_date.strip()}\n"
        f"Issuing Authority: {company_name.strip()}\n"
        f"Status: VALID & VERIFIED{url_line}"
    )
    return payload


def generate_qr_image(
    certificate_id: str,
    student_name: str,
    course_name: str,
    completion_date: str,
    company_name: str,
    size: int = 240,
    fill_color: str = "#0F2854",
    back_color: str = "#FFFFFF",
    output_path: Optional[Path] = None,
    add_frame: bool = True
) -> Image.Image:
    """
    Generates a high-quality QR code image with error correction and optional styling.

    Args:
        certificate_id: Unique certificate identifier.
        student_name: Name of the recipient.
        course_name: Name of the completed course.
        completion_date: Date string of completion.
        company_name: Organization name.
        size: Target pixel width and height.
        fill_color: Hex color for the QR code modules.
        back_color: Hex color for the background.
        output_path: Optional path to save the generated image.
        add_frame: Whether to add a subtle elegant border.

    Returns:
        PIL.Image.Image: The generated QR code image in RGBA.
    """
    payload = generate_qr_payload(
        certificate_id=certificate_id,
        student_name=student_name,
        course_name=course_name,
        completion_date=completion_date,
        company_name=company_name,
    )

    qr = qrcode.QRCode(
        version=None,
        error_correction=ERROR_CORRECT_M,
        box_size=10,
        border=2,
    )
    qr.add_data(payload)
    qr.make(fit=True)

    # Render base image
    qr_img = qr.make_image(fill_color=fill_color, back_color=back_color).convert("RGBA")

    # Resize to exact requested dimension with high-quality resampling
    if qr_img.size != (size, size):
        qr_img = qr_img.resize((size, size), Image.Resampling.LANCZOS)

    if add_frame:
        # Create subtle outer boundary with light gold border for a luxury certificate feel
        bordered = Image.new("RGBA", (size + 12, size + 12), (255, 255, 255, 255))
        draw = ImageDraw.Draw(bordered)
        draw.rectangle(
            [(0, 0), (size + 11, size + 11)],
            outline="#C5A059",
            width=2
        )
        bordered.paste(qr_img, (6, 6), qr_img)
        qr_img = bordered

    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        qr_img.save(output_path, format="PNG")

    return qr_img


def generate_qr_bytes(
    certificate_id: str,
    student_name: str,
    course_name: str,
    completion_date: str,
    company_name: str,
    size: int = 240,
) -> bytes:
    """Generate QR code and return PNG bytes directly."""
    img = generate_qr_image(
        certificate_id=certificate_id,
        student_name=student_name,
        course_name=course_name,
        completion_date=completion_date,
        company_name=company_name,
        size=size
    )
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()
