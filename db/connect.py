"""
Create a connection to the database

I considered using an ORM (SQLAlchemy) but it seems a bit over 
the top for what is currently a short-term project
"""

#   PostgreSQL driver
import psycopg2 as pg

#   Database connection
conn = pg.connect(database="rideshare")

#   Cursor to preform db operations
cur = conn.cursor()