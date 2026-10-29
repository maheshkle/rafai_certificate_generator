"""
Streamlit Web Application: RAFAI Technologies - AI Foundation Certificate Generator.
Enterprise-grade dynamic bulk certificate generation system.
"""

import io
import time
from pathlib import Path
from datetime import date
import pandas as pd
import streamlit as st
from PIL import Image

import config
import asset_generator
from excel_handler import (
    parse_and_validate_students,
    create_sample_dataset,
    ValidationResult,
    StudentRecord,
)
from certificate_generator import (
    CertificateGenerator,
    BatchGenerationResult,
)

# Page Configuration
st.set_page_config(
    page_title=config.APP_TITLE,
    page_icon=config.APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)

# Ensure default assets exist at startup
asset_generator.ensure_default_assets()

# Inject Custom CSS for Premium Design Aesthetic
st.markdown("""
<style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Playfair+Display:ital,wght@0,600;0,700;1,600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Main Container Padding */
    .block-container {
        padding-top: 1.8rem;
        padding-bottom: 3rem;
        max-width: 95rem;
    }

    /* Hero Banner */
    .hero-banner {
        background: linear-gradient(135deg, #071329 0%, #0F2854 60%, #1B4380 100%);
        border: 1px solid #C5A059;
        border-radius: 14px;
        padding: 24px 30px;
        color: #FFFFFF;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px rgba(7, 19, 41, 0.15);
        position: relative;
        overflow: hidden;
    }
    .hero-banner::after {
        content: "";
        position: absolute;
        top: -50%;
        right: -20%;
        width: 400px;
        height: 400px;
        background: radial-gradient(circle, rgba(197, 160, 89, 0.15) 0%, rgba(255,255,255,0) 70%);
        border-radius: 50%;
        pointer-events: none;
    }
    .hero-title {
        font-family: 'Playfair Display', serif;
        font-size: 2.1rem;
        font-weight: 700;
        letter-spacing: 0.5px;
        margin: 0 0 6px 0;
        color: #FAF6EE;
    }
    .hero-subtitle {
        font-size: 1.0rem;
        color: #C5A059;
        font-weight: 500;
        margin: 0;
    }
    .hero-badge {
        display: inline-block;
        background: rgba(197, 160, 89, 0.2);
        color: #E9D29B;
        border: 1px solid #C5A059;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-bottom: 10px;
    }

    /* Metric Cards */
    .metric-card {
        background: #FFFFF;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
        border-left: 5px solid #0F2854;
        padding: 16px 20px;
        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.04);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(15, 40, 84, 0.08);
    }
    .metric-card.gold {
        border-left-color: #C5A059;
    }
    .metric-card.success {
        border-left-color: #10B981;
    }
    .metric-card.error {
        border-left-color: #EF4444;
    }
    .metric-title {
        font-size: 0.82rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #64748B;
        font-weight: 600;
        margin-bottom: 4px;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 800;
        color: #0F172A;
        margin: 0;
    }

    /* Custom Section Headers */
    .section-header {
        font-size: 1.25rem;
        font-weight: 700;
        color: #0F2854;
        margin-top: 15px;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* Custom Table Styling */
    .stDataFrame {
        border-radius: 8px;
        overflow: hidden;
        border: 1px solid #E2E8F0;
    }

    /* Sidebar Header */
    .sidebar-header {
        font-family: 'Playfair Display', serif;
        font-size: 1.25rem;
        font-weight: 700;
        color: #0F2854;
        margin-bottom: 15px;
        border-bottom: 2px solid #C5A059;
        padding-bottom: 8px;
    }
</style>
""", unsafe_allow_html=True)


