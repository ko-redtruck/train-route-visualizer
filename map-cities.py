from ast import Not
import folium
import geocoder
import sys

COUNTRY = 'Germany'

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
    g  = _get_geo_location_from_raw( _transform_city_name(city_name),previous_location)
    if g.ok:
        return g
    else:
        return None



def draw_map_from(cities_names):
    previous_location = None
    g_cities = []
    for city_name in cities_names:
        g_city = get_geo_location_from(city_name,previous_location)
        if g_city is not None:
            print(f"Adding: {g_city.address} for {city_name}")
            g_cities.append(g_city)
            previous_location = [g_city.lat,g_city.lng]

   # g_cities = [get_geo_location_from(city_name) for city_name in cities_names]
    #g_cities = [g_city for g_city in g_cities if g_city is not None]
    
    #print(g_cities)
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
    if len(sys.argv) >= 3:
        COUNTRY = sys.argv[2]
    draw_map_from(file_to_list(sys.argv[1]))
        