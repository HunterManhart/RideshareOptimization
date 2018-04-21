# Ride Sharing Optimizer

An implementation of the optimization, from this paper https://dl.acm.org/citation.cfm?id=3159721, on taxi or ride sharing routes from a driver's perspective.

## Getting Started

How to run on your local machine

### Prerequisites

You'll need Python3:
```
brew install postgres

```

And PostgreSQL:
```
brew install postgresql
brew tap homebrew/services
```

### Setting up the database

Starting from the home directory

Make the database:
```
createdb rideshare
```

Initialize the tables (and zones for NYC):
```
cd db/
python initDb.py
```

Add a data file to the database (The data files can )
```
python addYellow.py *file*
```

The files can be found here: http://www.nyc.gov/html/tlc/html/about/trip_record_data.shtml
And here's an example
```
python addYellow.py ../data/yellow/yellow_tripdata_2017-01.csv
```

Now move to the optimization folder, when database setup is complete
```
cd ../optimize/
```

### Examine Preprocessing

To see some results from the preprocessing:
```
python buildMatrices.py verbose
```

### Optimize

The matrices will need to be preprocess out of the database, but then will be cached.
To fresh calculate and optimize:
```
python driverOpt.py fresh
```

else just:
```
python driverOpt.py
```

To optimize with robust earnings (i.e. using nonlinear optimization to find a transition matrix within a confidence interval that minimizes earnings)
```
python driverOpt.py *?fresh* robust
```


## Known issues

The data obtained leads to rather sparse matrices, as I believe NYC increased their zones by a magnitude, but the data doesn't fill in those zones yet

The price and travel time matrices can be more accurate by leveraging Google Maps and Uber APIs

The nonlinear optimize doesn't appear to work under the current 3 constraints, likely due to SciPy, so a better constraint nonlin optimizer needs to be found and implemented.
