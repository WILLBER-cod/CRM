from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from . import models
from . import schemas
from .database import get_db, engine
from .services.distribution_service import DistributionService

# Создаем таблицы
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Lead Distribution CRM", version="1.0.0")

# Операторы
@app.post("/operators/", response_model=schemas.Operator)
def create_operator(operator: schemas.OperatorCreate, db: Session = Depends(get_db)):
    db_operator = models.Operator(**operator.dict())
    db.add(db_operator)
    db.commit()
    db.refresh(db_operator)
    return db_operator

@app.get("/operators/", response_model=List[schemas.Operator])
def read_operators(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    operators = db.query(models.Operator).offset(skip).limit(limit).all()
    return operators

@app.put("/operators/{operator_id}", response_model=schemas.Operator)
def update_operator(operator_id: int, operator: schemas.OperatorCreate, db: Session = Depends(get_db)):
    db_operator = db.query(models.Operator).filter(models.Operator.id == operator_id).first()
    if not db_operator:
        raise HTTPException(status_code=404, detail="Operator not found")
    
    for key, value in operator.dict().items():
        setattr(db_operator, key, value)
    
    db.commit()
    db.refresh(db_operator)
    return db_operator

# Источники
@app.post("/sources/", response_model=schemas.Source)
def create_source(source: schemas.SourceCreate, db: Session = Depends(get_db)):
    db_source = models.Source(**source.dict())
    db.add(db_source)
    db.commit()
    db.refresh(db_source)
    return db_source

@app.get("/sources/", response_model=List[schemas.Source])
def read_sources(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    sources = db.query(models.Source).offset(skip).limit(limit).all()
    return sources

# Настройка распределения
@app.post("/distribution/config/")
def set_distribution_config(config: schemas.DistributionConfig, db: Session = Depends(get_db)):
    # Удаляем старые настройки для этого источника
    db.query(models.OperatorSourceWeight).filter(
        models.OperatorSourceWeight.source_id == config.source_id
    ).delete()
    
    # Добавляем новые настройки
    for op_config in config.operators:
        weight = models.OperatorSourceWeight(**op_config.dict())
        db.add(weight)
    
    db.commit()
    return {"message": "Distribution configuration updated"}

# Обращения
@app.post("/contacts/", response_model=schemas.Contact)
def create_contact(contact: schemas.ContactCreate, db: Session = Depends(get_db)):
    contact_data = contact.dict()
    result_contact = DistributionService.distribute_contact(db, contact_data)
    return result_contact

@app.get("/contacts/", response_model=List[schemas.Contact])
def read_contacts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    contacts = db.query(models.Contact).offset(skip).limit(limit).all()
    return contacts

# Лиды
@app.get("/leads/", response_model=List[schemas.Lead])
def read_leads(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    leads = db.query(models.Lead).offset(skip).limit(limit).all()
    return leads

@app.get("/")
def read_root():
    return {"message": "Lead Distribution CRM API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
