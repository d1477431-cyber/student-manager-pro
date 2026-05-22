import os
import sqlite3
import json
import hashlib
import logging
from datetime import datetime
from contextlib import contextmanager

try:
    import mysql.connector
except ImportError:
    mysql = None

DATA_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(DATA_DIR, "etudiants.db")
DB_TYPE = os.getenv("DB_TYPE", "sqlite")

def get_db_p():
    return "%s" if DB_TYPE == "mysql" else "?"

DB_P = get_db_p()

def get_db_connection():
    if DB_TYPE == "mysql" and mysql:
        try:
            # Les paramètres devraient être chargés depuis des variables d'environnement en production
            return mysql.connector.connect(
                host=os.getenv("MYSQL_HOST", "localhost"),
                user=os.getenv("MYSQL_USER", "root"),
                password=os.getenv("MYSQL_PASSWORD", ""),
                database=os.getenv("MYSQL_DATABASE", "student_manager")
            )
        except Exception as e:
            logging.error(f"Erreur MySQL : {e}. Repli sur SQLite.")
    return sqlite3.connect(DB_PATH)

@contextmanager
def db_session():
    conn = get_db_connection()
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def hash_password(password):
    salt = "manager_pro_security_2026"
    return hashlib.sha256((password + salt).encode()).hexdigest()

def log_event(username, event, details=""):
    try:
        with db_session() as conn:
            cursor = conn.cursor()
            query = f"INSERT INTO logs (timestamp, event, username, details) VALUES ({DB_P}, {DB_P}, {DB_P}, {DB_P})"
            cursor.execute(query, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), event, username, details))
    except Exception as e:
        logging.error(f"Erreur log: {e}")

def setup_database():
    with db_session() as conn:
        cursor = conn.cursor()
        PK_TYPE = "VARCHAR(50) PRIMARY KEY" if DB_TYPE == "mysql" else "TEXT PRIMARY KEY"
        AI_TYPE = "INT AUTO_INCREMENT PRIMARY KEY" if DB_TYPE == "mysql" else "INTEGER PRIMARY KEY AUTOINCREMENT"
        REP_CMD = "REPLACE INTO" if DB_TYPE == "mysql" else "INSERT OR REPLACE INTO"

        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS etudiants (
                matricule {PK_TYPE},
                nom TEXT, prenom TEXT, age INTEGER, note TEXT,
                photo TEXT, date_ajout TEXT, email TEXT, telephone TEXT,
                statut TEXT DEFAULT 'Actif', filiere TEXT, niveau TEXT,
                frais_scolarite REAL DEFAULT 500000
            )
        """)

        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password_hash TEXT,
                role TEXT,
                theme TEXT DEFAULT 'dark'
            )
        """)

        # Utilisateurs par défaut
        defaults = [
            ("dodo", hash_password("dodo"), "Admin", 'dark'),
            ("sec", hash_password("sec123"), "Secrétaire", 'dark'),
            ("prof", hash_password("prof123"), "Professeur", 'dark')
        ]
        for u in defaults:
            cursor.execute(f"{REP_CMD} users (username, password_hash, role, theme) VALUES ({DB_P}, {DB_P}, {DB_P}, {DB_P})", u)

        cursor.execute(f"CREATE TABLE IF NOT EXISTS logs (id {AI_TYPE}, timestamp TEXT, event TEXT, username TEXT, details TEXT)")
        
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS paiements (
                id {AI_TYPE}, matricule TEXT, montant REAL, 
                date_paiement TEXT, type_paiement TEXT, commentaire TEXT,
                FOREIGN KEY (matricule) REFERENCES etudiants(matricule)
            )
        """)

        # Migrations automatiques pour les colonnes manquantes
        cols = [("email", "TEXT"), ("telephone", "TEXT"), ("statut", "TEXT DEFAULT 'Actif'"), 
                ("filiere", "TEXT"), ("niveau", "TEXT"), ("frais_scolarite", "REAL DEFAULT 500000")]
        for col, t in cols:
            try:
                cursor.execute(f"ALTER TABLE etudiants ADD COLUMN {col} {t}")
            except:
                pass