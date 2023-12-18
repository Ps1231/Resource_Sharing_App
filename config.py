from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session, sessionmaker

DATABASE_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'rashi@2003',
    'db': 'resource',
    'charset': 'utf8mb4'
}

SECRET_KEY = 'your_secret_key_here'
DEBUG = True

# Include the correct port number in the connection string
# engine = create_engine("mysql+pymysql://root:rashi@2003@localhost/resource")


# base = automap_base()
# base.prepare(engine, reflect=True)
# Session = sessionmaker(bind=engine)
# session = Session()
