# -*- coding: utf-8 -*-
"""
Created on Thu Jul  3 16:42:38 2025

@author: cleit
"""


# MAIN FILE  (FAST API) 

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from urllib.parse import quote_plus


# -------------BANCO DE DADOS-----------------#

#Acesso ao banco de dados
senha = quote_plus("Senha Mysql")
DATABASE_URL = f"mysql+pymysql://root:{senha}@localhost/boarding_system"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modelo do banco de dados
class PassengerDB(Base):
    __tablename__ = "passengers"
    id = Column(Integer, primary_key=True, index=True)
    NAME = Column(String(100), index=True)
    FLIGHT = Column(String(100), index=True)
    ORIGIN = Column(String(100))
    DESTINATION = Column(String(100))
    SEAT = Column(String(10))
    CHECKIN_STATUS = Column(Integer)  # 0 = Não feito, 1 = Feito

# Cria a tabela
Base.metadata.create_all(bind=engine)

# FASTAPI BACKEND
class Passenger(BaseModel):
    NAME: str
    FLIGHT: str
    ORIGIN: str
    DESTINATION: str
    SEAT: str

class PassengerResponse(Passenger):
    id: int
    CHECKIN_STATUS: int
    class Config:
        orm_mode = True

#Cria Api
app = FastAPI()

# Dependência de sessão
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Rotas
@app.post("/passengers", response_model=PassengerResponse)
def create_passenger(passenger: Passenger, db: Session = Depends(get_db)):
    db_passenger = PassengerDB(**passenger.dict(), CHECKIN_STATUS=0)
    db.add(db_passenger)
    try:
        db.commit()
        db.refresh(db_passenger)
        return db_passenger
    except:
        db.rollback()
        raise HTTPException(status_code=400, detail="Erro ao cadastrar passageiro.")

@app.get("/passengers", response_model=List[PassengerResponse])
def list_passengers(db: Session = Depends(get_db)):
    return db.query(PassengerDB).all()

@app.get("/passengers/{passenger_id}", response_model=PassengerResponse)
def get_passenger(passenger_id: int, db: Session = Depends(get_db)):
    passenger = db.query(PassengerDB).filter(PassengerDB.id == passenger_id).first()
    if not passenger:
        raise HTTPException(status_code=404, detail="Passageiro não encontrado.")
    return passenger

@app.post("/passengers/{passenger_id}/checkin")
def do_checkin(passenger_id: int, db: Session = Depends(get_db)):
    passenger = db.query(PassengerDB).filter(PassengerDB.id == passenger_id).first()
    if not passenger:
        raise HTTPException(status_code=404, detail="Passageiro não encontrado.")
    
    passenger.CHECKIN_STATUS = 1
    db.commit()
    return {"message": "Check-in realizado com sucesso!"}
