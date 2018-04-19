"""
            Initialize the tables in the database

Currently NYC is hardcoded into the initialization, as this is the only city for 
the scope of this project, but this can quickly be made dynamic (probably make a
zones folder with the zone files named New_York_City-1.csv, loop the dir, parse
the names into cities, put zones in)
"""

#   Connect to db
from connect import conn, cur
import csv

#   Create cities table (just doing NYC for project, but this can be easily extended to others)
cur.execute("""
    DROP TABLE IF EXISTS cities CASCADE;
    CREATE TABLE cities (id serial primary key,
                         city varchar(50) not null);
    INSERT INTO cities VALUES (1, 'New York');
    """)    # Caps doesn't matter for processing, I like this style for readability
print("Cities table created")

#   Create zone table from scratch (may want to make primary key into (borough, zone))
cur.execute("""
    DROP TABLE IF EXISTS zones CASCADE;
    CREATE TABLE zones (id serial primary key,
                        city integer REFERENCES cities(id),
                        borough varchar(50),
                        zone varchar(50),
                        service_zone varchar(50));
    """)
print("Zones table created")

#   Add NYC zones to table
zoneFile = "../data/nyc_zones.csv"
with open(zoneFile, 'r') as csvfile:
    reader = csv.reader(csvfile)
    next(reader)   # Skip first line
    for row in reader:
        cur.execute("INSERT INTO zones VALUES (%s, 1, %s, %s, %s)", row)
print("NYC zones added")

#   Create table with taxi data
cur.execute("""
    DROP TABLE IF EXISTS taxi CASCADE;
    CREATE TABLE taxi (id serial primary key,
                       city_id integer REFERENCES cities(id), 
                       pickup_time timestamp not null, 
                       dropoff_time timestamp not null,
                       passenger_count integer not null default 1,
                       trip_distance numeric(10,2),
                       pickup_location integer REFERENCES zones(id),
                       dropoff_location integer REFERENCES zones(id),
                       fare numeric(10,2) not null,
                       tip numeric(10,2) not null default 0,
                       tolls numeric(10,2) not null default 0,
                       total numeric(10,2) not null);
""")
print("Taxi table created")

conn.commit()

print("Changes commited successfully")

cur.close()
conn.close()