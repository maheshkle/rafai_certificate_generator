"""
Certificate Generation Engine for RAFAI Technologies.
Produces high-resolution PNG (300 DPI) and print-ready PDF certificates.
Features dynamic text scaling, luxury typography, QR verification integration,
fault-tolerant batch processing, and ZIP package creation.
"""

from typing import List, Dict, Optional, Tuple, Callable
from pathlib import Path
from dataclasses import dataclass, field
import zipfile
import io
import time
import math
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import landscape, A4
from reportlab.pdfgen import canvas

import config
from excel_handler import StudentRecord
from qr_generator import generate_qr_image
import asset_generator


@dataclass
class BatchGenerationResult:
    """Summary of batch generation operation."""
    total_requested: int = 0
    generated_count: int = 0
    failed_count: int = 0
    elapsed_seconds: float = 0.0
    generated_files: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[Dict[str, Any]] = field(default_factory=list)
    zip_path: Optional[Path] = None
    zip_size_bytes: int = 0


class CertificateGenerator:
    """
    Main generator class responsible for rendering certificates.
    Caches visual assets and fonts for fast batch processing.
    """

    def __init__(self, cert_config: Optional[config.CertificateConfig] = None):
        self.config = cert_config or config.CertificateConfig()
        asset_generator.ensure_default_assets()
        self._load_assets()
        self._load_fonts()

    def _get_font(self, font_names: List[str], size: int) -> ImageFont.ImageFont:
        """Helper to find the first available TrueType font or fallback."""
        windows_font_dir = Path("C:/Windows/Fonts")
        for name in font_names:
            # Check local file or system font
            candidates = [name, windows_font_dir / name, str(windows_font_dir / name)]
            for cand in candidates:
                try:
                    return ImageFont.truetype(str(cand), size)
                except Exception:
                    continue
        return ImageFont.load_default()

    def _load_fonts(self):
        """Loads and caches typography hierarchy."""
        # Serif Header & Student Name fonts
        self.font_header_sub = self._get_font(["georgia.ttf", "times.ttf", "arial.ttf"], 22)
        self.font_title = self._get_font(["georgiab.ttf", "georgia.ttf", "timesbd.ttf", "arialbd.ttf"], 56)
        self.font_present = self._get_font(["segoeui.ttf", "arial.ttf", "calibri.ttf"], 24)
        self.font_student_base = lambda sz: self._get_font(["georgiab.ttf", "georgia.ttf", "timesbd.ttf"], sz)
        self.font_course = self._get_font(["georgiab.ttf", "georgia.ttf", "arialbd.ttf"], 44)
        self.font_course_split_title = self._get_font(["georgiab.ttf", "georgia.ttf", "arialbd.ttf"], 40)
        self.font_course_details_base = lambda sz: self._get_font(["georgiai.ttf", "ariali.ttf", "segoeui.ttf", "calibri.ttf"], sz)
        self.font_course_sub = self._get_font(["ariali.ttf", "georgiai.ttf", "arial.ttf"], 22)
        self.font_college = self._get_font(["georgiab.ttf", "georgia.ttf", "arialbd.ttf"], 26)
        self.font_label = self._get_font(["segoeuib.ttf", "arialbd.ttf", "calibri.ttf"], 17)
        self.font_value = self._get_font(["georgiab.ttf", "georgia.ttf", "arialbd.ttf"], 21)
        self.font_meta = self._get_font(["arial.ttf", "calibri.ttf"], 16)
        self.font_footer = self._get_font(["arial.ttf", "calibri.ttf"], 13)

    def _load_assets(self):
        """Loads and pre-processes background template, logo, signature, and seal."""
        template_p = self.config.template_path if self.config.template_path.exists() else config.DEFAULT_TEMPLATE_PATH
        if not template_p.exists():
            asset_generator.create_default_template(template_p)
        self.template_img = Image.open(template_p).convert("RGBA")
        if self.template_img.size != (config.CANVAS_WIDTH, config.CANVAS_HEIGHT):
            self.template_img = self.template_img.resize(
                (config.CANVAS_WIDTH, config.CANVAS_HEIGHT), Image.Resampling.LANCZOS
            )

        logo_p = self.config.logo_path if self.config.logo_path.exists() else config.DEFAULT_LOGO_PATH
        if not logo_p.exists():
            asset_generator.create_default_logo(logo_p)
        self.logo_img = Image.open(logo_p).convert("RGBA")

        sig_p = self.config.signature_path if self.config.signature_path.exists() else config.DEFAULT_SIGNATURE_PATH
        if not sig_p.exists():
            asset_generator.create_default_signature(sig_p)
        self.signature_img = Image.open(sig_p).convert("RGBA")

        seal_p = self.config.seal_path if self.config.seal_path.exists() else config.DEFAULT_SEAL_PATH
        if not seal_p.exists():
            asset_generator.create_default_seal(seal_p)
        self.seal_img = Image.open(seal_p).convert("RGBA")

    def reload_assets(self):
        """Allows hot-reloading when user uploads a custom logo, signature, or template."""
        self._load_assets()
        self._load_fonts()

    def render_certificate_image(self, student: StudentRecord) -> Image.Image:
        """
        Renders a complete, high-resolution certificate for a given student record.

        Contains all required fields:
        - RAFAI TECHNOLOGIES
        - CERTIFICATE OF COMPLETION
        - This certificate is proudly presented to
        - [STUDENT NAME]
        - for successfully completing
        - [COURSE NAME]
        - College: [COLLEGE NAME]
        - Completion Date: [DATE]
        - Certificate ID: [CERTIFICATE ID]
        - Instructor: [INSTRUCTOR NAME]
        - Company logo
        - Instructor signature
        - Decorative border
        - Professional typography
        - QR code (bottom-right)
        - Official Seal

        Returns:
            PIL.Image.Image: The rendered 2000x1414 certificate.
        """
        # Start with a copy of the high-res template
        cert = self.template_img.copy()
        draw = ImageDraw.Draw(cert)
        width, height = cert.size
        cx = width // 2

        # 1. Overlay Company Logo (Top Center, Y ~ 100-210)
        max_logo_w, max_logo_h = 420, 115
        logo_w, logo_h = self.logo_img.size
        ratio = min(max_logo_w / logo_w, max_logo_h / logo_h)
        new_logo_w, new_logo_h = int(logo_w * ratio), int(logo_h * ratio)
        resized_logo = self.logo_img.resize((new_logo_w, new_logo_h), Image.Resampling.LANCZOS)
        logo_x = cx - new_logo_w // 2
        logo_y = 105
        cert.paste(resized_logo, (logo_x, logo_y), resized_logo)

        # Sub-header division badge
        draw.text(
            (cx, 235),
            f"{self.config.company_name.upper()}  •  ARTIFICIAL INTELLIGENCE DIVISION",
            fill=config.COLOR_NAVY_PRIMARY,
            font=self.font_header_sub,
            anchor="mm"
        )

        # Thin gold divider with center diamond
        draw.line([(cx - 260, 260), (cx + 260, 260)], fill=config.COLOR_GOLD_PRIMARY, width=2)
        draw.polygon([(cx, 255), (cx + 6, 260), (cx, 265), (cx - 6, 260)], fill=config.COLOR_NAVY_PRIMARY)

        # 2. Main Title: CERTIFICATE OF COMPLETION
        draw.text(
            (cx, 320),
            "CERTIFICATE OF COMPLETION",
            fill=config.COLOR_NAVY_DEEP,
            font=self.font_title,
            anchor="mm"
        )
        # Decorative underline bar
        draw.line([(cx - 320, 355), (cx + 320, 355)], fill=config.COLOR_GOLD_PRIMARY, width=3)
        draw.line([(cx - 180, 361), (cx + 180, 361)], fill=config.COLOR_GOLD_LIGHT, width=1)

        # 3. Presentation line
        draw.text(
            (cx, 420),
            "THIS CERTIFICATE IS PROUDLY PRESENTED TO",
            fill=config.COLOR_TEXT_SECONDARY,
            font=self.font_present,
            anchor="mm"
        )

        # 4. Student Name (Dynamic auto-scaling font size for long names, reduced for elegant proportion)
        raw_name = student.student_name.strip()
        target_name_font_size = 58
        if len(raw_name) > 28:
            target_name_font_size = 44
        elif len(raw_name) > 22:
            target_name_font_size = 50

        font_student = self.font_student_base(target_name_font_size)
        draw.text(
            (cx, 515),
            raw_name,
            fill=config.COLOR_NAVY_PRIMARY,
            font=font_student,
            anchor="mm"
        )

        # Elegant gold underline accent below student name
        name_bbox = draw.textbbox((cx, 515), raw_name, font=font_student, anchor="mm")
        name_width = name_bbox[2] - name_bbox[0]
        line_half = max(int(name_width // 2) + 35, 170)
        draw.line([(cx - line_half, 558), (cx + line_half, 558)], fill=config.COLOR_GOLD_PRIMARY, width=2)
        draw.ellipse([cx - 4, 554, cx + 4, 562], fill=config.COLOR_NAVY_PRIMARY, outline=config.COLOR_GOLD_PRIMARY)

        # 5. Course Completion Statement
        draw.text(
            (cx, 625),
            "for successfully completing the industry-accredited program in",
            fill=config.COLOR_TEXT_SECONDARY,
            font=self.font_course_sub,
            anchor="mm"
        )

        # Course Name (Splits by '-' if present: first part in main line, second part in smaller font below)
        raw_course = student.course.strip()
        if "-" in raw_course:
            parts = raw_course.split("-", 1)
            course_main = parts[0].strip().upper()
            course_details = parts[1].strip()

            # First split: main title
            draw.text(
                (cx, 672),
                course_main,
                fill=config.COLOR_NAVY_DEEP,
                font=self.font_course_split_title,
                anchor="mm"
            )

            # Second split: course topics / subtitle with small font size
            detail_font_size = 20
            font_course_details = self.font_course_details_base(detail_font_size)
            detail_bbox = draw.textbbox((cx, 715), course_details, font=font_course_details, anchor="mm")
            detail_width = detail_bbox[2] - detail_bbox[0]
            if detail_width > 1650:
                detail_font_size = max(14, int(detail_font_size * 1650 / detail_width))
                font_course_details = self.font_course_details_base(detail_font_size)

            draw.text(
                (cx, 715),
                course_details,
                fill=config.COLOR_NAVY_PRIMARY,
                font=font_course_details,
                anchor="mm"
            )
            college_y = 772
        else:
            # Single-line Course Name
            draw.text(
                (cx, 695),
                raw_course.upper(),
                fill=config.COLOR_NAVY_DEEP,
                font=self.font_course,
                anchor="mm"
            )
            college_y = 770

        # 6. College Name
        college_display = f"College :  {student.college.strip()}"
        draw.text(
            (cx, college_y),
            college_display,
            fill=config.COLOR_TEXT_PRIMARY,
            font=self.font_college,
            anchor="mm"
        )

        # Center separator line
        draw.line([(180, 830), (width - 180, 830)], fill=config.COLOR_GOLD_LIGHT, width=1)
        draw.line([(cx - 150, 830), (cx + 150, 830)], fill=config.COLOR_GOLD_PRIMARY, width=3)

        # 7. Lower Section: Left Details, Center Seal, Center-Right Signature, Bottom-Right QR
        # -------------------------------------------------------------
        # Left Block: Certificate ID & Completion Date
        left_x = 170
        draw.text((left_x, 900), "CERTIFICATE DETAILS", fill=config.COLOR_GOLD_DARK, font=self.font_label)
        draw.line([(left_x, 922), (left_x + 280, 922)], fill=config.COLOR_GOLD_PRIMARY, width=1)

        draw.text((left_x, 940), "Certificate ID:", fill=config.COLOR_TEXT_MUTED, font=self.font_meta)
        draw.text((left_x, 965), student.certificate_id, fill=config.COLOR_NAVY_PRIMARY, font=self.font_value)

        draw.text((left_x, 1010), "Completion Date:", fill=config.COLOR_TEXT_MUTED, font=self.font_meta)
        draw.text((left_x, 1035), student.completion_date, fill=config.COLOR_NAVY_PRIMARY, font=self.font_value)

        draw.text((left_x, 1080), "Issued By:", fill=config.COLOR_TEXT_MUTED, font=self.font_meta)
        draw.text((left_x, 1105), self.config.company_name, fill=config.COLOR_TEXT_PRIMARY, font=self.font_value)

        draw.text((left_x, 1150), "Verification Status:", fill=config.COLOR_TEXT_MUTED, font=self.font_meta)
        # Draw green verification badge with checkmark
        badge_y = 1177
        draw.ellipse([left_x, badge_y, left_x + 18, badge_y + 18], fill="#166534")
        draw.line([(left_x + 4, badge_y + 9), (left_x + 8, badge_y + 13), (left_x + 14, badge_y + 5)], fill="#FFFFFF", width=2)
        draw.text((left_x + 26, 1174), "Official & Verified", fill="#166534", font=self.font_value)

        # -------------------------------------------------------------
        # Center Block: Official Gold Seal
        seal_size = 230
        resized_seal = self.seal_img.resize((seal_size, seal_size), Image.Resampling.LANCZOS)
        seal_x = cx - 115
        seal_y = 930
        cert.paste(resized_seal, (seal_x, seal_y), resized_seal)

        draw.text((cx, 1180), "OFFICIAL VERIFICATION SEAL", fill=config.COLOR_GOLD_DARK, font=self.font_label, anchor="mm")
        draw.text((cx, 1205), "RAFAI TECHNOLOGIES", fill=config.COLOR_TEXT_MUTED, font=self.font_meta, anchor="mm")

        # -------------------------------------------------------------
        # Center-Right Block: Instructor Signature & Designation
        sig_x = 1440
        sig_w, sig_h = 280, 95
        resized_sig = self.signature_img.resize((sig_w, sig_h), Image.Resampling.LANCZOS)
        cert.paste(resized_sig, (sig_x, 955), resized_sig)

        # Signature rule line
        draw.line([(sig_x, 1060), (sig_x + sig_w, 1060)], fill=config.COLOR_NAVY_PRIMARY, width=2)

        instructor_cx = sig_x + sig_w // 2
        draw.text(
            (instructor_cx, 1085),
            self.config.instructor_name,
            fill=config.COLOR_NAVY_PRIMARY,
            font=self.font_value,
            anchor="mm"
        )
        draw.text(
            (instructor_cx, 1115),
            self.config.instructor_title,
            fill=config.COLOR_TEXT_MUTED,
            font=self.font_meta,
            anchor="mm"
        )
        draw.text(
            (instructor_cx, 1140),
            self.config.company_name,
            fill=config.COLOR_GOLD_DARK,
            font=self.font_label,
            anchor="mm"
        )

         

        # -------------------------------------------------------------
        # Footer Bar (Bottom Inset)
        draw.line([(100, 1310), (width - 100, 1310)], fill=config.COLOR_GOLD_LIGHT, width=1)
        draw.text(
            (cx, 1330),
            f"This credential is independently verifiable via id. Issued by {self.config.company_name}. All rights reserved.",
            fill=config.COLOR_TEXT_MUTED,
            font=self.font_footer,
            anchor="mm"
        )

        return cert

    def render_certificate_pdf(self, student: StudentRecord, img: Image.Image, output_pdf_path: Path) -> Path:
        """
        Saves a 300 DPI print-ready A4 landscape PDF from the rendered image.
        Uses ReportLab with high-fidelity canvas embedding and official document metadata.
        """
        output_pdf_path = Path(output_pdf_path)
        output_pdf_path.parent.mkdir(parents=True, exist_ok=True)

        # Create temporary buffer for high-res PNG image
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)

        # Standard A4 Landscape: 841.89 x 595.28 points
        c = canvas.Canvas(str(output_pdf_path), pagesize=landscape(A4))
        c.setTitle(f"Certificate of Completion - {student.student_name}")
        c.setAuthor(self.config.company_name)
        c.setSubject(f"{student.course} Certification")
        c.setCreator(f"{self.config.company_name} Certificate Generator")
        c.setKeywords([student.certificate_id, student.student_name, student.course, "Certificate"])

        # Embed high-resolution image directly into canvas
        from reportlab.lib.utils import ImageReader
        img_reader = ImageReader(buf)
        c.drawImage(img_reader, 0, 0, width=841.89, height=595.28)
        c.showPage()
        c.save()

        return output_pdf_path

    def generate_single_certificate(
        self,
        student: StudentRecord,
        output_dir: Path,
        generate_pdf: bool = True,
        generate_png: bool = True
    ) -> Dict[str, Path]:
        """
        Renders and saves PNG and/or PDF certificates for a single student.
        """
        output_dir = Path(output_dir)
        pdf_dir = output_dir / "PDF"
        png_dir = output_dir / "PNG"

        pdf_dir.mkdir(parents=True, exist_ok=True)
        png_dir.mkdir(parents=True, exist_ok=True)

        results = {}
        cert_img = self.render_certificate_image(student)

        if generate_png:
            png_path = png_dir / student.png_filename
            cert_img.save(png_path, format="PNG", dpi=(300, 300))
            results["png"] = png_path

        if generate_pdf:
            pdf_path = pdf_dir / student.pdf_filename
            self.render_certificate_pdf(student, cert_img, pdf_path)
            results["pdf"] = pdf_path

        return results

    def generate_batch(
        self,
        students: List[StudentRecord],
        output_dir: Path,
        generate_pdf: bool = True,
        generate_png: bool = True,
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> BatchGenerationResult:
        """
        Executes bulk certificate generation for a list of valid students.
        Never crashes because of one student error; records failure and continues.
        """
        start_time = time.time()
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        result = BatchGenerationResult(total_requested=len(students))

        for idx, student in enumerate(students, start=1):
            try:
                paths = self.generate_single_certificate(
                    student=student,
                    output_dir=output_dir,
                    generate_pdf=generate_pdf,
                    generate_png=generate_png
                )
                result.generated_count += 1
                result.generated_files.append({
                    "row_number": student.row_number,
                    "student_name": student.student_name,
                    "college": student.college,
                    "course": student.course,
                    "completion_date": student.completion_date,
                    "certificate_id": student.certificate_id,
                    "pdf_path": str(paths.get("pdf", "")),
                    "png_path": str(paths.get("png", "")),
                    "status": "Success"
                })
            except Exception as e:
                result.failed_count += 1
                result.errors.append({
                    "row_number": student.row_number,
                    "student_name": student.student_name,
                    "certificate_id": student.certificate_id,
                    "error": str(e)
                })

            if progress_callback:
                progress_callback(idx, len(students), student.student_name)

        result.elapsed_seconds = round(time.time() - start_time, 2)
        return result

    def create_zip_archive(
        self,
        output_dir: Path,
        students: List[StudentRecord],
        zip_filename: str = "RAFAI_AI_Foundation_Certificates.zip",
        include_png: bool = True
    ) -> Path:
        """
        Creates a clean ZIP archive containing:
        - PDF/ directory with all PDF certificates
        - PNG/ directory with all PNG certificates (if include_png is True)
        - manifest.csv with complete issuance and verification records
        """
        output_dir = Path(output_dir)
        zip_path = output_dir / zip_filename

        manifest_rows = []
        for s in students:
            manifest_rows.append({
                "Certificate ID": s.certificate_id,
                "Student Name": s.student_name,
                "College": s.college,
                "Course": s.course,
                "Completion Date": s.completion_date,
                "Email": s.email,
                "PDF Filename": s.pdf_filename,
                "PNG Filename": s.png_filename,
                "Status": "Issued & Verified",
            })
        manifest_df = pd.DataFrame(manifest_rows)

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            # Write manifest CSV
            manifest_csv_bytes = manifest_df.to_csv(index=False).encode("utf-8")
            zipf.writestr("manifest.csv", manifest_csv_bytes)

            # Write PDFs
            pdf_dir = output_dir / "PDF"
            if pdf_dir.exists():
                for p in pdf_dir.glob("*.pdf"):
                    zipf.write(p, arcname=f"PDF/{p.name}")

            # Write PNGs
            if include_png:
                png_dir = output_dir / "PNG"
                if png_dir.exists():
                    for p in png_dir.glob("*.png"):
                        zipf.write(p, arcname=f"PNG/{p.name}")

        return zip_path
