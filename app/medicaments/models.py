"""Medicament database model."""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Text
from app.db.base import Base


class Medicament(Base):
    """Medicament model for pharmaceutical nomenclature."""
    
    __tablename__ = "medicaments"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Nomenclature fields
    n = Column(Integer, nullable=True)  # Numéro de ligne
    num_enregistrement = Column(String(100), nullable=True, index=True)
    code = Column(String(50), nullable=False, index=True)
    dci = Column(String(255), nullable=False, index=True)
    nom_marque = Column(String(255), nullable=False, index=True)
    forme = Column(String(255), nullable=False)
    dosage = Column(String(100), nullable=False)
    conditionnement = Column(String(100), nullable=False)
    liste = Column(String(50), nullable=True, index=True)
    p1 = Column(String(50), nullable=True)
    p2 = Column(String(50), nullable=True)
    obs = Column(Text, nullable=True)
    laboratoire = Column(String(255), nullable=False, index=True)
    pays_laboratoire = Column(String(100), nullable=False, index=True)
    date_enregistrement_initial = Column(Date, nullable=True)
    date_enregistrement_final = Column(Date, nullable=True)
    type_medicament = Column(String(50), nullable=False, index=True)
    statut = Column(String(10), nullable=False, index=True)
    duree_stabilite = Column(String(100), nullable=True)
    
    # Metadata fields
    version_nomenclature = Column(String(50), nullable=False, index=True)
    source_fichier = Column(String(255), nullable=True)
    deleted = Column(Boolean, default=False, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self) -> str:
        return f"<Medicament(id={self.id}, code={self.code}, dci={self.dci}, nom_marque={self.nom_marque})>"
