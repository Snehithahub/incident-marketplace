# seed.py
from database import engine, Base, SessionLocal
from models import Provider

def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    # Seed only if empty
    if db.query(Provider).count() == 0:
        providers = [
            Provider(name="Ramesh Kumar", category="farmer", phone="9876543210",
                     description="Fresh tomatoes and onions. Home delivery available.", location="Hyderabad"),
            Provider(name="Sita Devi", category="farmer", phone="7987654321",
                     description="Organic greens, limited stock.", location="Hyderabad"),
            Provider(name="Amit Sharma", category="plumber", phone="9123456780",
                     description="Pipe repair, 24/7 service.", location="Hyderabad"),
            Provider(name="Kavya Rao", category="caretaker", phone="7012345678",
                     description="Experienced caretaker for elderly, can help with meds.", location="Hyderabad")
        ]
        for p in providers:
            db.add(p)
        db.commit()
    db.close()

if __name__ == "__main__":
    init_db()
    print("Seeded DB (providers.db)")
