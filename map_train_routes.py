import folium
from db_data import Journey, Trip,Station
import datetime

def draw(train_journey,only_transfer_stations=False):
    map = folium.Map(location= train_journey.start_station().location())
    if only_transfer_stations == True:
        train_routes = train_journey.transfer_stations()
    else:
        train_routes = train_journey.all_stations()

    transfer_count = 0
    for train_route in train_routes:
        route_line_points = []
        for station in train_route:  
            route_line_points.append(tuple(station.location()))
        folium.PolyLine(route_line_points,color=["Red","Blue","Green","Black","White"][transfer_count%5]).add_to(map)
        
        for station in train_route:
            folium.Circle(
                radius=1000,
                location=station.location(),
                popup=station.name(),
                color="crimson",
                fill=True,
            ).add_to(map)

        transfer_count += 1
    
    map_filename = f"{train_journey.start_station().name()}-{train_journey.end_station().name()}.html"
    map.save(map_filename)
    return map_filename


if __name__ == "__main__":
    start_and_endpoint_is_not_confirmed = True

    while start_and_endpoint_is_not_confirmed:
        start_station_name = input("Start train station: ")
        destination_station_name = input("Destination train station: ")

        start_station = Station(start_station_name)
        destination_station = Station(destination_station_name)

        print("Found followning stations")
        print(f"- Start: {start_station.db_name()}")
        print(f"- Destination: {destination_station.db_name()}")
        confirmation = input("This is correct? (Y/n) ")
        if confirmation == "y" or confirmation == "":
            start_and_endpoint_is_not_confirmed = False

    start_time = None
    use_default_start_time = input("Earliest depature time: tomorrow at 06:00 (Y/n): ")
    custom_start_time_incorrect = True
    if use_default_start_time == "n":
        while custom_start_time_incorrect:
            start_time_string = input("Your depature time (%d.%m.%Y %H:%M): ")
            try:
                start_time = datetime.datetime.strptime(start_time_string,"%d.%m.%Y %H:%M")
                print(f"- Depature time: {start_time.strftime('%d.%m.%Y %H:%M')}")
                confirmation = input("This is correct? (Y/n) ")
                if confirmation == "y" or confirmation == "":
                    custom_start_time_incorrect = False
            except ValueError:
                print("ValueError: Wrong format. Please try again")

    train_trip = Trip(start_station,destination_station,start_time)
    options = train_trip.journies()
    print(f"Found {len(options)} possible routes for {train_trip.start_time()}")
    for i,journey in enumerate(options):
        print(f"- {i}: {journey.start_station().time()}-{journey.end_station().time()}, {journey.duration()}, {journey.changes()} changes, {journey.products()}")
    
    route_selection = int(input(f"Type 0-{len(train_trip.journies())-1} for which route to visualize: "))

    saved_map_filename = draw(train_trip.journies()[route_selection])
    print(f"Saved map in {saved_map_filename}")
        