# ==============================================================================
# SIDEBAR CONFIGURATION
# ==============================================================================
with st.sidebar:
    st.markdown('<div class="sidebar-header">🏛️ Batch Configuration</div>', unsafe_allow_html=True)

    company_name = st.text_input(
        "Company Name",
        value=config.COMPANY_NAME_DEFAULT,
        help="Official issuing organization printed on the certificate.",
    )

    course_name = st.text_input(
        "Course Name",
        value=config.COURSE_NAME_DEFAULT,
        help="Default course title if not specified per-student in the Excel sheet.",
    )

    instructor_name = st.text_input(
        "Instructor Name",
        value=config.INSTRUCTOR_NAME_DEFAULT,
        help="Name printed beneath the instructor signature line.",
    )

    instructor_title = st.text_input(
        "Instructor Title",
        value=config.INSTRUCTOR_TITLE_DEFAULT,
        help="Designation / official role of the instructor.",
    )

    # Date Picker with fallback string
    selected_date = st.date_input(
        "Completion Date",
        value=date(2026, 10, 8),
        help="Default completion date if not specified per-student in the file.",
    )
    completion_date_str = selected_date.strftime("%d-%b-%Y")

    st.markdown("---")
    st.markdown('<div class="sidebar-header">🔢 Certificate ID Settings</div>', unsafe_allow_html=True)

    col_prefix, col_start = st.columns([3, 2])
    with col_prefix:
        cert_prefix = st.text_input(
            "Prefix",
            value=config.PREFIX_DEFAULT,
            help="Prefix format (e.g. RAFAI-AI-2026)",
        )
    with col_start:
        start_number = st.number_input(
            "Start #",
            min_value=1,
            value=config.START_NUMBER_DEFAULT,
            step=1,
            help="Starting sequence number (e.g. 1 -> 0001)",
        )

    st.markdown("---")
    with st.expander("🎨 Asset Customization (Logo / Sig / Seal)"):
        st.caption("Upload custom assets or keep defaults:")
        custom_logo = st.file_uploader("Replace Logo", type=["png", "jpg", "jpeg"], key="upload_logo")
        custom_sig = st.file_uploader("Replace Signature", type=["png", "jpg", "jpeg"], key="upload_sig")
        custom_template = st.file_uploader("Replace Template", type=["png", "jpg", "jpeg"], key="upload_template")

        if st.button("Reset Assets to Defaults"):
            asset_generator.create_default_logo(config.DEFAULT_LOGO_PATH)
            asset_generator.create_default_signature(config.DEFAULT_SIGNATURE_PATH)
            asset_generator.create_default_seal(config.DEFAULT_SEAL_PATH)
            asset_generator.create_default_template(config.DEFAULT_TEMPLATE_PATH)
            st.success("Default assets restored.")
            st.rerun()

    st.markdown("---")
    st.markdown("⚙️ **Output Formats**")
    gen_pdf = st.checkbox("Generate PDF (Print-Ready)", value=True)
    gen_png = st.checkbox("Generate PNG (High-Res 300 DPI)", value=True)

    if not (gen_pdf or gen_png):
        st.warning("Please select at least one output format (PDF or PNG).")


# Handle custom asset updates if provided
active_logo_path = config.DEFAULT_LOGO_PATH
if custom_logo:
    active_logo_path = config.ASSETS_DIR / "custom_logo.png"
    with open(active_logo_path, "wb") as f:
        f.write(custom_logo.getbuffer())

active_sig_path = config.DEFAULT_SIGNATURE_PATH
if custom_sig:
    active_sig_path = config.ASSETS_DIR / "custom_signature.png"
    with open(active_sig_path, "wb") as f:
        f.write(custom_sig.getbuffer())

active_template_path = config.DEFAULT_TEMPLATE_PATH
if custom_template:
    active_template_path = config.ASSETS_DIR / "custom_template.png"
    with open(active_template_path, "wb") as f:
        f.write(custom_template.getbuffer())

# Construct Active Certificate Configuration
cert_config = config.CertificateConfig(
    company_name=company_name,
    course_name=course_name,
    instructor_name=instructor_name,
    instructor_title=instructor_title,
    completion_date_str=completion_date_str,
    prefix=cert_prefix,
    start_number=int(start_number),
    logo_path=active_logo_path,
    signature_path=active_sig_path,
    template_path=active_template_path,
    generate_png=gen_png,
    generate_pdf=gen_pdf,
)

generator = CertificateGenerator(cert_config)


