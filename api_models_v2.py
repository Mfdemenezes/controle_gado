"""
Novos modelos Pydantic para v2.0 - Sistema Reprodutivo
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime

# ============================================================
# MODELOS: Raças
# ============================================================
class RacaBase(BaseModel):
    nome: str = Field(..., max_length=100)
    descricao: Optional[str] = None
    origem: Optional[str] = Field(None, max_length=100)
    caracteristicas: Optional[str] = None
    ativo: bool = True

class RacaCreate(RacaBase):
    pass

class RacaUpdate(BaseModel):
    nome: Optional[str] = Field(None, max_length=100)
    descricao: Optional[str] = None
    origem: Optional[str] = None
    caracteristicas: Optional[str] = None
    ativo: Optional[bool] = None

class Raca(RacaBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# ============================================================
# MODELOS: Lotes
# ============================================================
class LoteBase(BaseModel):
    nome: str = Field(..., max_length=100)
    descricao: Optional[str] = None
    capacidade: Optional[int] = None
    ativo: bool = True

class LoteCreate(LoteBase):
    pass

class Lote(LoteBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# ============================================================
# MODELOS: Pastos
# ============================================================
class PastoBase(BaseModel):
    nome: str = Field(..., max_length=100)
    area_hectares: Optional[float] = None
    tipo: Optional[str] = Field(None, max_length=50)
    descricao: Optional[str] = None
    ativo: bool = True

class PastoCreate(PastoBase):
    pass

class Pasto(PastoBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# ============================================================
# MODELOS: Touros
# ============================================================
class TouroBase(BaseModel):
    brinco: str = Field(..., max_length=50)
    nome: Optional[str] = Field(None, max_length=100)
    raca_id: Optional[int] = None
    data_nascimento: Optional[date] = None
    registro: Optional[str] = Field(None, max_length=100)
    linhagem: Optional[str] = None
    ativo: bool = True
    observacoes: Optional[str] = None

class TouroCreate(TouroBase):
    pass

class Touro(TouroBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# ============================================================
# MODELOS: Categorias
# ============================================================
class Categoria(BaseModel):
    id: int
    nome: str
    sexo: str
    idade_min_meses: int
    idade_max_meses: Optional[int]
    descricao: Optional[str]
    ordem: Optional[int]
    
    class Config:
        from_attributes = True

# ============================================================
# MODELOS: Eventos Reprodutivos
# ============================================================
class EventoReprodutivoBase(BaseModel):
    animal_id: int
    tipo_evento: str = Field(..., pattern="^(inseminacao|diagnostico_positivo|diagnostico_negativo|parto|aborto|cio)$")
    data_evento: date
    touro_id: Optional[int] = None
    bezerra_id: Optional[int] = None
    natimorto: bool = False
    observacoes: Optional[str] = None

class EventoReprodutivoCreate(EventoReprodutivoBase):
    pass

class EventoReprodutivo(EventoReprodutivoBase):
    id: int
    data_prevista: Optional[date]
    created_at: datetime
    
    class Config:
        from_attributes = True

# ============================================================
# MODELOS: Animal Atualizado
# ============================================================
class AnimalCreateV2(BaseModel):
    brinco: str = Field(..., max_length=50)
    nome: Optional[str] = Field(None, max_length=100)
    sexo: str = Field(..., pattern="^[MF]$")
    raca_id: Optional[int] = None
    data_nascimento: Optional[date] = None
    peso_atual: Optional[float] = None
    lote_id: Optional[int] = None
    pasto_id: Optional[int] = None
    mae_id: Optional[int] = None
    pai_id: Optional[int] = None
    observacoes: Optional[str] = None

class AnimalCompletoV2(BaseModel):
    id: int
    brinco: str
    nome: Optional[str]
    sexo: str
    data_nascimento: Optional[date]
    idade_meses: Optional[int]
    raca: Optional[str]
    categoria: Optional[str]
    peso_atual: Optional[float]
    lote: Optional[str]
    pasto: Optional[str]
    status_reprodutivo: Optional[str]
    foto_url: Optional[str]
    mae_brinco: Optional[str]
    pai_brinco: Optional[str]
    status: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

# ============================================================
# MODELOS: Estatísticas Reprodutivas
# ============================================================
class StatsReprodutivas(BaseModel):
    total_prenhas: int
    total_vazias: int
    total_inseminadas: int
    total_a_diagnosticar: int
    total_recem_paridas: int
    total_femeas_reprodutivas: int

# ============================================================
# MODELOS: Próximos Eventos
# ============================================================
class ProximoEvento(BaseModel):
    id: int
    brinco: str
    nome: Optional[str]
    tipo_evento: str
    data_evento: date
    data_prevista: Optional[date]
    dias_restantes: Optional[int]
    touro: Optional[str]
    
    class Config:
        from_attributes = True
