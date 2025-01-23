from fastapi import FastAPI
from app.middlewares.cors import setup_cors
from app.middlewares.logging import setup_logging
from app.apps.users.routers import router as users_router
from app.apps.locales.routers import router as locales_router

app = FastAPI()

# Configurar middlewares
setup_cors(app)
setup_logging(app)

# Registrar los routers
app.include_router(users_router)
app.include_router(locales_router)

@app.get("/")
def root():
    return {"message": "API Modular con FastAPI"}
