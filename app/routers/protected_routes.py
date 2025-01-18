from fastapi import APIRouter, Depends
from app.middlewares.role_validation import role_required

router = APIRouter(
    prefix="/protected",
    tags=["Protected"]
)

@router.get("/staff", dependencies=[Depends(role_required("staff"))])
def staff_route():
    return {"message": "Bienvenido, usuario Staff"}
