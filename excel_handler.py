"""
Excel and CSV handler for RAFAI Technologies Certificate Generator.
Provides robust data ingestion, flexible column mapping, strict validation,
deduplication, certificate ID assignment, filename sanitization, and sample dataset creation.
"""

from typing import List, Dict, Tuple, Optional, Any, Union
from dataclasses import dataclass, field
from pathlib import Path
import re
from io import BytesIO
import datetime
import pandas as pd
from dateutil import parser as date_parser

import config


@dataclass
class ValidationError:
    """Represents a failed student record validation."""
    row_number: int
    student_name: str
    college: str
    error_reason: str


@dataclass
class StudentRecord:
    """Validated student record ready for certificate rendering."""
    row_number: int
    student_name: str
    college: str
    course: str
    completion_date: str
    email: str
    certificate_id: str
    sanitized_name: str
    pdf_filename: str
    png_filename: str
    is_valid: bool = True
    error_message: Optional[str] = None


@dataclass
class ValidationResult:
    """Summary of batch parsing and validation."""
    valid_records: List[StudentRecord] = field(default_factory=list)
    invalid_records: List[ValidationError] = field(default_factory=list)
    total_rows: int = 0

    @property
    def valid_count(self) -> int:
        return len(self.valid_records)

    @property
    def invalid_count(self) -> int:
        return len(self.invalid_records)

    def to_dataframe(self) -> pd.DataFrame:
        """Converts valid records to a Pandas DataFrame for UI preview."""
        if not self.valid_records:
            return pd.DataFrame()
        return pd.DataFrame([
            {
                "Row #": r.row_number,
                "Certificate ID": r.certificate_id,
                "Student Name": r.student_name,
                "College": r.college,
                "Course": r.course,
                "Completion Date": r.completion_date,
                "Email": r.email,
                "PDF Filename": r.pdf_filename,
            }
            for r in self.valid_records
        ])

    def errors_dataframe(self) -> pd.DataFrame:
        """Converts invalid records to a Pandas DataFrame for UI error reporting."""
        if not self.invalid_records:
            return pd.DataFrame()
        return pd.DataFrame([
            {
                "Excel Row #": e.row_number,
                "Student Name": e.student_name or "(Blank)",
                "College": e.college or "(Blank)",
                "Rejection Reason": e.error_reason,
            }
            for e in self.invalid_records
        ])


def sanitize_filename(name: str) -> str:
    """
    Sanitize a student name to be safe across Windows and Linux filesystems.
    Removes forbidden characters, collapses spaces into underscores.
    """
    if not name:
        return "Student"
    # Remove characters illegal in Windows filenames: \ / : * ? " < > | and control chars
    clean = re.sub(r'[\\/*?:"<>|]', '', str(name))
    # Replace spaces and punctuation with underscores
    clean = re.sub(r'[\s\t\n]+', '_', clean)
    clean = re.sub(r'_+', '_', clean).strip('._ ')
    return clean if clean else "Student"


def format_date_flexible(
    date_val: Any,
    default_date_str: str = "08-Oct-2026"
) -> Tuple[str, bool, Optional[str]]:
    """
    Safely parse and format completion dates.
    Accepts datetime objects, pandas Timestamps, strings in various formats.
    Returns (formatted_date_string, is_valid, error_reason).
    """
    if pd.isna(date_val) or date_val is None:
        # If blank, fallback to UI default date if available
        if default_date_str and default_date_str.strip():
            return default_date_str.strip(), True, None
        return "", False, "Completion date is missing"

    # Already datetime
    if isinstance(date_val, (datetime.date, datetime.datetime, pd.Timestamp)):
        return date_val.strftime("%d-%b-%Y"), True, None

    date_str = str(date_val).strip()
    if not date_str:
        if default_date_str and default_date_str.strip():
            return default_date_str.strip(), True, None
        return "", False, "Completion date is empty"

    try:
        # If string starts with 4 digits (ISO format like YYYY-MM-DD or YYYY-MM-DD HH:MM:SS),
        # parse with yearfirst=True, dayfirst=False so that month is not mistakenly swapped with day.
        if re.match(r"^\d{4}[-/]\d{1,2}[-/]\d{1,2}", date_str):
            parsed = date_parser.parse(date_str, yearfirst=True, dayfirst=False)
        elif re.match(r"^\d{1,2}[-/]\d{1,2}[-/]\d{4}", date_str):
            parsed = date_parser.parse(date_str, dayfirst=True)
        else:
            parsed = date_parser.parse(date_str, dayfirst=True)
        return parsed.strftime("%d-%b-%Y"), True, None
    except Exception:
        # If strict parsing fails, check if default date can save it, otherwise report error
        return "", False, f"Invalid date format: '{date_str}'"


