"""Excel file parser for nomenclature import."""
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import openpyxl
import pandas as pd
from io import BytesIO


def get_available_sheets(file_content: bytes) -> List[Dict[str, Any]]:
    """
    Get list of available sheets in Excel file with metadata.
    
    Args:
        file_content: Excel file content as bytes
        
    Returns:
        List[Dict[str, Any]]: List of sheet information
    """
    try:
        excel_file = pd.ExcelFile(BytesIO(file_content))
        sheets = []
        
        for sheet_name in excel_file.sheet_names:
            try:
                # Read first few rows to detect structure
                df = pd.read_excel(BytesIO(file_content), sheet_name=sheet_name, nrows=10)
                
                # Detect header row
                header_row = detect_header_row(BytesIO(file_content), sheet_name)
                
                # Read full sheet to get row count
                df_full = pd.read_excel(BytesIO(file_content), sheet_name=sheet_name, header=header_row)
                
                # Detect sheet type
                sheet_type = detect_sheet_type(df_full)
                
                sheets.append({
                    "name": sheet_name,
                    "rows": len(df_full),
                    "detected_type": sheet_type,
                    "columns": df_full.columns.tolist() if header_row is not None else []
                })
            except Exception as e:
                sheets.append({
                    "name": sheet_name,
                    "rows": 0,
                    "detected_type": "error",
                    "columns": [],
                    "error": str(e)
                })
        
        return sheets
    except Exception as e:
        raise ValueError(f"Error reading Excel file: {str(e)}")


def detect_header_row(file_content: bytes, sheet_name: str) -> Optional[int]:
    """
    Detect which row contains the header in an Excel sheet.
    Looks for rows containing key columns like 'N', 'CODE', 'DCI', etc.
    
    Args:
        file_content: Excel file content as bytes
        sheet_name: Name of the sheet
        
    Returns:
        Optional[int]: Row index of header, or None if not found
    """
    try:
        # Read first 20 rows without header
        df = pd.read_excel(BytesIO(file_content), sheet_name=sheet_name, header=None, nrows=20)
        
        # Key columns to look for (case-insensitive)
        key_columns = ['N', 'CODE', 'DCI', 'DENOMINATION COMMUNE INTERNATIONALE', 'NOM DE MARQUE']
        
        for idx, row in df.iterrows():
            # Convert row to uppercase strings for comparison
            row_values = [str(val).strip().upper() for val in row if pd.notna(val)]
            
            # Check if this row contains at least 2 key columns
            matches = sum(1 for key in key_columns if any(key in val for val in row_values))
            
            if matches >= 2:
                return idx
        
        # Default to row 0 if not found
        return 0
    except Exception:
        return 0


def detect_sheet_type(df: pd.DataFrame) -> str:
    """
    Detect the type of data in a sheet based on column names.
    
    Args:
        df: DataFrame to analyze
        
    Returns:
        str: Type of sheet ('medicaments', 'unknown')
    """
    columns_str = ' '.join([str(col).upper() for col in df.columns])
    
    # Check for medicaments sheet
    medicament_indicators = ['CODE', 'DCI', 'DENOMINATION COMMUNE', 'NOM DE MARQUE', 'MARQUE']
    
    matches = sum(1 for indicator in medicament_indicators if indicator in columns_str)
    
    if matches >= 2:
        return "medicaments"
    
    return "unknown"


