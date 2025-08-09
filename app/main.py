from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import firebase_admin
from firebase_admin import credentials, auth, firestore
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(dotenv_path="C:/Users/besbe/tech_blog/env/.env")

# Get Firebase credentials path
cred_path = os.getenv("FIREBASE_CRED_PATH")
if not cred_path:
    raise Exception("FIREBASE_CRED_PATH not found")

# Initialize Firebase app
cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred)

# Firestore client
db = firestore.client()

app = FastAPI()

# HTTP Bearer auth scheme to extract token from header
auth_scheme = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    """
    Verify Firebase ID token from Authorization header.
    Raise 401 if invalid.
    Return decoded token if valid.
    """
    token = credentials.credentials
    try:
        decoded = auth.verify_id_token(token)
        return decoded
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

@app.get("/")
def root():
    return {"message": "FastAPI + Firebase backend is running!"}

@app.get("/secure-data")
def secure_data(user=Depends(verify_token)):
    return {"message": f"Hello {user['uid']}, you are authenticated!"}

@app.post("/add-data")
def add_data(data: dict, user=Depends(verify_token)):
    # Save data to Firestore under user's document
    doc_ref = db.collection("users").document(user["uid"])
    doc_ref.set(data)
    return {"message": "Data saved successfully"}
