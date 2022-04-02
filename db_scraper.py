from bs4 import BeautifulSoup

BEAUTIFULSOUP_PARSER_MODE="html5lib"


class DB_Journey_Scraper:
    def __init__(self,journey_data):
        self.__soup = BeautifulSoup(journey_data,BEAUTIFULSOUP_PARSER_MODE)

    def hwai_id(self):
        return self.__soup.find("div").get("id").replace("overview_update","")
    def start_station_name(self):
        return self.__soup.find("div",class_="station first").text
              
    def start_station_time(self):
        return self.__soup.find("div",class_="time timeDep").text.replace("-","").strip()
        
    def destination_station_name(self):
        return self.__soup.find("div",class_="station stationDest").text.strip()

    def destination_station_time(self):
        return self.__soup.find("div",class_="time timeArr").text

    def duration(self):
        return self.__soup.find("div",class_="duration").text.replace("|","").strip()
    def changes(self):
        return self.__soup.find("div",class_="changes").text.replace("Umstiege","").replace(",","").strip()
    def products(self):
        return self.__soup.find("div",class_="products").text.replace("|","").strip()

    def all_stations_data_from(self,all_stations_raw_data):
        all_station_soup = BeautifulSoup(all_stations_raw_data,"html5lib")

        stations_data = []
        transfer_count = 0

        for li in all_station_soup.find_all("li"):
            if li.get("class") is not None and "remarks" not in li.get("class") and "intermediate" not in li.get("class") and "dateDivider" not in li.get("class"):
                if "intermediateStationRow" in li.get("class"):
                    station_name = li.select_one("div.intermediateStation").contents[0].strip()
                elif "sectionArrival" in li.get("class"):
                    station_name = li.select_one("div.station").text.strip()
                else:
                    station_name = li.select_one("div.station").contents[0].strip()
                station_time = li.select_one("div.time").text.strip()
                station_data = {
                    "name" : station_name,
                    "time" : station_time
                }

                if "sectionDeparture" in li.get("class"):
                    stations_data.append([station_data])
                elif "sectionArrival" in li.get("class"):
                    stations_data[transfer_count].append(station_data)
                    transfer_count += 1
                elif "intermediateStationRow" in li.get("class"):
                    stations_data[transfer_count].append(station_data)
        return stations_data

class DB_Trip_Scraper:
    def __init__(self,html_train_travel_information_query_result):
        self.__soup = BeautifulSoup(html_train_travel_information_query_result,BEAUTIFULSOUP_PARSER_MODE)
    def journies_data(self):
        journies_div = self.__soup.find(id="resultsOverviewContainer")
        journies_data = [str(tbody) for tbody in journies_div.find_all("div") if tbody.get("id") is not None and "overview_update" in tbody.get("id")]
        return journies_data
   