def _find_column(df: pd.DataFrame, candidates: List[str]) -> Optional[str]:
    """Find a column in the DataFrame by matching against a list of candidates (case-insensitive)."""
    norm_cols = {re.sub(r'[\s_]+', '', str(c)).lower(): c for c in df.columns}
    for candidate in candidates:
        norm_candidate = re.sub(r'[\s_]+', '', candidate).lower()
        if norm_candidate in norm_cols:
            return norm_cols[norm_candidate]
    return None


def read_data_file(file_or_path: Union[str, Path, BytesIO, Any]) -> pd.DataFrame:
    """
    Reads an uploaded Excel (.xlsx, .xls) or CSV file into a pandas DataFrame.
    Guarantees no execution of formulas or macro code.
    """
    if isinstance(file_or_path, (str, Path)):
        path = Path(file_or_path)
        if path.suffix.lower() == ".csv":
            df = pd.read_csv(path, dtype=str)
        else:
            df = pd.read_excel(path, dtype=str, engine="openpyxl")
    else:
        # Streamlit UploadedFile or BytesIO
        file_name = getattr(file_or_path, "name", "").lower()
        if file_name.endswith(".csv"):
            df = pd.read_csv(file_or_path, dtype=str)
        else:
            # Default to Excel reader with openpyxl
            try:
                df = pd.read_excel(file_or_path, dtype=str, engine="openpyxl")
            except Exception:
                # Rewind and attempt CSV in case user uploaded CSV with generic name
                if hasattr(file_or_path, "seek"):
                    file_or_path.seek(0)
                df = pd.read_csv(file_or_path, dtype=str)
    return df


