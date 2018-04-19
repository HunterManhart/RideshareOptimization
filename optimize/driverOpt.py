"""
        Build and Optimize Dirver Model

Three actions:
a0: Get Passenger
a1: Go Home
a2: Relocate
"""

import numpy as np
from scipy.optimize import minimize
from scipy.stats import chi2
from math import log
import sys
import resource

limit = sys.getrecursionlimit()

#   Cache matrices because they're computationally expensive
# python dirverOpt.py fresh  will recache them (or cache in the first place)
if len(sys.argv) > 1 and sys.argv[1] == "fresh":
    from buildMatrices import F, T, R, cost, count, N, zones
    #   Switch to saving dictionary of matrices later for extensibility
    np.save("./matrices/F", F)
    np.save("./matrices/T", T)
    np.save("./matrices/R", R)
    np.save("./matrices/cost", cost)
    np.save("./matrices/count", count)
    np.save("./matrices/extra", np.array([N, zones]))
    print("Matrices built")
else:
    F = np.load("./matrices/F.npy")
    T = np.load("./matrices/T.npy")
    R = np.load("./matrices/R.npy")
    cost = np.load("./matrices/cost.npy")
    count = np.load("./matrices/count.npy")
    N, zones = np.load("./matrices/extra.npy")
    print("Matrices got from cache")

B = 8*6
home = 10


def build_constraint(c, n, alpha):
    b_max = np.dot(c, np.log(c))
    f_inv = chi2.ppf((1-alpha), n-1)
    eq = (2*(b_max - n*log(n)) - f_inv) / 2

    return lambda p: np.dot(c, np.log(p)) - eq

#   Dynamic Progamming
def v(i, b, t):
    return np.array([ futureEarnings(j, b - T[t,i,j], t + T[t,i,j]) for j in range(zones) ])

earnings = np.full([zones, B, N], np.nan)
def futureEarnings(i, b, t):
    #   Out of time
    if b <= 0 or t >= N:
        return 0

    # print("i: " + str(i) + "   b: " + str(b) + "  t: " + str(t))

    #   Check cache
    if not np.isnan(earnings[i,b-1,t]):
        return earnings[i,b-1,t]

    #       Expected earnings from this zone 
    #   Robust Earnings (nonlinear minimization)
    exp = R[t,i,:] + v(i, b, t)
    objective = lambda p: np.dot( p, exp )
    count[count == 0] = 1
    constraint = build_constraint(count[t,i,:], zones, .9)

    con1 = {'type': 'eq', 'fun': constraint} 
    con2 = {'type': 'eq', 'fun': lambda p: np.sum(p) - 1} 
    con3 = {'type': 'ineq', 'fun': lambda p: p}
    cons = ([con1, con2, con3])
    solution = minimize(objective, F[t,i,:], constraints=cons)
    print(solution.x)
    a0 = solution.fun
    print(a0)

    #   Not robust earnings
    # a0 = np.dot( F[t,i,:], R[t,i,:] + v(i, b, t) )

    #       Go home and wait till later
    if i == home:
        a1 = futureEarnings(home, b, t + 1)
    else:
        a1 = -cost[t,i,home] + futureEarnings(home, b, t + T[t,i,home])

    #       Change zones
    a2 = max(( -cost[t,i,j] + futureEarnings(j, b - T[t,i,j], t + T[t,i,j]) for j in range(N) if (j!=home and j!=i) ))

    #   Cache and return
    earnings[i,b-1,t] = max(a0, a1, a2)
    return earnings[i,b-1,t]


#   Need to bottom-up calculate because python doesn't like recursion
for t in range(N-1, -1, -1):
    print("t: " + str(t) + " is finished")
    for b in range(B):
        for i in range(zones):
            futureEarnings(i, b+1, t)

e = futureEarnings(home, B, 0)

print(e)
