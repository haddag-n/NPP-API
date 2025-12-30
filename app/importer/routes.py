"""Import routes for nomenclature."""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from typing import Optional, List
import json

from app.importer.excel_parser import parse_excel_file, validate_medicament_record, get_available_sheets
from app.medicaments.models import Medicament
from app.models.import_log import ImportLog
from app.auth.models import User
from app.core.security import get_current_admin
from app.db.session import get_db
from pydantic import BaseModel

router = APIRouter(prefix="/import", tags=["Import"])


class SheetPreview(BaseModel):
    """Schema for sheet preview."""
    name: str
    rows: int
    detected_type: str
    columns: List[str]
    error: Optional[str] = None


class SheetsPreviewResponse(BaseModel):
    """Schema for sheets preview response."""
    filename: str
    sheets: List[SheetPreview]


class SheetImportResult(BaseModel):
    """Schema for single sheet import result."""
    rows_inserted: int
    rows_updated: int
    rows_ignored: int
    errors: List[dict]


class ImportResponse(BaseModel):
    """Schema for import response."""
    version_nomenclature: str
    source_fichier: str
    sheets_processed: dict[str, SheetImportResult]
    total_rows_inserted: int
    total_rows_updated: int
    available_sheets: List[str]


class ImportResult:
    """Container for import operation results."""
    
    def __init__(self, version: str, filename: str):
        self.version_nomenclature = version
        self.source_fichier = filename
        self.sheets_processed = {}
        self.available_sheets = []
    
    def add_sheet_result(self, sheet_name: str, inserted: int, updated: int, ignored: int, errors: list):
        """Add result for a sheet."""
        self.sheets_processed[sheet_name] = {
            "rows_inserted": inserted,
            "rows_updated": updated,
            "rows_ignored": ignored,
            "errors": errors
        }
    
    @property
    def total_rows_inserted(self) -> int:
        return sum(r["rows_inserted"] for r in self.sheets_processed.values())
    
    @property
    def total_rows_updated(self) -> int:
        return sum(r["rows_updated"] for r in self.sheets_processed.values())
    
    def to_dict(self):
        return {
            "version_nomenclature": self.version_nomenclature,
            "source_fichier": self.source_fichier,
            "sheets_processed": self.sheets_processed,
            "total_rows_inserted": self.total_rows_inserted,
            "total_rows_updated": self.total_rows_updated,
            "available_sheets": self.available_sheets
        }


@router.post("/sheets/preview", response_model=SheetsPreviewResponse)
async def preview_excel_sheets(
    file: UploadFile = File(..., description="Excel file to preview"),
    current_user: User = Depends(get_current_admin)  # Admin only
):
    """
    Preview available sheets in an Excel file without importing.
    
    Requires Admin role.
    
    Args:
        file: Excel file upload
        current_user: Current admin user
        
    Returns:
        SheetsPreviewResponse: List of available sheets with metadata
    """
    # Validate file type
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an Excel file (.xlsx or .xls)"
        )
    
    try:
        # Read file content
        file_content = await file.read()
        
        # Get sheet information
        sheets = get_available_sheets(file_content)
        
        return SheetsPreviewResponse(
            filename=file.filename,
            sheets=[SheetPreview(**sheet) for sheet in sheets]
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error reading file: {str(e)}"
        )


