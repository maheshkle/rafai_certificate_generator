"""
End-to-End Pipeline Verification Test for RAFAI Technologies Certificate Generator.
Validates Excel reading, data validation, certificate generation, QR code payload, and ZIP packaging.
"""

from pathlib import Path
import sys
import zipfile
import pandas as pd

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import config
from excel_handler import parse_and_validate_students, create_sample_dataset
from certificate_generator import CertificateGenerator
from qr_generator import generate_qr_payload

def run_tests():
    print("=" * 60)
    print("STARTING RAFAI CERTIFICATE GENERATOR VERIFICATION TESTS")
    print("=" * 60)

    # 1. Test Sample Data Creation
    clean_excel = config.SAMPLE_DATA_DIR / "sample_students_ai_foundation.xlsx"
    error_excel = config.SAMPLE_DATA_DIR / "sample_students_with_errors.xlsx"
    create_sample_dataset(clean_excel, num_students=52, include_invalid=False)
    create_sample_dataset(error_excel, num_students=50, include_invalid=True)
    assert clean_excel.exists(), "Clean excel file was not created"
    assert error_excel.exists(), "Error excel file was not created"
    print("✓ Test 1 Passed: Sample Excel datasets created successfully.")

    # 2. Test Ingestion & Validation on Clean Dataset
    res_clean = parse_and_validate_students(clean_excel)
    assert res_clean.total_rows == 52, f"Expected 52 rows, got {res_clean.total_rows}"
    assert res_clean.valid_count == 52, f"Expected 52 valid, got {res_clean.valid_count}"
    assert res_clean.invalid_count == 0, f"Expected 0 invalid, got {res_clean.invalid_count}"
    print("✓ Test 2 Passed: Clean dataset validated (52 valid, 0 invalid).")

    # 3. Test Ingestion & Validation on Error Dataset
    res_error = parse_and_validate_students(error_excel)
    assert res_error.invalid_count > 0, "Expected invalid rows in error dataset"
    assert res_error.valid_count > 0, "Expected valid rows to still be processed"
    print(f"✓ Test 3 Passed: Error isolation verified ({res_error.valid_count} valid, {res_error.invalid_count} rejected).")

    # 4. Test QR Code Payload Content
    sample_student = res_clean.valid_records[0]
    qr_text = generate_qr_payload(
        certificate_id=sample_student.certificate_id,
        student_name=sample_student.student_name,
        course_name=sample_student.course,
        completion_date=sample_student.completion_date,
        company_name=config.COMPANY_NAME_DEFAULT,
    )
    assert sample_student.certificate_id in qr_text
    assert sample_student.student_name in qr_text
    assert sample_student.course in qr_text
    assert sample_student.completion_date in qr_text
    assert config.COMPANY_NAME_DEFAULT in qr_text
    print("✓ Test 4 Passed: QR code verification payload contains all required fields.")

    # 5. Test Certificate Generator (Rendering & Batch Export)
    test_out = config.BASE_DIR / "test_run_output"
    generator = CertificateGenerator()
    batch_res = generator.generate_batch(
        students=res_clean.valid_records[:5], # test with 5 students
        output_dir=test_out,
        generate_pdf=True,
        generate_png=True,
    )
    assert batch_res.generated_count == 5, f"Expected 5 generated, got {batch_res.generated_count}"
    assert batch_res.failed_count == 0, f"Expected 0 failed, got {batch_res.failed_count}"

    for f_info in batch_res.generated_files:
        assert Path(f_info["pdf_path"]).exists(), f"PDF missing: {f_info['pdf_path']}"
        assert Path(f_info["png_path"]).exists(), f"PNG missing: {f_info['png_path']}"
    print("✓ Test 5 Passed: Batch certificate rendering produced valid PDFs & PNGs.")

    # 6. Test ZIP Archive Creation & Manifest Verification
    zip_path = generator.create_zip_archive(
        output_dir=test_out,
        students=res_clean.valid_records[:5],
        zip_filename="RAFAI_AI_Foundation_Certificates.zip",
        include_png=True,
    )
    assert zip_path.exists(), "ZIP archive was not created"
    assert zip_path.stat().st_size > 0, "ZIP archive is empty"

    with zipfile.ZipFile(zip_path, "r") as zf:
        namelist = zf.namelist()
        assert "manifest.csv" in namelist, "manifest.csv missing from ZIP"
        pdf_entries = [n for n in namelist if n.startswith("PDF/") and n.endswith(".pdf")]
        png_entries = [n for n in namelist if n.startswith("PNG/") and n.endswith(".png")]
        assert len(pdf_entries) == 5, f"Expected 5 PDFs in ZIP, got {len(pdf_entries)}"
        assert len(png_entries) == 5, f"Expected 5 PNGs in ZIP, got {len(png_entries)}"

        # Inspect manifest CSV
        with zf.open("manifest.csv") as mf:
            m_df = pd.read_csv(mf)
            assert len(m_df) == 5, f"Expected 5 manifest rows, got {len(m_df)}"
            assert "Certificate ID" in m_df.columns
            assert "Student Name" in m_df.columns
    print("✓ Test 6 Passed: ZIP package structure and manifest.csv verified.")

    # Cleanup test run folder
    import shutil
    shutil.rmtree(test_out, ignore_errors=True)
    print("✓ Test Cleanup: Temporary test artifacts cleaned.")
    print("=" * 60)
    print("ALL TESTS PASSED SUCCESSFULLY! APPLICATION IS READY FOR PRODUCTION.")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()
