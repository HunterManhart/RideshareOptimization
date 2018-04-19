"""
Add yellow taxi csv file to db
"""

#   Connect to db
from connect import conn, cur
import pandas as pd
from sys import argv

#   Check that a file name was passed
assert len(argv) > 1, "No file name was passed"

#   File
fileLoc = argv[1]

#   We only want certain indices in a certain order from our input data
def indexList(indices, list):
    return [ list[i] for i in indices ]

chunksize = 10 ** 5
for chunk in pd.read_csv(fileLoc, chunksize=chunksize, skiprows=[0,1]):
    data = [ indexList((1, 2, 3, 4, 7, 8, 10, 13, 14, 16), row) for row in (chunk.values.tolist()) ]
    print("Chunk formatted")

    values = b','.join(cur.mogrify("(1, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", row) for row in data)

    command = b"""INSERT INTO taxi (city_id, pickup_time, dropoff_time, passenger_count, 
                              trip_distance, pickup_location, dropoff_location, fare, 
                              tip, tolls, total) VALUES """ + values

    print("Executing insert")
    cur.execute(command)
    print("Insert finished")

conn.commit()
print("Taxi data committed successfully")

cur.close()
conn.close()