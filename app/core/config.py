from decouple import config

class Settings:
    DB_USER: str = config("DB_USER")
    DB_PASSWORD: str = config("DB_PASSWORD")
    DB_SERVER: str = config("DB_SERVER")
    DB_NAME: str = config("DB_NAME")
    DB_DRIVER: str = config("DB_DRIVER", default="ODBC Driver 17 for SQL Server")

    DATABASE_URL: str = (
        f"mssql+pyodbc://{DB_USER}:{DB_PASSWORD}@{DB_SERVER}/{DB_NAME}?driver={DB_DRIVER}"
    )

settings = Settings()
