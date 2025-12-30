"""Pydantic schemas for Medicament model."""
from pydantic import BaseModel, ConfigDict
from datetime import datetime, date
from typing import Optional, List, Generic, TypeVar


class MedicamentBase(BaseModel):
    """Base Medicament schema."""
    n: Optional[int] = None
    num_enregistrement: Optional[str] = None
    code: str
    dci: str
    nom_marque: str
    forme: str
    dosage: str
    conditionnement: str
    liste: Optional[str] = None
    p1: Optional[str] = None
    p2: Optional[str] = None
    obs: Optional[str] = None
    laboratoire: str
    pays_laboratoire: str
    date_enregistrement_initial: Optional[date] = None
    date_enregistrement_final: Optional[date] = None
    type_medicament: str
    statut: str
    duree_stabilite: Optional[str] = None
    version_nomenclature: str


class MedicamentCreate(MedicamentBase):
    """Schema for creating a new medicament."""
    pass


class MedicamentUpdate(BaseModel):
    """Schema for updating a medicament."""
    n: Optional[int] = None
    num_enregistrement: Optional[str] = None
    code: Optional[str] = None
    dci: Optional[str] = None
    nom_marque: Optional[str] = None
    forme: Optional[str] = None
    dosage: Optional[str] = None
    conditionnement: Optional[str] = None
    liste: Optional[str] = None
    p1: Optional[str] = None
    p2: Optional[str] = None
    obs: Optional[str] = None
    laboratoire: Optional[str] = None
    pays_laboratoire: Optional[str] = None
    date_enregistrement_initial: Optional[date] = None
    date_enregistrement_final: Optional[date] = None
    type_medicament: Optional[str] = None
    statut: Optional[str] = None
    duree_stabilite: Optional[str] = None
    version_nomenclature: Optional[str] = None


class MedicamentOut(MedicamentBase):
    """Schema for medicament output."""
    id: int
    source_fichier: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


T = TypeVar('T')


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response schema."""
    items: List[T]
    total: int
    page: int
    page_size: int


class MedicamentStatistics(BaseModel):
    """Schema for medicament statistics."""
    par_laboratoire: dict[str, int]
    par_pays: dict[str, int]
    par_type: dict[str, int]