@router.post("/nomenclature")
async def import_nomenclature(
    file: UploadFile = File(..., description="Excel file containing nomenclature"),
    version: str = Form(..., description="Version of nomenclature (e.g., 2025-07-31)"),
    sheet_names: Optional[str] = Form(None, description="Comma-separated list of sheet names to import (empty = all sheets)"),
    remplacer_version: bool = Form(False, description="Replace existing version"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin)  # Admin only
):
    """
    Import nomenclature from Excel file (supports multi-sheet import).
    
    Requires Admin role.
    
    Args:
        file: Excel file upload
        version: Version identifier for this nomenclature
        sheet_names: Optional comma-separated list of sheet names to import
        remplacer_version: If True, soft delete existing entries with same version
        db: Database session
        current_user: Current admin user
        
    Returns:
        dict: Import results with counts and errors per sheet
    """
    # Validate file type
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an Excel file (.xlsx or .xls)"
        )
    
    # Parse sheet_names parameter
    sheets_to_import = None
    if sheet_names:
        sheets_to_import = [s.strip() for s in sheet_names.split(',') if s.strip()]
    
    # Create import log
    import_log = ImportLog(
        version_nomenclature=version,
        source_fichier=file.filename,
        start_time=datetime.utcnow()
    )
    db.add(import_log)
    await db.commit()
    
    result = ImportResult(version=version, filename=file.filename)
    
    try:
        # Read file content
        file_content = await file.read()
        
        # Get all available sheets
        available_sheets_info = get_available_sheets(file_content)
        result.available_sheets = [sheet["name"] for sheet in available_sheets_info]
        
        # Determine which sheets to process
        if sheets_to_import:
            # Validate specified sheets exist
            available_names = set(result.available_sheets)
            invalid_sheets = [s for s in sheets_to_import if s not in available_names]
            if invalid_sheets:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid sheet names: {', '.join(invalid_sheets)}. Available: {', '.join(result.available_sheets)}"
                )
            sheets_to_process = sheets_to_import
        else:
            # Process all sheets with type 'medicaments'
            sheets_to_process = [
                sheet["name"] for sheet in available_sheets_info 
                if sheet["detected_type"] == "medicaments"
            ]
            
            if not sheets_to_process:
                # If no medicament sheets detected, process all sheets
                sheets_to_process = result.available_sheets
        
        # If remplacer_version is True, soft delete existing entries
        if remplacer_version:
            update_result = await db.execute(
                select(Medicament).where(
                    Medicament.version_nomenclature == version,
                    Medicament.deleted == False
                )
            )
            existing_medicaments = update_result.scalars().all()
            for med in existing_medicaments:
                med.deleted = True
            await db.commit()
        
        # Process each sheet
        for sheet_name in sheets_to_process:
            sheet_inserted = 0
            sheet_updated = 0
            sheet_ignored = 0
            sheet_errors = []
            
            try:
                # Parse Excel sheet
                records = parse_excel_file(file_content, sheet_name=sheet_name)
                
                # Process each record
                for idx, record in enumerate(records, start=1):
                    try:
                        # Validate record
                        is_valid, validation_errors = validate_medicament_record(record)
                        if not is_valid:
                            sheet_errors.append({
                                "row": idx,
                                "message": "; ".join(validation_errors)
                            })
                            sheet_ignored += 1
                            continue
                        
                        # Add version and source file
                        record['version_nomenclature'] = version
                        record['source_fichier'] = file.filename
                        
                        # Check if medicament exists (by code and version)
                        existing = await db.execute(
                            select(Medicament).where(
                                Medicament.code == record['code'],
                                Medicament.version_nomenclature == version,
                                Medicament.deleted == False
                            )
                        )
                        existing_meds = existing.scalars().all()
                        
                        if len(existing_meds) > 1:
                            # Multiple records found - log as error and skip
                            sheet_errors.append({
                                "row": idx,
                                "message": f"Duplicate code '{record['code']}' found in database ({len(existing_meds)} entries). Skipping to avoid conflicts."
                            })
                            sheet_ignored += 1
                            continue
                        elif len(existing_meds) == 1:
                            # Update existing medicament
                            existing_med = existing_meds[0]
                            for key, value in record.items():
                                if key not in ['id', 'created_at']:
                                    setattr(existing_med, key, value)
                            sheet_updated += 1
                        else:
                            # Create new medicament
                            new_medicament = Medicament(**record)
                            db.add(new_medicament)
                            sheet_inserted += 1
                        
                        # Commit every 100 records to avoid memory issues
                        if (sheet_inserted + sheet_updated) % 100 == 0:
                            await db.commit()
                            
                    except Exception as e:
                        sheet_errors.append({
                            "row": idx,
                            "message": f"Error processing row: {str(e)}"
                        })
                        sheet_ignored += 1
                        continue
                
                # Final commit for this sheet
                await db.commit()
                
                # Add sheet result
                result.add_sheet_result(
                    sheet_name=sheet_name,
                    inserted=sheet_inserted,
                    updated=sheet_updated,
                    ignored=sheet_ignored,
                    errors=sheet_errors
                )
                
            except Exception as e:
                # Error processing entire sheet
                result.add_sheet_result(
                    sheet_name=sheet_name,
                    inserted=0,
                    updated=0,
                    ignored=0,
                    errors=[{"message": f"Failed to process sheet: {str(e)}"}]
                )
                continue
        
        # Update import log
        import_log.end_time = datetime.utcnow()
        import_log.rows_inserted = result.total_rows_inserted
        import_log.rows_updated = result.total_rows_updated
        import_log.rows_ignored = sum(r["rows_ignored"] for r in result.sheets_processed.values())
        
        # Combine all errors from all sheets
        all_errors = []
        for sheet_name, sheet_result in result.sheets_processed.items():
            for error in sheet_result["errors"]:
                all_errors.append({"sheet": sheet_name, **error})
        
        import_log.errors = json.dumps(all_errors) if all_errors else None
        await db.commit()
        
        return result.to_dict()
        
    except Exception as e:
        # Update import log with error
        import_log.end_time = datetime.utcnow()
        import_log.errors = json.dumps([{"message": str(e)}])
        await db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Import failed: {str(e)}"
        )


