
from fastapi import FastAPI
from app.auth import routes as auth_routes
from app.blog import routes as blog_routes

app = FastAPI(title="Tech Blog API")

# Include auth and blog routes (we'll define them later)
app.include_router(auth_routes.router, prefix="/auth", tags=["Auth"])
app.include_router(blog_routes.router, prefix="/blogs", tags=["Blogs"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Tech Blog API!"}
