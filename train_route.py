import requests
from bs4 import BeautifulSoup
import sys

def city_station_names_from(db_train_url):
    r = requests.get(db_train_url)
    soup = BeautifulSoup(r.text, 'html.parser')

    station_names = []

    table_rows = soup.table.find_all("tr")
    for i in range(2,len(table_rows)):
        station_names.append(table_rows[i].a.text)

    return station_names
    
if __name__ == "__main__":
    for station in city_station_names_from(sys.argv[1]):
        print(station)
