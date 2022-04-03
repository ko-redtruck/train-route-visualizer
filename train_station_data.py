import pandas as pd
import numpy as np
import time
df = pd.read_csv("train_stations.csv",sep=";")
from db_data import Station

def relative_error(v1,v2):
    return abs(v1-v2)/abs(v1) 

def n_nearst_train_stations(train_stations_df,lat,lng,n=10):
    train_station_df = train_stations_df.sub(lat,axis="latitude").sub(lng,axis="longitude")
    return train_station_df.nsmallest(n,["latitude","longitude"])
def filter_db_stations(row):
    
    
    MAX_ERROR = 0.001
    try:
        train_station = Station(row["name"])
        db_location = train_station.location()
        if relative_error(db_location[0],row["latitude"]) <= MAX_ERROR and relative_error(db_location[1],row["longitude"]) <= MAX_ERROR:
            print(f"TRUE: {row['name']}")
            return True
        else:
            print(f"FALSE LOCATION: {row['name']} | {train_station.db_name()}")
            return False
    except LookupError:
        print(f"FALSE LOOKUP: {row['name']}")
        return False
    except:
        print(f"ERROR ERROR: {row['name']}")
        return False

df = df[df.latitude.notnull() & df.longitude.notnull()]

m = df.apply(filter_db_stations, axis=1)
df = df[m]
print(df)

df.to_csv("train_stations_db_low_error.csv",sep=";")