def parse_and_validate_students(
    file_or_path: Any,
    default_course: str = config.COURSE_NAME_DEFAULT,
    default_completion_date: str = "08-Oct-2026",
    prefix: str = config.PREFIX_DEFAULT,
    start_number: int = config.START_NUMBER_DEFAULT,
) -> ValidationResult:
    """
    Ingests and validates student records from an Excel or CSV file.

    Features:
    - Flexible column matching for variations (e.g., 'Student Name', 'Name', 'FullName').
    - Strict validation: Name and College are mandatory.
    - Graceful error isolation (one bad row does not stop the batch).
    - Batch deduplication: detects duplicate student names in same college.
    - Zero-padded sequential Certificate ID generation.
    - Filename sanitization.
    """
    result = ValidationResult()

    try:
        df = read_data_file(file_or_path)
    except Exception as e:
        result.invalid_records.append(
            ValidationError(
                row_number=1,
                student_name="",
                college="",
                error_reason=f"Failed to read file: {str(e)}"
            )
        )
        return result

    result.total_rows = len(df)
    if result.total_rows == 0:
        result.invalid_records.append(
            ValidationError(
                row_number=1,
                student_name="",
                college="",
                error_reason="The uploaded file contains no data rows."
            )
        )
        return result

    # Identify column mappings
    col_name = _find_column(df, ["Student Name", "StudentName", "Name", "Full Name", "Candidate Name"])
    col_college = _find_column(df, ["College", "College Name", "Institution", "University", "College/University"])
    col_course = _find_column(df, ["Course", "Course Name", "Program", "Track"])
    col_date = _find_column(df, ["Completion Date", "CompletionDate", "Date", "Passing Date", "Issue Date"])
    col_email = _find_column(df, ["Email", "Email Address", "Student Email", "Mail"])

    if not col_name:
        result.invalid_records.append(
            ValidationError(
                row_number=1,
                student_name="",
                college="",
                error_reason="Missing required column: 'Student Name'. Expected columns: Student Name, College, Course, Completion Date, Email."
            )
        )
        return result

    if not col_college:
        result.invalid_records.append(
            ValidationError(
                row_number=1,
                student_name="",
                college="",
                error_reason="Missing required column: 'College'. Expected columns: Student Name, College, Course, Completion Date, Email."
            )
        )
        return result

    seen_students: Dict[Tuple[str, str], int] = {}
    current_id_number = start_number

    # Process each row (Excel rows are 1-indexed, with header as row 1, so data starts at row 2)
    for idx, row in df.iterrows():
        excel_row_num = int(idx) + 2

        # 1. Check for completely blank row
        if row.isna().all() or all(str(v).strip() == "" for v in row.values if not pd.isna(v)):
            result.invalid_records.append(
                ValidationError(
                    row_number=excel_row_num,
                    student_name="",
                    college="",
                    error_reason="Blank row detected (no data in row)."
                )
            )
            continue

        raw_name = row.get(col_name)
        raw_college = row.get(col_college)
        raw_course = row.get(col_course) if col_course else None
        raw_date = row.get(col_date) if col_date else None
        raw_email = row.get(col_email) if col_email else ""

        student_name = str(raw_name).strip() if pd.notna(raw_name) else ""
        college = str(raw_college).strip() if pd.notna(raw_college) else ""
        email = str(raw_email).strip() if pd.notna(raw_email) else ""

        # Validate Student Name
        if not student_name:
            result.invalid_records.append(
                ValidationError(
                    row_number=excel_row_num,
                    student_name="",
                    college=college,
                    error_reason="Student Name is mandatory and cannot be empty."
                )
            )
            continue

        # Validate College
        if not college:
            result.invalid_records.append(
                ValidationError(
                    row_number=excel_row_num,
                    student_name=student_name,
                    college="",
                    error_reason="College is mandatory and cannot be empty."
                )
            )
            continue

        # Determine Course
        if pd.notna(raw_course) and str(raw_course).strip():
            course = str(raw_course).strip()
        else:
            course = default_course.strip()

        if not course:
            result.invalid_records.append(
                ValidationError(
                    row_number=excel_row_num,
                    student_name=student_name,
                    college=college,
                    error_reason="Course name is mandatory (none provided in row or settings)."
                )
            )
            continue

        # Validate Completion Date
        comp_date, is_date_valid, date_err = format_date_flexible(raw_date, default_completion_date)
        if not is_date_valid:
            result.invalid_records.append(
                ValidationError(
                    row_number=excel_row_num,
                    student_name=student_name,
                    college=college,
                    error_reason=date_err or "Invalid completion date."
                )
            )
            continue

        # Check for duplicates within this batch
        dedup_key = (student_name.lower(), college.lower(), course.lower())
        if dedup_key in seen_students:
            first_row = seen_students[dedup_key]
            result.invalid_records.append(
                ValidationError(
                    row_number=excel_row_num,
                    student_name=student_name,
                    college=college,
                    error_reason=f"Duplicate entry: Student already registered in row {first_row}."
                )
            )
            continue
        seen_students[dedup_key] = excel_row_num

        # Generate unique Certificate ID (format: RAFAI-AI-2026-0001)
        certificate_id = f"{prefix.strip()}-{current_id_number:04d}"
        current_id_number += 1

        # Sanitize filename components
        clean_name = sanitize_filename(student_name)
        pdf_filename = f"{clean_name}_{certificate_id}.pdf"
        png_filename = f"{clean_name}_{certificate_id}.png"

        record = StudentRecord(
            row_number=excel_row_num,
            student_name=student_name,
            college=college,
            course=course,
            completion_date=comp_date,
            email=email,
            certificate_id=certificate_id,
            sanitized_name=clean_name,
            pdf_filename=pdf_filename,
            png_filename=png_filename,
            is_valid=True,
        )
        result.valid_records.append(record)

    return result


