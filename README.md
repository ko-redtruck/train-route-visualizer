# train-route-visualizer
Visualize train routes with data from Deutsche Bahn and MapBox

### Tools
Output the list of station names from a train info site of the Deutsche Bahn
```
python3 train-route.py <db-train-info-url> > train_station_names
```

Mark and draw a path of city names in a certain country 
```
python3 train-route.py <train_station_names_file> <Country>
```

### Example
```
export MAPBOX_ACCESS_TOKEN=<your access token for mapbox>
python3 train_route.py 'https://reiseauskunft.bahn.de/bin/traininfo.exe/dn/267003/908814/557064/189531/80?ld=43109&protocol=https:&seqnr=2&ident=bv.09569109.1647008909&date=15.03.22&station_evaId=8700021&station_type=dep&currentReferrer=tp&rt=1&rtMode=DB-HYBRID&&time=14:41&currentJourneyClass=2&' > train_route_1
python3 map-cities.py train_route_1 France
```
![Screenshot from 2022-03-11 16-25-24](https://user-images.githubusercontent.com/24638508/157896934-9b5324e9-a286-42b6-976f-f04e2789fae8.png)
