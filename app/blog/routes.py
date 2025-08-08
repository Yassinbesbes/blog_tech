from fastapi import APIRouter

router = APIRouter()

@router.get("/test-blog")
def test_blog():
    return {"message": "Blog route is working!"}
