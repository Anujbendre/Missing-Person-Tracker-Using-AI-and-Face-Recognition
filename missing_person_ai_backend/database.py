import mysql.connector
from mysql.connector import pooling
from config import DB_CONFIG

# Create connection pool for faster database access
db_pool = pooling.MySQLConnectionPool(
    pool_name="missing_person_pool",
    pool_size=10,
    pool_reset_session=True,
    **DB_CONFIG
)

def get_db_connection():
    """Get connection from pool for faster access"""
    return db_pool.get_connection()
