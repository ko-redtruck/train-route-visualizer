from distutils.log import debug
from tracemalloc import start
from flask import Flask
from flask import request, render_template
from map_train_routes import draw
from db_data import Station,Trip
from train_station_folium import JavascriptMarker
import folium
import urllib.parse
import pandas as pd
app = Flask(__name__)


@app.route('/')
def index():
    start_station_name = request.args.get("start")
    start_station_name = start_station_name if start_station_name is not None else ""
    
    destination_station_name = request.args.get("dest")
    destination_station_name = destination_station_name if destination_station_name is not None else ""


    return render_template("index.html",
        start_station_name = start_station_name,
        destination_station_name = destination_station_name
    )


@app.route('/map-stations')
def map_train_stations():
    map = folium.Map(location= [50.11,8.68],zoom_start=5)

    df = pd.read_csv("train_stations_db_low_error.csv",sep=";")
    #df = df.query("is_main_station=='t'")
    for i,train_station in df.iterrows():
        JavascriptMarker(
            [train_station.latitude, train_station.longitude], popup=f"<i>{train_station.name}</i>"
        ).add_to(map)

    return map._repr_html_()

@app.route('/map')
def map():
    start_station = Station(request.args.get('start'))
    destination_station = Station(request.args.get("dest"))
    route_number = 0
    if request.args.get("num") != None:
        route_number = int(request.args.get("num"))-1

    map = draw(Trip(start_station,destination_station).journies()[route_number])
    
    JavascriptMarker(
        [45.3288, -121.6625], popup="<i>Mt. Hood Meadows</i>"
    ).add_to(map)

    return map._repr_html_()

@app.route('/stations')
def stations():
    start_station = Station(request.args.get('start'))
    destination_station = Station(request.args.get("dest"))

    return render_template("stations.html",
        user_start_station_name = start_station.name(),
        user_destination_station_name = destination_station.name(),
        start_station_name=start_station.db_name(),
        destination_station_name=destination_station.db_name()
    )

@app.route('/routes')
def routes():
    start_station = Station(request.args.get('start'))
    destination_station = Station(request.args.get("dest"))

    train_routes = Trip(start_station,destination_station).journies()
    return render_template("routes.html",
        train_routes=train_routes,
        number_of_train_routes=len(train_routes),
        start_station_name=request.args.get('start'),
        destination_station_name=request.args.get("dest"),
        start_station_db_name = start_station.db_name(),
        destination_station_db_name = destination_station.db_name()
    )

if __name__ == '__main__':
    app.run(debug=True)