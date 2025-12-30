"""CRUD operations for Medicament model."""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from datetime import date

from app.medicaments.models import Medicament
from app.medicaments.schemas import MedicamentCreate, MedicamentUpdate


async def get_medicament_by_id(db: AsyncSession, medicament_id: int) -> Optional[Medicament]:
    """
    Get a medicament by ID (excluding deleted ones).
    
    Args:
        db: Database session
        medicament_id: Medicament ID
        
    Returns:
        Optional[Medicament]: Medicament or None
    """
    result = await db.execute(
        select(Medicament).where(
            and_(
                Medicament.id == medicament_id,
                Medicament.deleted == False
            )
        )
    )
    return result.scalar_one_or_none()


async def get_medicaments(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 50,
    q: Optional[str] = None,
    dci: Optional[str] = None,
    nom_marque: Optional[str] = None,
    code: Optional[str] = None,
    laboratoire: Optional[str] = None,
    pays_laboratoire: Optional[str] = None,
    liste: Optional[str] = None,
    type_medicament: Optional[str] = None,
    statut: Optional[str] = None,
    date_initial_min: Optional[date] = None,
    date_initial_max: Optional[date] = None,
    version: Optional[str] = None
) -> tuple[List[Medicament], int]:
    """
    Get paginated and filtered list of medicaments.
    
    Args:
        db: Database session
        page: Page number (1-indexed)
        page_size: Items per page
        q: Full-text search on DCI and nom_marque
        dci: Filter by DCI
        nom_marque: Filter by nom_marque
        code: Filter by code
        laboratoire: Filter by laboratoire
        pays_laboratoire: Filter by pays_laboratoire
        liste: Filter by liste
        type_medicament: Filter by type_medicament
        statut: Filter by statut
        date_initial_min: Minimum date_enregistrement_initial
        date_initial_max: Maximum date_enregistrement_initial
        version: Filter by version_nomenclature
        
    Returns:
        tuple[List[Medicament], int]: List of medicaments and total count
    """
    # Base query - exclude deleted
    query = select(Medicament).where(Medicament.deleted == False)
    
    # Apply filters
    if q:
        search_pattern = f"%{q}%"
        query = query.where(
            or_(
                Medicament.dci.ilike(search_pattern),
                Medicament.nom_marque.ilike(search_pattern)
            )
        )
    
    if dci:
        query = query.where(Medicament.dci.ilike(f"%{dci}%"))
    
    if nom_marque:
        query = query.where(Medicament.nom_marque.ilike(f"%{nom_marque}%"))
    
    if code:
        query = query.where(Medicament.code.ilike(f"%{code}%"))
    
    if laboratoire:
        query = query.where(Medicament.laboratoire.ilike(f"%{laboratoire}%"))
    
    if pays_laboratoire:
        query = query.where(Medicament.pays_laboratoire.ilike(f"%{pays_laboratoire}%"))
    
    if liste:
        query = query.where(Medicament.liste == liste)
    
    if type_medicament:
        query = query.where(Medicament.type_medicament == type_medicament)
    
    if statut:
        query = query.where(Medicament.statut == statut)
    
    if date_initial_min:
        query = query.where(Medicament.date_enregistrement_initial >= date_initial_min)
    
    if date_initial_max:
        query = query.where(Medicament.date_enregistrement_initial <= date_initial_max)
    
    if version:
        query = query.where(Medicament.version_nomenclature == version)
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    
    # Execute query
    result = await db.execute(query)
    medicaments = result.scalars().all()
    
    return list(medicaments), total


async def create_medicament(db: AsyncSession, medicament: MedicamentCreate) -> Medicament:
    """
    Create a new medicament.
    
    Args:
        db: Database session
        medicament: Medicament data
        
    Returns:
        Medicament: Created medicament
    """
    db_medicament = Medicament(**medicament.model_dump())
    db.add(db_medicament)
    await db.commit()
    await db.refresh(db_medicament)
    return db_medicament


async def update_medicament(
    db: AsyncSession,
    medicament_id: int,
    medicament_update: MedicamentUpdate
) -> Optional[Medicament]:
    """
    Update a medicament.
    
    Args:
        db: Database session
        medicament_id: Medicament ID
        medicament_update: Update data
        
    Returns:
        Optional[Medicament]: Updated medicament or None
    """
    db_medicament = await get_medicament_by_id(db, medicament_id)
    if not db_medicament:
        return None
    
    # Update fields
    update_data = medicament_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_medicament, field, value)
    
    await db.commit()
    await db.refresh(db_medicament)
    return db_medicament


async def delete_medicament(db: AsyncSession, medicament_id: int) -> bool:
    """
    Soft delete a medicament (set deleted = True).
    
    Args:
        db: Database session
        medicament_id: Medicament ID
        
    Returns:
        bool: True if deleted, False if not found
    """
    db_medicament = await get_medicament_by_id(db, medicament_id)
    if not db_medicament:
        return False
    
    db_medicament.deleted = True
    await db.commit()
    return True


async def get_statistics(db: AsyncSession) -> dict:
    """
    Get medicament statistics.
    
    Args:
        db: Database session
        
    Returns:
        dict: Statistics grouped by laboratory, country, and type
    """
    # Count by laboratoire
    lab_query = select(
        Medicament.laboratoire,
        func.count(Medicament.id).label('count')
    ).where(Medicament.deleted == False).group_by(Medicament.laboratoire)
    lab_result = await db.execute(lab_query)
    par_laboratoire = {row[0]: row[1] for row in lab_result.all()}
    
    # Count by pays
    pays_query = select(
        Medicament.pays_laboratoire,
        func.count(Medicament.id).label('count')
    ).where(Medicament.deleted == False).group_by(Medicament.pays_laboratoire)
    pays_result = await db.execute(pays_query)
    par_pays = {row[0]: row[1] for row in pays_result.all()}
    
    # Count by type
    type_query = select(
        Medicament.type_medicament,
        func.count(Medicament.id).label('count')
    ).where(Medicament.deleted == False).group_by(Medicament.type_medicament)
    type_result = await db.execute(type_query)
    par_type = {row[0]: row[1] for row in type_result.all()}
    
    return {
        "par_laboratoire": par_laboratoire,
        "par_pays": par_pays,
        "par_type": par_type
    }
