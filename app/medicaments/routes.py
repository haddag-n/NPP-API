"""Medicaments routes."""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import date

from app.medicaments.schemas import (
    MedicamentOut,
    MedicamentCreate,
    MedicamentUpdate,
    PaginatedResponse,
    MedicamentStatistics
)
from app.medicaments import crud
from app.auth.models import User
from app.core.security import get_current_user, get_current_admin
from app.db.session import get_db

router = APIRouter(prefix="/medicaments", tags=["Medicaments"])


@router.get("", response_model=PaginatedResponse[MedicamentOut])
async def list_medicaments(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=200, description="Items per page"),
    q: Optional[str] = Query(None, description="Full-text search on DCI and nom_marque"),
    dci: Optional[str] = Query(None, description="Filter by DCI"),
    nom_marque: Optional[str] = Query(None, description="Filter by nom_marque"),
    code: Optional[str] = Query(None, description="Filter by code"),
    laboratoire: Optional[str] = Query(None, description="Filter by laboratoire"),
    pays_laboratoire: Optional[str] = Query(None, description="Filter by pays_laboratoire"),
    liste: Optional[str] = Query(None, description="Filter by liste"),
    type: Optional[str] = Query(None, alias="type", description="Filter by type_medicament"),
    statut: Optional[str] = Query(None, description="Filter by statut"),
    date_initial_min: Optional[date] = Query(None, description="Minimum date_enregistrement_initial"),
    date_initial_max: Optional[date] = Query(None, description="Maximum date_enregistrement_initial"),
    version: Optional[str] = Query(None, description="Filter by version_nomenclature"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List and search medicaments with pagination and filters.
    
    Requires authentication (Lecteur or Admin).
    """
    medicaments, total = await crud.get_medicaments(
        db=db,
        page=page,
        page_size=page_size,
        q=q,
        dci=dci,
        nom_marque=nom_marque,
        code=code,
        laboratoire=laboratoire,
        pays_laboratoire=pays_laboratoire,
        liste=liste,
        type_medicament=type,
        statut=statut,
        date_initial_min=date_initial_min,
        date_initial_max=date_initial_max,
        version=version
    )
    
    return PaginatedResponse(
        items=medicaments,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/statistiques", response_model=MedicamentStatistics)
async def get_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get medicament statistics.
    
    Requires authentication (Lecteur or Admin).
    """
    stats = await crud.get_statistics(db)
    return MedicamentStatistics(**stats)


@router.get("/{medicament_id}", response_model=MedicamentOut)
async def get_medicament(
    medicament_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific medicament by ID.
    
    Requires authentication (Lecteur or Admin).
    """
    medicament = await crud.get_medicament_by_id(db, medicament_id)
    if not medicament:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medicament not found"
        )
    return medicament


@router.post("", response_model=MedicamentOut, status_code=status.HTTP_201_CREATED)
async def create_medicament(
    medicament: MedicamentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin)  # Admin only
):
    """
    Create a new medicament.
    
    Requires Admin role.
    """
    return await crud.create_medicament(db, medicament)


@router.put("/{medicament_id}", response_model=MedicamentOut)
async def update_medicament(
    medicament_id: int,
    medicament_update: MedicamentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin)  # Admin only
):
    """
    Update a medicament.
    
    Requires Admin role.
    """
    medicament = await crud.update_medicament(db, medicament_id, medicament_update)
    if not medicament:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medicament not found"
        )
    return medicament


@router.delete("/{medicament_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_medicament(
    medicament_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin)  # Admin only
):
    """
    Delete a medicament (soft delete).
    
    Requires Admin role.
    """
    deleted = await crud.delete_medicament(db, medicament_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medicament not found"
        )
    return None
