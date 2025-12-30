"""ImportLog database model."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text
from app.db.base import Base


class ImportLog(Base):
    """ImportLog model for tracking nomenclature imports."""
    
    __tablename__ = "import_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    version_nomenclature = Column(String(50), nullable=False, index=True)
    source_fichier = Column(String(255), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    rows_inserted = Column(Integer, default=0, nullable=False)
    rows_updated = Column(Integer, default=0, nullable=False)
    rows_ignored = Column(Integer, default=0, nullable=False)
    errors = Column(Text, nullable=True)  # JSON string
    
    def __repr__(self) -> str:
        return f"<ImportLog(id={self.id}, version={self.version_nomenclature}, file={self.source_fichier})>"
