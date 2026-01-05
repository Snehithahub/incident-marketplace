# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import Provider
from kafka_producer import send_event
import seed

# Ensure DB and seed
Base.metadata.create_all(bind=engine)
seed.init_db()

app = FastAPI(title="Incident Marketplace Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ProviderCreate(BaseModel):
    name: str
    category: str
    phone: str
    description: Optional[str] = None
    location: Optional[str] = None

class ProviderOut(BaseModel):
    id: int
    name: str
    category: str
    phone_masked: str
    description: Optional[str]
    location: Optional[str]

    class Config:
        orm_mode = True

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def mask_phone(phone: str) -> str:
    # show first 2 and last 2 digits e.g., 98••••21
    if len(phone) < 4:
        return "****"
    return phone[:2] + "••••" + phone[-2:]

@app.get("/categories")
def categories():
    return ["farmer", "plumber", "caretaker", "electrician", "carpenter"]

@app.get("/providers", response_model=List[ProviderOut])
def list_providers(category: Optional[str] = None):
    db = SessionLocal()
    q = db.query(Provider)
    if category:
        q = q.filter(Provider.category == category)
    results = q.all()
    out = []
    for p in results:
        out.append(ProviderOut(
            id=p.id, name=p.name, category=p.category,
            phone_masked=mask_phone(p.phone),
            description=p.description, location=p.location
        ))
    db.close()
    return out

@app.post("/providers", response_model=ProviderOut)
def create_provider(item: ProviderCreate):
    db = SessionLocal()
    p = Provider(name=item.name, category=item.category, phone=item.phone,
                 description=item.description, location=item.location)
    db.add(p); db.commit(); db.refresh(p)
    out = ProviderOut(id=p.id, name=p.name, category=p.category,
                      phone_masked=mask_phone(p.phone),
                      description=p.description, location=p.location)
    db.close()
    return out

@app.post("/reveal/{provider_id}")
def reveal_number(provider_id: int):
    db = SessionLocal()
    p = db.query(Provider).filter(Provider.id == provider_id).first()
    if not p:
        db.close()
        raise HTTPException(status_code=404, detail="Provider not found")
    # Log reveal to Kafka
    send_event(event_type="reveal", provider_id=p.id, provider_name=p.name)
    # Return full phone to caller — frontend should display and show Call button
    db.close()
    return {"phone": p.phone}

@app.post("/call/{provider_id}")
def call(provider_id: int):
    db = SessionLocal()
    p = db.query(Provider).filter(Provider.id == provider_id).first()
    if not p:
        db.close()
        raise HTTPException(status_code=404, detail="Provider not found")
    send_event(event_type="call", provider_id=p.id, provider_name=p.name)
    db.close()
    return {"status": "ok"}