def create_sample_dataset(
    output_excel_path: Path,
    output_csv_path: Optional[Path] = None,
    num_students: int = 55,
    include_invalid: bool = False
) -> Tuple[Path, Optional[Path]]:
    """
    Creates a comprehensive realistic sample student dataset for RAFAI Technologies AI Foundation.
    Contains 50+ diverse college student records across major universities.
    Optionally includes controlled invalid rows to demonstrate validation reporting in UI.
    """
    first_names = [
        "Rahul", "Priya", "Aarav", "Ananya", "Rohan", "Sneha", "Vikram", "Neha",
        "Arjun", "Pooja", "Aditya", "Rhea", "Siddharth", "Kavya", "Tanmay",
        "Ishita", "Varun", "Meera", "Karan", "Shreya", "Nikhil", "Divya",
        "Gaurav", "Sanjana", "Harsh", "Simran", "Akash", "Ritu", "Manish",
        "Deepika", "Kunal", "Tanya", "Amit", "Swati", "Pranav", "Bhavna",
        "Dev", "Aishwarya", "Sachin", "Monika", "Ayush", "Payal", "Sameer",
        "Anjali", "Mayank", "Nisha", "Rajesh", "Kritika", "Suraj", "Pallavi",
        "Abhishek", "Sonali", "Tushar", "Preeti", "Mohit", "Rashmi"
    ]
    last_names = [
        "Sharma", "Patil", "Patel", "Iyer", "Verma", "Kulkarni", "Malhotra", "Reddy",
        "Nair", "Deshmukh", "Joshi", "Sen", "Chopra", "Gupta", "Mehta",
        "Bansal", "Rao", "Menon", "Kapoor", "Bhat", "Bose", "Saxena",
        "Garg", "Pillai", "Singhania", "Mishra", "Pandey", "Agarwal", "Shah",
        "Jain", "Trivedi", "Chavan", "Sood", "Dhar", "Hegde", "Ghosh"
    ]
    colleges = [
        "ABC College of Engineering",
        "XYZ Institute of Technology",
        "Veermata Jijabai Technological Institute (VJTI), Mumbai",
        "COEP Technological University, Pune",
        "MIT World Peace University, Pune",
        "BITS Pilani, Hyderabad Campus",
        "Indian Institute of Technology (IIT), Bombay",
        "RV College of Engineering, Bengaluru",
        "Delhi Technological University (DTU), New Delhi",
        "College of Engineering Guindy (Anna University), Chennai",
        "National Institute of Technology (NIT), Tiruchirappalli",
        "PES University, Bengaluru",
        "Symbiosis Institute of Technology, Pune",
        "Thadomal Shahani Engineering College, Mumbai",
        "Vellore Institute of Technology (VIT), Vellore",
    ]

    records = []
    total = max(num_students, 50)
    for i in range(total):
        fname = first_names[i % len(first_names)]
        lname = last_names[(i * 3 + 1) % len(last_names)]
        full_name = f"{fname} {lname}"
        college = colleges[i % len(colleges)]
        email = f"{fname.lower()}.{lname.lower()}{i+1}@example.com"
        records.append({
            config.COLUMN_STUDENT_NAME: full_name,
            config.COLUMN_COLLEGE: college,
            config.COLUMN_COURSE: "AI Foundation",
            config.COLUMN_COMPLETION_DATE: "08-Oct-2026",
            config.COLUMN_EMAIL: email,
        })

    if include_invalid:
        # Add intentional edge cases to test validation
        records.append({
            config.COLUMN_STUDENT_NAME: "",  # Missing student name
            config.COLUMN_COLLEGE: "Global Institute of Tech",
            config.COLUMN_COURSE: "AI Foundation",
            config.COLUMN_COMPLETION_DATE: "08-Oct-2026",
            config.COLUMN_EMAIL: "noname@example.com",
        })
        records.append({
            config.COLUMN_STUDENT_NAME: "Vikram Singhania",
            config.COLUMN_COLLEGE: "",  # Missing college
            config.COLUMN_COURSE: "AI Foundation",
            config.COLUMN_COMPLETION_DATE: "08-Oct-2026",
            config.COLUMN_EMAIL: "vikram@example.com",
        })
        records.append({
            config.COLUMN_STUDENT_NAME: "Rohan Verma",  # Duplicate of earlier student in same college
            config.COLUMN_COLLEGE: colleges[4 % len(colleges)],
            config.COLUMN_COURSE: "AI Foundation",
            config.COLUMN_COMPLETION_DATE: "08-Oct-2026",
            config.COLUMN_EMAIL: "rohan.duplicate@example.com",
        })
        records.append({
            config.COLUMN_STUDENT_NAME: "Aniket Deshpande",
            config.COLUMN_COLLEGE: "Modern College of Engineering",
            config.COLUMN_COURSE: "AI Foundation",
            config.COLUMN_COMPLETION_DATE: "invalid-date-99",  # Invalid date string
            config.COLUMN_EMAIL: "aniket@example.com",
        })

    df = pd.DataFrame(records)

    output_excel_path = Path(output_excel_path)
    output_excel_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_excel(output_excel_path, index=False, engine="openpyxl")

    if output_csv_path:
        output_csv_path = Path(output_csv_path)
        output_csv_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_csv_path, index=False)

    return output_excel_path, output_csv_path


if __name__ == "__main__":
    # Create sample datasets for immediate testing
    clean_excel = config.SAMPLE_DATA_DIR / "sample_students_ai_foundation.xlsx"
    clean_csv = config.SAMPLE_DATA_DIR / "sample_students_ai_foundation.csv"
    create_sample_dataset(clean_excel, clean_csv, num_students=52, include_invalid=False)

    test_invalid_excel = config.SAMPLE_DATA_DIR / "sample_students_with_errors.xlsx"
    create_sample_dataset(test_invalid_excel, num_students=50, include_invalid=True)
    print("Sample datasets created successfully in", config.SAMPLE_DATA_DIR)
