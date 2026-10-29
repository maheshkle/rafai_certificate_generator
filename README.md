# RAFAI Technologies - AI Foundation Certificate Generator

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![Streamlit App](https://img.shields.io/badge/Streamlit-1.35%2B-FF4B4B.svg)](https://streamlit.io/)
[![ReportLab](https://img.shields.io/badge/ReportLab-4.2%2B-orange.svg)](https://www.reportlab.com/)
[![License: Proprietary](https://img.shields.io/badge/License-RAFAI%20Technologies-navy.svg)](#)

An enterprise-grade, dynamic Certificate Generation Web Application engineered for **RAFAI TECHNOLOGIES**. The platform automates the batch generation of verifiable, tamper-evident completion certificates for students completing the **AI Foundation** course across universities and colleges.

The system supports Excel/CSV bulk ingestion, rigorous multi-point validation, instant visual preview, high-resolution rendering (300 DPI PNG & print-ready A4 PDF), digital verification QR codes, and automated ZIP packaging with manifest audit logs.

---

## Table of Contents
- [Architecture & Overview](#architecture--overview)
- [Key Features](#key-features)
- [System Requirements](#system-requirements)
- [Installation & Setup](#installation--setup)
- [Running the Application](#running-the-application)
- [Excel & CSV Format Specifications](#excel--csv-format-specifications)
- [Folder Structure](#folder-structure)
- [Customization Guide](#customization-guide)
  - [How to Replace the Company Logo](#how-to-replace-the-company-logo)
  - [How to Replace Instructor Signature](#how-to-replace-instructor-signature)
  - [How to Customize the Certificate Background Template](#how-to-customize-the-certificate-background-template)
  - [Configuring Certificate ID & Numbering](#configuring-certificate-id--numbering)
- [Generating 50+ to 500+ Certificates](#generating-50-to-500-certificates)
- [Security & Error Handling](#security--error-handling)
- [Verification QR Code Protocol](#verification-qr-code-protocol)
- [Testing](#testing)

---

## Architecture & Overview

The application follows a clean separation of concerns:

```
┌────────────────────────────────────────────────────────┐
│                        app.py                          │
│        Streamlit Executive Dashboard & Web UI         │
└──────────────┬─────────────────────────┬───────────────┘
               │                         │
               ▼                         ▼
┌──────────────────────────────┐ ┌──────────────────────────────┐
│       excel_handler.py       │ │   certificate_generator.py   │
│ Ingestion, Schema Mapping,   │ │ Rendering Engine, Typography,│
│ Validation & Deduplication   │ │ PDF/PNG Export, ZIP Packager │
└──────────────┬───────────────┘ └──────────────┬───────────────┘
               │                                │
               ▼                                ▼
┌──────────────────────────────┐ ┌──────────────────────────────┐
│          config.py           │ │       qr_generator.py        │
│ Design Tokens, Paths & State │ │ Tamper-Evident QR Generator  │
└──────────────────────────────┘ └──────────────────────────────┘
```

- **`app.py`**: Streamlit web interface with real-time feedback, metric summaries, live single-certificate preview, batch progress indicators, and one-click ZIP download.
- **`certificate_generator.py`**: High-performance certificate rendering engine producing 300 DPI high-resolution PNGs and vector-aligned A4 Landscape PDFs using ReportLab.
- **`excel_handler.py`**: Resilient data reader for `.xlsx`, `.xls`, and `.csv` files. Performs flexible header normalization, mandatory field validation, date parsing, student deduplication, filename sanitization, and batch ID sequencing.
- **`qr_generator.py`**: High-contrast, error-corrected QR code generator embedding structured verification payloads.
- **`asset_generator.py`**: Programmatic visual asset synthesizer that creates crisp default logos, cursive signatures, gold embossed seals, and ornate templates if custom assets are not provided.
- **`config.py`**: Central repository for application constants, color palettes, dimensions, and default metadata.

---

## Key Features

1. **Flexible Bulk Ingestion**:
   - Accepts Excel (`.xlsx`, `.xls`) and CSV files.
   - Handles 5, 50, 500, or unlimited student records without hardcoded limits.
   - Column name flexibility (e.g., automatically recognizes `Student Name`, `StudentName`, `Name`, `Full Name`).

2. **Enterprise Validation & Fault Tolerance**:
   - **Zero-Crash Architecture**: A malformed row will never abort the entire batch.
   - Invalid records are isolated and clearly reported in an interactive error breakdown (showing Excel row number, student name, and exact rejection reason).
   - Valid records are processed continuously.
   - Automatic student deduplication per batch.

3. **High-Fidelity Landscape Certificate Design**:
   - Official landscape canvas (2000 × 1414 px, 300 DPI).
   - Dual-layer geometric navy and royal gold borders with ornate corner brackets.
   - Dynamic font auto-scaling for long student names to prevent truncation or overlap.
   - Official Gold Embossed Verification Seal with vector star accents.
   - Realistic cursive instructor signature with designation.
   - High-contrast corporate emblem.

4. **Dual Output (PDF + PNG)**:
   - **PDF**: Print-ready A4 landscape vector PDF generated with ReportLab.
   - **PNG**: 300 DPI lossless image suitable for digital credentials and social media (LinkedIn).
   - Sanitized filenames: `Student_Name_CertificateID.pdf` and `Student_Name_CertificateID.png`.

5. **Tamper-Evident QR Code Verification**:
   - Embedded on the bottom-right of every certificate.
   - Encodes Certificate ID, Student Name, College, Course, Issue Date, and Issuing Authority.

6. **Automated ZIP Compilation**:
   - Bundles all generated PDFs into a `PDF/` folder and PNGs into a `PNG/` folder.
   - Injects a `manifest.csv` audit record mapping every student to their Certificate ID, filenames, and validation status.

---

## System Requirements

- **Operating System**: Windows 10/11, macOS, or Linux (Ubuntu 20.04+)
- **Python**: Version 3.11, 3.12, 3.13, or 3.14
- **RAM**: Minimum 2 GB (4 GB recommended for 500+ student batches)
- **Disk Space**: ~200 MB for dependencies and outputs

---

## Installation & Setup

### 1. Clone or Navigate to the Repository
```bash
cd c:\Users\Admin\rafai_certificate_generator
```

### 2. Create and Activate a Virtual Environment (Recommended)

**On Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**On Windows (Command Prompt):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**On Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Required Dependencies
```bash
pip install -r requirements.txt
```

Verify that all dependencies installed cleanly:
```bash
python -c "import streamlit, pandas, openpyxl, PIL, reportlab, qrcode, dateutil; print('All dependencies installed successfully!')"
```

---

## Running the Application

Launch the Streamlit web server:

```bash
python -m streamlit run app.py
```

Once started, the application will be accessible at:
- **Local URL**: `http://localhost:8501`
- **Network URL**: `http://<your-ip>:8501`

---

## Excel & CSV Format Specifications

The application reads `.xlsx`, `.xls`, and `.csv` files.

### Expected Columns:
| Column Name | Required? | Description | Example |
| :--- | :---: | :--- | :--- |
| **Student Name** | **Yes** | Full name of the candidate | `Rahul Sharma` |
| **College** | **Yes** | College / University name | `ABC College of Engineering` |
| **Course** | Optional | Course name (defaults to UI value if empty) | `AI Foundation` |
| **Completion Date** | Optional | Date of passing (defaults to UI date if empty) | `24-Sep-2026` |
| **Email** | Optional | Contact email for the student | `rahul@example.com` |

### Sample Data Representation:

```text
Student Name | College | Course | Completion Date | Email
Rahul Sharma | ABC College of Engineering | AI Foundation | 24-Sep-2026 | rahul@example.com
Priya Patil  | VJTI Mumbai                | AI Foundation | 24-Sep-2026 | priya@example.com
Aarav Patel  | COEP Technological Univ    | AI Foundation | 24-Sep-2026 | aarav@example.com
```

> **Note on Dates**: Flexible date formats are supported: `24-Sep-2026`, `24/09/2026`, `2026-09-24`, or Excel date serials. If omitted in a row, the completion date configured in the UI sidebar is automatically applied.

---

## Folder Structure

```
rafai_certificate_generator/
├── app.py                      # Streamlit executive user interface
├── certificate_generator.py    # Dual PDF & PNG rendering engine & batch processor
├── excel_handler.py            # Data ingestion, schema validation & deduplication
├── qr_generator.py             # Tamper-evident verification QR code generator
├── asset_generator.py          # Programmatic synthesizer for logo, seal & signature
├── config.py                   # Central design tokens, palettes & configurations
├── test_pipeline.py            # Automated end-to-end test suite
├── requirements.txt            # Python dependencies
├── README.md                   # Complete architectural and operations manual
│
├── assets/                     # Visual assets (auto-generated or customized)
│   ├── rafai_logo.png          # High-resolution company emblem & wordmark
│   ├── instructor_signature.png# Instructor cursive signature graphic
│   ├── official_seal.png       # Gold embossed verification seal badge
│   └── certificate_template.png# High-resolution 2000x1414 landscape background
│
├── sample_data/                # Ready-to-use sample spreadsheets
│   ├── sample_students_ai_foundation.xlsx  # Clean dataset (52 college students)
│   ├── sample_students_ai_foundation.csv   # Clean CSV dataset
│   └── sample_students_with_errors.xlsx    # Test file with validation edge cases
│
└── output/                     # Generated certificates and packages
    ├── PDF/                    # Printable vector-compatible PDFs
    ├── PNG/                    # 300 DPI high-resolution images
    └── RAFAI_AI_Foundation_Certificates.zip # Master archive with manifest.csv
```

---

## Customization Guide

### How to Replace the Company Logo
1. **Via UI**: In the sidebar, expand **🎨 Asset Customization** and upload your logo (`.png` or `.jpg`).
2. **Via File**: Replace `assets/rafai_logo.png` with your transparent PNG logo (recommended dimensions: ~700 × 200 px).

### How to Replace Instructor Signature
1. **Via UI**: In the sidebar, expand **🎨 Asset Customization** and upload a signature image.
2. **Via File**: Replace `assets/instructor_signature.png` with a transparent PNG of the signature (recommended dimensions: ~500 × 160 px).

### How to Customize the Certificate Background Template
1. **Via UI**: Upload your custom background template under **🎨 Asset Customization**.
2. **Via File**: Replace `assets/certificate_template.png` with your custom high-res landscape graphic (recommended size: `2000 × 1414` px).
3. If no template file exists, `asset_generator.py` automatically generates the default double-gold ornate background.

### Configuring Certificate ID & Numbering
In the left sidebar:
- **Prefix**: Set prefix code (e.g., `RAFAI-AI-2026`).
- **Start #**: Set initial integer sequence (e.g., `1` produces `RAFAI-AI-2026-0001`, `0002`, etc.).

---

## Generating 50+ to 500+ Certificates

1. Start the application: `python -m streamlit run app.py`.
2. Click **"📥 Sample Excel (52 Clean)"** to obtain the pre-formatted 52-student dataset, or upload your own Excel/CSV file.
3. Review the **Validation & Dataset Summary** cards:
   - Ensure **Valid Records** matches your expected count.
   - If invalid records are detected, expand the **Validation Error Report** to identify the specific rows and reasons.
4. Select any student in the **Step 3: Live Certificate Preview** dropdown to inspect their personalized certificate live before initiating bulk export.
5. Click **"🚀 Generate Certificates"**.
   - The real-time progress bar tracks progress: `50 / 50 (100%)`.
6. Once complete, click **"📥 Download All Certificates ZIP"**.
7. Extract the ZIP file to access:
   - `PDF/`: All printable PDF certificates (`Student_Name_CertificateID.pdf`).
   - `PNG/`: All 300 DPI images (`Student_Name_CertificateID.png`).
   - `manifest.csv`: Comprehensive verification audit report.

---

## Security & Error Handling

- **Formula Injection Mitigation**: Files are parsed via openpyxl and pandas strictly as text/data values; formulas and macro scripts are never executed.
- **Filename Sanitization**: Recipient names are sanitized using strict regex filters (`re.sub(r'[\\/*?:"<>|]', '', name)`), preventing directory traversal attacks or filesystem character errors on Windows and Linux.
- **Fault-Tolerant Processing**: In bulk generation loops, each certificate render is wrapped in isolated exception handlers. If an unexpected error occurs on one record, it is logged and the remaining batch continues without interruption.
- **Path Shielding**: Internal server filesystem paths are never exposed to the client interface.

---

## Verification QR Code Protocol

Every certificate features an individual QR code at the bottom-right corner. Scanning the QR code with any standard smartphone camera or QR reader decodes the tamper-evident payload:

```text
CERTIFICATE VERIFICATION
Certificate ID: RAFAI-AI-2026-0001
Recipient: Rahul Sharma
Course: AI Foundation
Completion Date: 08-Oct-2026
Issuing Authority: RAFAI TECHNOLOGIES
Status: VALID & VERIFIED
```

---

## Testing

The application includes an automated end-to-end verification test suite:

```bash
python test_pipeline.py
```

This verifies:
- Clean and error-injected Excel generation.
- Schema parsing, column normalization, and validation rules.
- QR code payload integrity.
- PNG and PDF rendering accuracy.
- ZIP packaging and manifest file verification.

---

## Technical Specifications Summary

| Feature | Specification |
| :--- | :--- |
| **Language** | Python 3.11+ (Tested on 3.14) |
| **Web Framework** | Streamlit 1.35+ |
| **Image Processing** | Pillow (PIL) 10.3+ |
| **PDF Generation** | ReportLab 4.2+ (A4 Landscape) |
| **Spreadsheet Engine**| Pandas + OpenPyXL |
| **QR Code Engine** | qrcode[pil] (Error Correction Level M/H) |
| **Date Parsing** | python-dateutil |
| **Resolution** | 2000 × 1414 pixels @ 300 DPI |
| **Output Formats** | PDF, PNG, ZIP, CSV Manifest |

---

Developed for **RAFAI TECHNOLOGIES** • *Enterprise AI Training & Certification Division*
