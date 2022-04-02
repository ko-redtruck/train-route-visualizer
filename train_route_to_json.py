from db_data import Journey, Trip,Station
import datetime
import sys
import json

if __name__ == "__main__":
    if len(sys.argv)<3:
        print("Usage: [start train station name] [destination station name] [optional: depature time %d.%m.%Y %H:%M | default: tomorrow 06:00]")
        sys.exit()
    start_station = Station(sys.argv[1])
    destination_station = Station(sys.argv[2])

    start_time = None
    if len(sys.argv) > 3:
        start_time_string = sys.argv[3]
        start_time = datetime.datetime.strptime(start_time_string,"%d.%m.%Y %H:%M")
    
    train_options = Trip(start_station,destination_station,start_time)
     
    data = [
        [[{
            "name" : station.name(),
            "time" : station.time(),
            "location" : station.location()

        } for station in train_connection]
            for train_connection in journey.all_stations()]
                for journey in train_options.journies()
    ]
    filename =  f"{start_station.db_name()}-{destination_station.db_name()}-train-trip.json"   
    with open(filename,"w") as file:
        file.write(json.dumps(data))
        print(f"Saved json data in {filename}")
        

