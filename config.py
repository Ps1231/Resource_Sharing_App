from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session, sessionmaker

DATABASE_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'rashi@2003',
    'db': 'resource1',
    'charset': 'utf8mb4'
}

SECRET_KEY = 'your_secret_key_here'
DEBUG = True
