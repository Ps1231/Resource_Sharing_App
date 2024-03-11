import pymysql
DATABASE_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'rashi@2003',
    'db': 'resource1',
    'charset': 'utf8mb4'
}

SECRET_KEY = 'your_secret_key_here'
DEBUG = True
db = pymysql.connect(**DATABASE_CONFIG, cursorclass=pymysql.cursors.DictCursor)