# ==============================================================================
# MAIN PAGE: HERO BANNER
# ==============================================================================
st.markdown(f"""
<div class="hero-banner">
    <div class="hero-badge">AI FOUNDATION ACCREDITATION</div>
    <h1 class="hero-title">{config.APP_TITLE}</h1>
    <p class="hero-subtitle">High-throughput automated certificate generation with verified QR codes, dual PDF/PNG export, and enterprise validation.</p>
</div>
""", unsafe_allow_html=True)


# ==============================================================================
# SAMPLE TEMPLATE DOWNLOAD BAR
# ==============================================================================
with st.container():
    col_info, col_btn1, col_btn2 = st.columns([5, 3, 3])
    with col_info:
        st.markdown("**Need a starter dataset?** Download pre-formatted sample files containing 50+ college students:")

    clean_sample_path = config.SAMPLE_DATA_DIR / "sample_students_ai_foundation.xlsx"
    if not clean_sample_path.exists():
        create_sample_dataset(clean_sample_path, num_students=52, include_invalid=False)

    with open(clean_sample_path, "rb") as f:
        sample_excel_bytes = f.read()

    invalid_sample_path = config.SAMPLE_DATA_DIR / "sample_students_with_errors.xlsx"
    if not invalid_sample_path.exists():
        create_sample_dataset(invalid_sample_path, num_students=50, include_invalid=True)

    with open(invalid_sample_path, "rb") as f:
        invalid_excel_bytes = f.read()

    with col_btn1:
        st.download_button(
            label="📥 Sample Excel (52 Clean)",
            data=sample_excel_bytes,
            file_name="sample_students_ai_foundation.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
    with col_btn2:
        st.download_button(
            label="🧪 Test Sample (With Errors)",
            data=invalid_excel_bytes,
            file_name="sample_students_with_validation_errors.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            help="Includes missing names, blank colleges, duplicate student, and invalid date to test the validation engine.",
        )


# ==============================================================================
# DATA INGESTION: UPLOADER OR ONE-CLICK DEMO LOAD
# ==============================================================================
st.markdown('<div class="section-header">📂 Step 1: Upload Student Records</div>', unsafe_allow_html=True)

upload_col, demo_col = st.columns([3, 1])

with upload_col:
    uploaded_file = st.file_uploader(
        "Upload Excel (.xlsx, .xls) or CSV file with student records:",
        type=["xlsx", "xls", "csv"],
        help="Expected columns: Student Name, College, Course, Completion Date, Email",
    )

with demo_col:
    st.markdown("<div style='height: 28px'></div>", unsafe_allow_html=True)
    use_sample = st.button("🚀 Load 52 Student Sample", use_container_width=True)
    if use_sample:
        st.session_state["use_sample_data"] = True

active_data_source = None
if uploaded_file is not None:
    active_data_source = uploaded_file
elif st.session_state.get("use_sample_data", False):
    active_data_source = clean_sample_path
else:
    # Default to auto-loading sample data so user immediately sees live UI
    active_data_source = clean_sample_path


# ==============================================================================
# DATA PARSING & VALIDATION
# ==============================================================================
if active_data_source:
    with st.spinner("Analyzing and validating student data..."):
        validation_result: ValidationResult = parse_and_validate_students(
            file_or_path=active_data_source,
            default_course=course_name,
            default_completion_date=completion_date_str,
            prefix=cert_prefix,
            start_number=int(start_number),
        )

    # Metric summary cards
    st.markdown('<div class="section-header">📊 Step 2: Validation & Dataset Summary</div>', unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)

    with m1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Total Records</div>
            <div class="metric-value">{validation_result.total_rows}</div>
        </div>
        """, unsafe_allow_html=True)

    with m2:
        st.markdown(f"""
        <div class="metric-card success">
            <div class="metric-title">Valid Records</div>
            <div class="metric-value">{validation_result.valid_count}</div>
        </div>
        """, unsafe_allow_html=True)

    with m3:
        err_class = "error" if validation_result.invalid_count > 0 else "metric-card"
        st.markdown(f"""
        <div class="metric-card {err_class}">
            <div class="metric-title">Flagged / Invalid</div>
            <div class="metric-value">{validation_result.invalid_count}</div>
        </div>
        """, unsafe_allow_html=True)

    with m4:
        id_range_str = "-"
        if validation_result.valid_records:
            first_id = validation_result.valid_records[0].certificate_id
            last_id = validation_result.valid_records[-1].certificate_id
            id_range_str = f"{first_id} → {last_id.split('-')[-1]}"

        st.markdown(f"""
        <div class="metric-card gold">
            <div class="metric-title">Certificate ID Range</div>
            <div class="metric-value" style="font-size: 1.25rem; font-weight: 700; padding-top: 6px;">{id_range_str}</div>
        </div>
        """, unsafe_allow_html=True)

    # Validation Error Alerts
    if validation_result.invalid_count > 0:
        st.warning(
            f"⚠️ **Attention**: Found {validation_result.invalid_count} invalid or incomplete row(s). "
            f"These rows have been isolated and removed from generation. All {validation_result.valid_count} valid students will be processed without interruption."
        )
        with st.expander(f"🔍 View Detailed Validation Error Report ({validation_result.invalid_count} rows)", expanded=True):
            st.dataframe(
                validation_result.errors_dataframe(),
                use_container_width=True,
                hide_index=True,
            )
    else:
        st.success(f"✓ All {validation_result.valid_count} student records passed strict validation with zero errors!")

    # Student Records Table
    with st.expander("📋 Inspect Validated Student Records", expanded=False):
        valid_df = validation_result.to_dataframe()
        if not valid_df.empty:
            search_query = st.text_input("🔍 Search records by Student Name, College, or Certificate ID:")
            if search_query:
                filtered_df = valid_df[
                    valid_df["Student Name"].str.contains(search_query, case=False, na=False) |
                    valid_df["College"].str.contains(search_query, case=False, na=False) |
                    valid_df["Certificate ID"].str.contains(search_query, case=False, na=False)
                ]
                st.dataframe(filtered_df, use_container_width=True, hide_index=True)
            else:
                st.dataframe(valid_df, use_container_width=True, hide_index=True)

    # ==============================================================================
    # STEP 3: LIVE CERTIFICATE PREVIEW
    # ==============================================================================
    st.markdown('<div class="section-header">👁️ Step 3: Live Certificate Preview</div>', unsafe_allow_html=True)

    if validation_result.valid_records:
        preview_names = [f"{s.student_name} ({s.certificate_id}) - {s.college}" for s in validation_result.valid_records]
        selected_preview_idx = st.selectbox(
            "Select a student to inspect their exact live certificate:",
            options=range(len(preview_names)),
            format_func=lambda i: preview_names[i],
            index=0,
        )

        selected_student = validation_result.valid_records[selected_preview_idx]

        preview_col, details_col = st.columns([7, 3])

        with preview_col:
            # Generate live preview image
            preview_img = generator.render_certificate_image(selected_student)
            st.image(
                preview_img,
                caption=f"Live Preview: {selected_student.student_name} | {selected_student.certificate_id}",
                use_container_width=True,
            )

        with details_col:
            st.markdown("### Certificate Metadata")
            st.markdown(f"**Recipient:** `{selected_student.student_name}`")
            st.markdown(f"**Certificate ID:** `{selected_student.certificate_id}`")
            st.markdown(f"**College:** `{selected_student.college}`")
            st.markdown(f"**Course:** `{selected_student.course}`")
            st.markdown(f"**Completion Date:** `{selected_student.completion_date}`")
            st.markdown(f"**Issued By:** `{company_name}`")
            st.markdown(f"**Instructor:** `{instructor_name}`")

            st.markdown("---")
            st.markdown("#### Instant Download for Preview")

            # Buffer for individual PNG download
            png_buf = io.BytesIO()
            preview_img.save(png_buf, format="PNG")
            st.download_button(
                label="🖼️ Download Preview (PNG)",
                data=png_buf.getvalue(),
                file_name=selected_student.png_filename,
                mime="image/png",
                use_container_width=True,
            )

            # Buffer for individual PDF download
            pdf_temp_path = config.DEFAULT_OUTPUT_DIR / f"temp_{selected_student.pdf_filename}"
            generator.render_certificate_pdf(selected_student, preview_img, pdf_temp_path)
            with open(pdf_temp_path, "rb") as f:
                pdf_bytes = f.read()

            st.download_button(
                label="📄 Download Preview (PDF)",
                data=pdf_bytes,
                file_name=selected_student.pdf_filename,
                mime="application/pdf",
                use_container_width=True,
            )

    # ==============================================================================
    # STEP 4: BULK GENERATION & PROGRESS
    # ==============================================================================
    st.markdown('<div class="section-header">⚡ Step 4: Bulk Certificate Generation</div>', unsafe_allow_html=True)

    if validation_result.valid_count == 0:
        st.error("No valid student records available to generate. Please check your uploaded file.")
    else:
        st.markdown(
            f"Click the button below to generate all **{validation_result.valid_count}** certificates "
            f"({'PDF & PNG' if (gen_pdf and gen_png) else ('PDF only' if gen_pdf else 'PNG only')})."
        )

        gen_button_col, _ = st.columns([3, 7])
        with gen_button_col:
            start_generation = st.button(
                f"🚀 Generate {validation_result.valid_count} Certificates",
                type="primary",
                use_container_width=True,
            )

        if start_generation:
            progress_bar = st.progress(0)
            status_text = st.empty()

            def update_progress(current: int, total: int, student_name: str):
                pct = int((current / total) * 100)
                progress_bar.progress(pct)
                status_text.markdown(f"**Generating certificates...** `{current} / {total}` ({pct}%) — *Current: {student_name}*")

            # Execute batch generation
            batch_result: BatchGenerationResult = generator.generate_batch(
                students=validation_result.valid_records,
                output_dir=config.DEFAULT_OUTPUT_DIR,
                generate_pdf=gen_pdf,
                generate_png=gen_png,
                progress_callback=update_progress,
            )

            status_text.markdown(
                f"✅ **Generation Complete!** Generated **{batch_result.generated_count} / {batch_result.total_requested}** "
                f"certificates in **{batch_result.elapsed_seconds}s**."
            )

            # Create ZIP archive
            with st.spinner("Compiling certificates into master ZIP package..."):
                zip_path = generator.create_zip_archive(
                    output_dir=config.DEFAULT_OUTPUT_DIR,
                    students=validation_result.valid_records,
                    zip_filename="RAFAI_AI_Foundation_Certificates.zip",
                    include_png=gen_png,
                )
                zip_size_mb = round(zip_path.stat().st_size / (1024 * 1024), 2)

            st.session_state["batch_completed"] = True
            st.session_state["zip_path"] = str(zip_path)
            st.session_state["zip_size_mb"] = zip_size_mb
            st.session_state["batch_result"] = batch_result

    # ==============================================================================
    # STEP 5: DOWNLOAD MASTER PACKAGE & INDIVIDUAL CERTIFICATES
    # ==============================================================================
    if st.session_state.get("batch_completed", False):
        st.markdown('<div class="section-header">📦 Step 5: Download Certificates</div>', unsafe_allow_html=True)

        zip_p = Path(st.session_state["zip_path"])
        if zip_p.exists():
            with open(zip_p, "rb") as f:
                zip_bytes = f.read()

            dl_col1, dl_col2 = st.columns([5, 5])
            with dl_col1:
                st.download_button(
                    label=f"📥 Download All Certificates ZIP ({st.session_state['zip_size_mb']} MB)",
                    data=zip_bytes,
                    file_name="RAFAI_AI_Foundation_Certificates.zip",
                    mime="application/zip",
                    type="primary",
                    use_container_width=True,
                )
            with dl_col2:
                st.info(
                    "Inside ZIP: `PDF/` folder with all printable PDF certificates, "
                    "`PNG/` folder with 300 DPI images, and `manifest.csv` with full verification records."
                )

        # Tabular browser for all generated certificates
        batch_res: BatchGenerationResult = st.session_state.get("batch_result")
        if batch_res and batch_res.generated_files:
            with st.expander("📂 Explore & Download Individual Generated Certificates", expanded=False):
                res_df = pd.DataFrame(batch_res.generated_files)
                st.dataframe(
                    res_df[["row_number", "certificate_id", "student_name", "college", "completion_date", "status"]],
                    use_container_width=True,
                    hide_index=True,
                )
