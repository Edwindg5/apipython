#app\dependencies.py
from fastapi import Depends
from app.database.connection import DatabaseConnection
import mysql.connector

def get_db():
    try:
        db = DatabaseConnection.get_connection()
        yield db
    finally:
        if db.is_connected():
            db.close()