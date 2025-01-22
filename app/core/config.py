from decouple import config

class Settings:
    # Configuración de Base de Datos
    DB_USER: str = config("DB_USER")
    DB_PASSWORD: str = config("DB_PASSWORD")
    DB_SERVER: str = config("DB_SERVER")
    DB_NAME: str = config("DB_NAME")
    DB_DRIVER: str = config("DB_DRIVER", default="ODBC Driver 17 for SQL Server")

    DATABASE_URL: str = (
        f"mssql+pyodbc://{DB_USER}:{DB_PASSWORD}@{DB_SERVER}/{DB_NAME}?driver={DB_DRIVER}"
    )

    # 🔐 Configuración de Seguridad (Agregada)
    SECRET_KEY: str = config("SECRET_KEY", default="tu_clave_super_segura")
    ALGORITHM: str = config("ALGORITHM", default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = config("ACCESS_TOKEN_EXPIRE_MINUTES", default=30, cast=int)

settings = Settings()
