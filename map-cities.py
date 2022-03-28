import folium
import geocoder
import sys
import os
import random
from soup import Trip,Station
COUNTRY = 'Germany'
MAPBOX_ACCESS_TOKEN_ENV_VARIABLE = "MAPBOX_ACCESS_TOKEN"
#dirty name changes to improve quality
def _transform_city_name(city_name):
    if " Ville" in city_name:
        return city_name.replace(" Ville","") + " " + COUNTRY
    if "Villefranche-s-Saone" == city_name:
        return "Villefranche-sur-Saône, Rhône, France"
    
    return city_name + " " + COUNTRY

def _get_geo_location_from_raw(city_name,previous_location=None):
    if previous_location == None:
        return geocoder.mapbox(city_name)
    else:
        return geocoder.mapbox(city_name,proximity=previous_location)

def get_geo_location_from(city_name,previous_location=None):
    g  = _get_geo_location_from_raw(_transform_city_name(city_name),previous_location)
    if g.ok:
        return g
    else:
        return None

def __random_hex_color():
    return ["Red","Blue","Green","Black","White"][random.randint(0,4)]

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
            folium.Circle(
                radius=1000,
                location=station.location(),
                popup=station.name(),
                color="crimson",
                fill=True,
            ).add_to(map)

            route_line_points.append(tuple(station.location()))
        folium.PolyLine(route_line_points,color=["Red","Blue","Green","Black","White"][transfer_count%5]).add_to(map)
        transfer_count += 1
    map.save(f"{train_journey.start_station().name()}-{train_journey.end_station().name()}.html")


def draw_map_from(cities_names):
    previous_location = None
    g_cities = []
    for city_name in cities_names:
        g_city = get_geo_location_from(city_name,previous_location)
        if g_city is not None:
            print(f"Adding: {g_city.address} for {city_name}")
            g_cities.append(g_city)
            previous_location = [g_city.lat,g_city.lng]

    g_first_city = g_cities[0]
    m = folium.Map(location=[g_first_city.lat,g_first_city.lng])

    for g_city in g_cities:
        folium.Circle(
            radius=1000,
            location=[g_city.lat,g_city.lng],
            popup=g_city.address,
            color="crimson",
            fill=True,
        ).add_to(m)

    points = [tuple([float(g_city.lat),float(g_city.lng)]) for g_city in g_cities]

    folium.PolyLine(points,color="crimson").add_to(m)
    m.save(f"{cities_names[0]}-{cities_names[-1]}.html")

#draw_map_from(['Mulhouse Ville', 'Illfurth(Mulhouse)', 'Altkirch', 'Dannemarie', 'Montreux Vieux', 'Belfort Ville', 'Hericourt', 'Montbéliard Ville', "L'Isle-sur-le-Doubs", 'Clerval', 'Baume-les-Dames', 'Besançon-Viotte','St-Vit', 'Dole Ville', 'Auxonne', 'Genlis(Dijon)', 'Dijon Ville', 'Beaune(Chagny)', 'Chagny', 'Chalon sur Saône', 'Tournus', 'Mâcon Ville', 'Belleville-sur-Saone', 'Villefranche-s-Saone', "St-Germain-au-Mont-d'Or", 'Lyon Part Dieu'])

def file_to_list(file_path):
    my_file = open(file_path, "r")
    content_list = my_file.readlines()
    return [i.rstrip("\n") for i in content_list]


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("usage: [start train station name] [destination train station name]")
    train_trip = Trip(Station(sys.argv[1]),Station(sys.argv[2]))
    route_selection = int(input(f"Found {len(train_trip.journies())} possible routes. Type 0-{len(train_trip.journies())-1} for which route to visualize:"))
    draw(train_trip.journies()[route_selection])

        

