import psycopg2
import os

def get_connection():
    return psycopg2.connect(
        host="db",
        database="sync_db",
        user="sync_user",
        password="sync_pass"
    )