@router.get("/duplicates")
async def detect_duplicates(
    version: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    Detect duplicate codes in the database.
    
    Requires Admin role.
    
    Args:
        version: Optional version filter
        db: Database session
        current_user: Current admin user
        
    Returns:
        dict: List of duplicate codes with counts
    """
    from sqlalchemy import func
    
    # Build query
    query = select(
        Medicament.code,
        Medicament.version_nomenclature,
        func.count(Medicament.id).label('count')
    ).where(
        Medicament.deleted == False
    )
    
    if version:
        query = query.where(Medicament.version_nomenclature == version)
    
    query = query.group_by(
        Medicament.code,
        Medicament.version_nomenclature
    ).having(
        func.count(Medicament.id) > 1
    )
    
    result = await db.execute(query)
    duplicates = result.all()
    
    duplicates_list = [
        {
            "code": dup.code,
            "version": dup.version_nomenclature,
            "count": dup.count
        }
        for dup in duplicates
    ]
    
    return {
        "total_duplicates": len(duplicates_list),
        "duplicates": duplicates_list
    }


@router.post("/clean-duplicates")
async def clean_duplicates(
    version: Optional[str] = None,
    keep_strategy: str = "latest",  # "latest" or "first"
    dry_run: bool = True,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    Clean duplicate codes in the database by keeping only one entry.
    
    Requires Admin role.
    
    Args:
        version: Optional version filter
        keep_strategy: Which entry to keep - "latest" (newest created_at) or "first" (oldest created_at)
        dry_run: If True, only show what would be deleted without actually deleting
        db: Database session
        current_user: Current admin user
        
    Returns:
        dict: List of cleaned duplicates
    """
    if keep_strategy not in ["latest", "first"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="keep_strategy must be 'latest' or 'first'"
        )
    
    from sqlalchemy import func
    
    # Find duplicate codes
    dup_query = select(
        Medicament.code,
        Medicament.version_nomenclature,
        func.count(Medicament.id).label('count')
    ).where(
        Medicament.deleted == False
    )
    
    if version:
        dup_query = dup_query.where(Medicament.version_nomenclature == version)
    
    dup_query = dup_query.group_by(
        Medicament.code,
        Medicament.version_nomenclature
    ).having(
        func.count(Medicament.id) > 1
    )
    
    dup_result = await db.execute(dup_query)
    duplicates = dup_result.all()
    
    cleaned = []
    total_deleted = 0
    
    # Process each duplicate group
    for dup in duplicates:
        # Get all entries for this code/version
        entries_query = select(Medicament).where(
            Medicament.code == dup.code,
            Medicament.version_nomenclature == dup.version_nomenclature,
            Medicament.deleted == False
        ).order_by(
            Medicament.created_at.desc() if keep_strategy == "latest" else Medicament.created_at.asc()
        )
        
        entries_result = await db.execute(entries_query)
        entries = entries_result.scalars().all()
        
        if len(entries) > 1:
            # Keep first entry, mark others as deleted
            kept_entry = entries[0]
            deleted_entries = []
            
            for entry in entries[1:]:
                deleted_entries.append({
                    "id": entry.id,
                    "code": entry.code,
                    "dci": entry.dci,
                    "nom_marque": entry.nom_marque,
                    "created_at": entry.created_at.isoformat()
                })
                
                if not dry_run:
                    entry.deleted = True
                
                total_deleted += 1
            
            cleaned.append({
                "code": dup.code,
                "version": dup.version_nomenclature,
                "total_found": len(entries),
                "kept": {
                    "id": kept_entry.id,
                    "code": kept_entry.code,
                    "dci": kept_entry.dci,
                    "nom_marque": kept_entry.nom_marque,
                    "created_at": kept_entry.created_at.isoformat()
                },
                "deleted": deleted_entries
            })
    
    if not dry_run:
        await db.commit()
    
    return {
        "dry_run": dry_run,
        "keep_strategy": keep_strategy,
        "total_duplicate_groups": len(cleaned),
        "total_entries_deleted": total_deleted,
        "cleaned": cleaned
    }
