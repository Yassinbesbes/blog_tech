# create_db.py
from app.database import Base, engine
from app import models  # This will import your User model

print("Creating database tables...")
Base.metadata.create_all(bind=engine)
print("Done.")