def parse_excel_file(file_content: bytes, sheet_name: str = None) -> List[Dict[str, Any]]:
    """
    Parse Excel file and extract medicament data from a specific sheet.
    
    Args:
        file_content: Excel file content as bytes
        sheet_name: Sheet name to parse (default: None = first sheet)
        
    Returns:
        List[Dict[str, Any]]: List of medicament dictionaries
        
    Raises:
        ValueError: If file format is invalid
    """
    try:
        # Detect header row
        if sheet_name is None:
            excel_file = pd.ExcelFile(BytesIO(file_content))
            sheet_name = excel_file.sheet_names[0]
        
        header_row = detect_header_row(file_content, sheet_name)
        
        # Read Excel file using pandas with detected header
        df = pd.read_excel(BytesIO(file_content), sheet_name=sheet_name, header=header_row)
        
        # Column mapping from Excel to database fields (case-insensitive)
        # Normalize column names to handle variations
        df.columns = df.columns.str.strip()
        
        # Flexible column mapping with multiple possible names
        column_mapping = {}
        for col in df.columns:
            col_upper = col.upper().strip()
            
            if col_upper in ['N', 'N°']:
                column_mapping[col] = 'n'
            elif 'ENREGISTREMENT' in col_upper and 'N°' in col_upper:
                column_mapping[col] = 'num_enregistrement'
            elif col_upper in ['CODE', 'CODE PRODUIT']:
                column_mapping[col] = 'code'
            elif 'DCI' in col_upper or 'DENOMINATION COMMUNE' in col_upper:
                column_mapping[col] = 'dci'
            elif 'NOM' in col_upper and 'MARQUE' in col_upper:
                column_mapping[col] = 'nom_marque'
            elif col_upper in ['FORME', 'FORME PHARMACEUTIQUE'] or (col_upper == 'FORME'):
                column_mapping[col] = 'forme'
            elif col_upper in ['DOSAGE', 'TITRE']:
                column_mapping[col] = 'dosage'
            elif 'CONDITIONNEMENT' in col_upper or 'PRÉSENTATION' in col_upper:
                column_mapping[col] = 'conditionnement'
            elif col_upper == 'LISTE':
                column_mapping[col] = 'liste'
            elif col_upper == 'P1':
                column_mapping[col] = 'p1'
            elif col_upper == 'P2':
                column_mapping[col] = 'p2'
            elif col_upper == 'OBS' or col_upper == 'OBSERVATION' or col_upper == 'OBSERVATIONS':
                column_mapping[col] = 'obs'
            elif 'LABORATOIRE' in col_upper and 'PAYS' not in col_upper:
                column_mapping[col] = 'laboratoire'
            elif 'PAYS' in col_upper and 'LABORATOIRE' in col_upper:
                column_mapping[col] = 'pays_laboratoire'
            elif 'DATE' in col_upper and 'INITIAL' in col_upper:
                column_mapping[col] = 'date_enregistrement_initial'
            elif 'DATE' in col_upper and ('FINAL' in col_upper or 'VALIDITÉ' in col_upper):
                column_mapping[col] = 'date_enregistrement_final'
            elif col_upper in ['TYPE', 'TYPE MEDICAMENT']:
                column_mapping[col] = 'type_medicament'
            elif col_upper == 'STATUT' or col_upper == 'ÉTAT':
                column_mapping[col] = 'statut'
            elif ('STABILITE' in col_upper or 'STABILITÉ' in col_upper) and ('DUREE' in col_upper or 'DURÉE' in col_upper):
                column_mapping[col] = 'duree_stabilite'
        
        # Rename columns according to mapping
        df = df.rename(columns=column_mapping)
        
        # Remove completely empty rows
        df = df.dropna(how='all')
        
        # Convert DataFrame to list of dictionaries
        records = []
        # Get all mapped fields
        mapped_fields = set(column_mapping.values())
        
        for _, row in df.iterrows():
            record = {}
            
            for db_field in mapped_fields:
                value = row.get(db_field)
                
                # Handle NaN values
                if pd.isna(value):
                    record[db_field] = None
                # Handle date fields
                elif db_field in ['date_enregistrement_initial', 'date_enregistrement_final']:
                    if isinstance(value, (datetime, pd.Timestamp)):
                        record[db_field] = value.date()
                    else:
                        record[db_field] = None
                # Handle integer fields
                elif db_field == 'n':
                    try:
                        record[db_field] = int(value) if value is not None else None
                    except (ValueError, TypeError):
                        record[db_field] = None
                # Handle string fields
                else:
                    record[db_field] = str(value).strip() if value is not None else None
            
            records.append(record)
        
        return records
        
    except Exception as e:
        raise ValueError(f"Error parsing Excel file: {str(e)}")


def validate_medicament_record(record: Dict[str, Any]) -> tuple[bool, List[str]]:
    """
    Validate a medicament record.
    
    Args:
        record: Medicament record dictionary
        
    Returns:
        tuple[bool, List[str]]: (is_valid, list of error messages)
    """
    errors = []
    
    # Only code is truly required (unique identifier)
    if not record.get('code'):
        errors.append("Missing required field: code")
        return False, errors
    
    # Set default value "ND" for all missing string fields
    default_fields = [
        'dci', 'nom_marque', 'forme', 'dosage',
        'conditionnement', 'laboratoire', 'pays_laboratoire',
        'type_medicament', 'statut'
    ]
    
    for field in default_fields:
        if not record.get(field):
            record[field] = 'ND'
    
    # Field length validation
    max_lengths = {
        'code': 50,
        'dci': 255,
        'nom_marque': 255,
        'forme': 255,
        'laboratoire': 255,
        'pays_laboratoire': 100
    }
    
    for field, max_length in max_lengths.items():
        value = record.get(field)
        if value and len(str(value)) > max_length:
            errors.append(f"Field {field} exceeds maximum length of {max_length}")
    
    is_valid = len(errors) == 0
    return is_valid, errors
