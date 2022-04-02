from flask import Flask
from flask import request, render_template
from map_train_routes import draw
from db_data import Station,Trip

app = Flask(__name__)


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/map')
def map():
    start_station = Station(request.args.get('start'))
    destination_station = Station(request.args.get("dest"))
    route_number = 0
    if request.args.get("num") != None:
        route_number = int(request.args.get("num"))-1

        

    map = draw(Trip(start_station,destination_station).journies()[route_number])
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
        destination_station_name=request.args.get("dest")
    )


if __name__ == '__main__':
    app.run(debug=True)