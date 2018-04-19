"""
        Build City Model

One for every hour of the day (12 time steps)
Empirical transition matrix (F):    Transition probability markov matrix
Travel time matrix (T):             Time from zone to zone
Rewards matrix (R):                 Earnings for trip between zone

May move to:
One for every hour of the day, for the seven days of the week (168 time steps)
"""

import sys
sys.path.insert(0, '../db/')

from connect import conn, cur
import numpy as np

#   Time units and cost ratio of distance (for the cost of the ride)
granularity = 10            # 10 minute intervals
N = int(1440 / granularity) # number of intervals
dist_cost = .2              # for estimating cost matrix

#   Number of zones
cur.execute("SELECT count(*) FROM zones WHERE city=%s", [1])
zones = cur.fetchone()[0]

#   Initialize matrices
count = np.zeros((N, zones, zones), dtype=int)
T = np.zeros((N, zones, zones))
R = np.zeros((N, zones, zones))
cost = np.zeros((N, zones, zones))

#   Get trips from db
i=0
cur.execute("""SELECT pickup_time, dropoff_time, pickup_location, dropoff_location, 
               total, trip_distance FROM taxi""")
for record in cur:
    #   Get hour and make index (hour, start location, end location)
    t = (6 * record[0].hour - 1) + int(record[0].minute/10)
    index = (t, record[2]-1, record[3]-1)

    #   Get trip time
    tripTime = record[1] - record[0]
    timeUnits = (tripTime.total_seconds() / 60) / granularity
    if(timeUnits < 0):      # Error in the data, don't add
        continue
    T[index] += timeUnits

    #   Get earnings
    R[index] += float(record[4])
    cost[index] += float(record[5]) * dist_cost     # cost has to be estimated as it wasn't given

    #   Increment count
    count[index] += 1

#   Printing to determine sparcity of matrices
if len(sys.argv) > 1 and sys.argv[1] == "verbose":
    total = zones**2
    print("Nonzero Elements: " + str(np.count_nonzero(count)) + "/" + str(N*total))

    for i in range(N):
        print("Hour " + str(i) + ": " + str(np.count_nonzero(count[i,:,:])/total))

    #   Print to see rides with loss (to see if dist_cost is too high)
    print((R < 0).sum())


#   Calculate probability of zone transfer
zoneRequests = count.sum(axis=2)[:,:,None]
zoneRequests[zoneRequests == 0] = 1     # To prevent divide by zero errors
F = count/zoneRequests

#   Average time
count[count == 0] = 1       # To prevent divide by zero errors
T = T / count
T = np.ceil(T)      # T needs to be in terms of discrete time units
T[T <= 0] = 2       # T > 0, need to find a better way to deal with sparcity
T = T.astype(np.int, copy=False)

#   Average reward
R = R / count
cost = cost / count
R -= cost

cur.close()
conn.close()
