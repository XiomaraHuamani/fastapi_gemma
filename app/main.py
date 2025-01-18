from fastapi import FastAPI
from app.db.connection import init_db
from app.routers import auth, protected_routes

app = FastAPI()

# Inicializar la base de datos
init_db()

# Registrar routers
app.include_router(auth.router)
app.include_router(protected_routes.router)

@app.get("/")
def root():
    return {"message": "¡Bienvenido a la API con login y autenticación!"}
