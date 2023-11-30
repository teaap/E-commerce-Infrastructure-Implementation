import os

databaseUrl = os.environ["DATABASE_PRODAVNICA_URL"]


class Configuration():
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://root:root@{databaseUrl}/prodavnica"
    JWT_SECRET_KEY = "JWT_SECRET_KEY"
