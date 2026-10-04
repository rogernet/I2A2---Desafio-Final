"""
storage.py - Persistência de dados em SQLite

Gerencia armazenamento de apólices extraídas, comparações e relatórios.
"""

import json
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any

import sqlalchemy as sa
from sqlalchemy import create_engine, Column, String, DateTime, JSON, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv

load_dotenv()

# === TIMEZONE BRT ===
BRT = timezone(timedelta(hours=-3))

def datetime_brt():
    """Retorna datetime atual em timezone BRT (Brasília)"""
    return datetime.now(BRT).replace(tzinfo=None)

# === CONFIG ===
BASE_DIR = Path(__file__).parent
DB_PATH = os.getenv("SQLITE_DB_PATH", "instance/apolices.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

# Criar diretório se não existir
Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# === MODELS ===
class PolicyExtraction(Base):
    """Apólice extraída de um PDF"""
    __tablename__ = "policy_extractions"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    file_hash = Column(String(64), unique=True, nullable=False)
    extracted_data = Column(JSON, nullable=False)
    raw_text = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime_brt, index=True)
    updated_at = Column(DateTime, default=datetime_brt, onupdate=datetime_brt)


class PolicyComparison(Base):
    """Resultado da comparação entre apólices"""
    __tablename__ = "policy_comparisons"
    
    id = Column(Integer, primary_key=True, index=True)
    policy1_id = Column(Integer, nullable=False)
    policy2_id = Column(Integer, nullable=False)
    comparison_result = Column(JSON, nullable=False)
    differences = Column(JSON, nullable=False)
    similarities = Column(JSON, nullable=True)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime_brt, index=True)


class ComparisonReport(Base):
    """Relatório executivo de comparação"""
    __tablename__ = "comparison_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    comparison_id = Column(Integer, nullable=False)
    summary = Column(Text, nullable=False)
    executive_summary = Column(Text, nullable=True)
    recommendations = Column(JSON, nullable=True)
    report_html = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime_brt, index=True)


# === INITIALIZATION ===
def init_db():
    """Cria as tabelas no banco de dados"""
    Base.metadata.create_all(bind=engine)
    print(f"✓ Database initialized at {DB_PATH}")


def get_db() -> Session:
    """Dependency injection para sessão do banco"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# === CRUD OPERATIONS ===
class PolicyStorage:
    """Interface de persistência para apólices"""
    
    @staticmethod
    def save_extraction(
        filename: str,
        file_hash: str,
        extracted_data: Dict[str, Any],
        raw_text: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> PolicyExtraction:
        """Salvar apólice extraída"""
        db = SessionLocal()
        try:
            # Verificar duplicata
            existing = db.query(PolicyExtraction).filter(
                PolicyExtraction.file_hash == file_hash
            ).first()
            
            if existing:
                return existing
            
            policy = PolicyExtraction(
                filename=filename,
                file_hash=file_hash,
                extracted_data=extracted_data,
                raw_text=raw_text,
                metadata=metadata or {}
            )
            db.add(policy)
            db.commit()
            db.refresh(policy)
            return policy
        finally:
            db.close()
    
    @staticmethod
    def get_extraction(policy_id: int) -> Optional[PolicyExtraction]:
        """Recuperar apólice extraída por ID"""
        db = SessionLocal()
        try:
            return db.query(PolicyExtraction).filter(
                PolicyExtraction.id == policy_id
            ).first()
        finally:
            db.close()
    
    @staticmethod
    def list_extractions() -> List[PolicyExtraction]:
        """Listar todas as apólices extraídas"""
        db = SessionLocal()
        try:
            return db.query(PolicyExtraction).order_by(
                PolicyExtraction.created_at.desc()
            ).all()
        finally:
            db.close()
    
    @staticmethod
    def delete_extraction(policy_id: int) -> bool:
        """Deletar apólice extraída"""
        db = SessionLocal()
        try:
            policy = db.query(PolicyExtraction).filter(
                PolicyExtraction.id == policy_id
            ).first()
            if policy:
                db.delete(policy)
                db.commit()
                return True
            return False
        finally:
            db.close()


class ComparisonStorage:
    """Interface de persistência para comparações"""
    
    @staticmethod
    def save_comparison(
        policy1_id: int,
        policy2_id: int,
        comparison_result: Dict[str, Any],
        differences: Dict[str, Any],
        similarities: Optional[Dict] = None,
        metadata: Optional[Dict] = None
    ) -> PolicyComparison:
        """Salvar resultado de comparação"""
        db = SessionLocal()
        try:
            comparison = PolicyComparison(
                policy1_id=policy1_id,
                policy2_id=policy2_id,
                comparison_result=comparison_result,
                differences=differences,
                similarities=similarities or {},
                metadata=metadata or {}
            )
            db.add(comparison)
            db.commit()
            db.refresh(comparison)
            return comparison
        finally:
            db.close()
    
    @staticmethod
    def get_comparison(comparison_id: int) -> Optional[PolicyComparison]:
        """Recuperar comparação por ID"""
        db = SessionLocal()
        try:
            return db.query(PolicyComparison).filter(
                PolicyComparison.id == comparison_id
            ).first()
        finally:
            db.close()
    
    @staticmethod
    def list_comparisons() -> List[PolicyComparison]:
        """Listar todas as comparações"""
        db = SessionLocal()
        try:
            return db.query(PolicyComparison).order_by(
                PolicyComparison.created_at.desc()
            ).all()
        finally:
            db.close()


class ReportStorage:
    """Interface de persistência para relatórios"""
    
    @staticmethod
    def save_report(
        comparison_id: int,
        summary: str,
        executive_summary: Optional[str] = None,
        recommendations: Optional[List] = None,
        report_html: Optional[str] = None
    ) -> ComparisonReport:
        """Salvar relatório de comparação"""
        db = SessionLocal()
        try:
            report = ComparisonReport(
                comparison_id=comparison_id,
                summary=summary,
                executive_summary=executive_summary,
                recommendations=recommendations or [],
                report_html=report_html
            )
            db.add(report)
            db.commit()
            db.refresh(report)
            return report
        finally:
            db.close()
    
    @staticmethod
    def get_report(report_id: int) -> Optional[ComparisonReport]:
        """Recuperar relatório por ID"""
        db = SessionLocal()
        try:
            return db.query(ComparisonReport).filter(
                ComparisonReport.id == report_id
            ).first()
        finally:
            db.close()
    
    @staticmethod
    def get_report_by_comparison(comparison_id: int) -> Optional[ComparisonReport]:
        """Recuperar relatório por ID de comparação"""
        db = SessionLocal()
        try:
            return db.query(ComparisonReport).filter(
                ComparisonReport.comparison_id == comparison_id
            ).first()
        finally:
            db.close()


if __name__ == "__main__":
    init_db()
