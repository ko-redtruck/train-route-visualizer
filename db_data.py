import requests
from bs4 import BeautifulSoup
from urllib.parse import urlencode
import json
import time,datetime
import requests_cache
import code

db_station_cache = requests_cache.CachedSession('db_station_api_cache')

class Station(object):
    __db_data = None
    def __init__(self,name):
        self.__name = name
    def name(self):
        return self.__name
    def location(self):
        self.__load_db_data()
        lat =  self.__db_data["ycoord"]
        lng = self.__db_data["xcoord"]
        lat = int(lat)/10**6
        lng = int(lng)/10**6
        return [lat,lng]
    
    def db_name(self):
        self.__load_db_data()
        return self.__db_data["value"]

    def __load_db_data(self):
        if self.__db_data == None:
            """
            ?encoding=utf-8&L=vs_test_fsugg_getstop&start=1&tpl=sls&REQ0JourneyStopsB=12&REQ0JourneyStopsS0A=7&getstop=1&noSession=yes&iER=yes&S=Freiburg&REQ0JourneyStopsS0a=131072&REQ0JourneyStopsS0o=8&js=true&=
            """
            query = {
                "S" : self.name()
            }
            DB_URL = "https://www.img-bahn.de/bin/ajax-getstop.exe/dn?"
            r = db_station_cache.get(DB_URL + urlencode(query))
            self.__db_data = json.loads(r.text[8:][:-22])['suggestions'][0]

    def db_data(self):
        self.__load_db_data()
        return self.__db_data
        

class Journey_Station(Station):
    def __init__(self,row_data):
        self.__row_data = row_data
        super().__init__(self.__name())

    def __filter_time(self,time_string):
        return time_string.replace("ab","").replace("an","").strip()
    def __name(self):
        return self.__row_data.find("td",class_="station").text.strip()

    def time(self):
        return self.__filter_time(self.__row_data.find("td",class_="time").text)
    def is_intermediate(self):
        return False

class Raw_Station(Station):
    def __init__(self,name,time):
        self.__time = time
        super().__init__(name)

    def __filter_time(self,time_string):
        return time_string.replace("-","").strip()
    def time(self):
        return self.__filter_time(self.__time)
    def is_intermediate(self):
        return False

class Intermediate_Journey_Station(Station):
    def __init__(self,row_data):
        self.__row_data = row_data
        super().__init__(self.__name())
    def __filter_time(self,time_string):
        return time_string.replace("ab","").replace("an","").strip()
    def __name(self):
        return self.__row_data.find("td",class_="intermediateStation").text.strip()
    def time(self):
        return self.__filter_time(self.__row_data.find("td",class_="intermediatTime").text)
    def is_intermediate(self):
        return True

class Journey:
    __transfer_stations_data = None
    __all_station_data = None
    __trip = None

    DB_URL = "https://reiseauskunft.bahn.de/bin/query.exe/dn"

    def __init__(self,table_data,trip):
        self.__table_data = table_data
        self.__trip = trip
    
    #WEB SCRAPING START

    def start_station(self):
        return Raw_Station(
                self.__table_data.find("div",class_="station first").text,
                self.__table_data.find("div",class_="time timeDep").text.replace("-","").strip()
            )
    def end_station(self):
        return Raw_Station(
                self.__table_data.find("div",class_="station stationDest").text.strip(),
                self.__table_data.find("div",class_="time timeArr").text
            )
    
    def duration(self):
        return self.__table_data.find("div",class_="duration").text.replace("|","").strip()
    def changes(self):
        return self.__table_data.find("div",class_="changes").text.replace("Umstiege","").replace(",","").strip()
    def products(self):
        return self.__table_data.find("div",class_="products").text.replace("|","").strip()

    #WEB SCRAPING END

    def __load_all_stations(self):
        if self.__all_station_data == None:
            query_string = urlencode({"HWAI":self.__build_HWAI_string_for_all_stations()})
            self.__all_station_data = self.__trip.load_db_details_data(query_string).text

    def __build_HWAI_string_for_transfer_stations(self):
        id = self.__hwai_id()
        return f"CONNECTION${id}!id={id}!HwaiConId={id}!HwaiDetailStatus=details!"
    
    def __hwai_id(self):
        return self.__table_data.get("id").replace("overview_update","")
    def __build_HWAI_string_for_all_stations(self):
        id = self.__hwai_id()
        return f"CONNECTION${id}!id={id}!HwaiConId={id}!HwaiDetailStatus=journeyGuide!"

    def __load_transfer_stations(self):
        if self.__transfer_stations_data == None:
           self.__transfer_stations_data = self.__trip.load_db_details_data(urlencode({"HWAI":self.__build_HWAI_string_for_transfer_stations()})).text
        
    #WARNING: status broken!
    def transfer_stations(self):
        print(self.__transfer_stations_data)
        self.__load_transfer_stations()
        soup = BeautifulSoup(self.__transfer_stations_data,"html5lib")
        stations = []
        transfer_count = 0
        for row in soup.find_all("tr"):
            if row.get("class") is not None:
                if "first" in row.get("class"):
                    stations.append([Journey_Station(row)])
                if "last" in row.get("class"):
                    stations[transfer_count].append(Journey_Station(row))
                    transfer_count += 1

        return stations
    def all_stations(self):
        self.__load_all_stations()
        soup = BeautifulSoup(self.__all_station_data,"html5lib")

        stations = []
        transfer_count = 0

        #WEB SCARPING START
        for li in soup.find_all("li"):
            if li.get("class") is not None and "remarks" not in li.get("class") and "intermediate" not in li.get("class"):
                if "intermediateStationRow" in li.get("class"):
                    station_name = li.select_one("div.intermediateStation").contents[0].strip()
                elif "sectionArrival" in li.get("class"):
                    station_name = li.select_one("div.station").text.strip()
                else:
                    station_name = li.select_one("div.station").contents[0].strip()
                station_time = li.select_one("div.time").text.strip()
                station = Raw_Station(station_name,station_time)

                if "sectionDeparture" in li.get("class"):
                    stations.append([station])
                elif "sectionArrival" in li.get("class"):
                    stations[transfer_count].append(station)
                    transfer_count += 1
                elif "intermediateStationRow" in li.get("class"):
                    stations[transfer_count].append(station)
        #WEB SCRAPING END
        return stations

class Trip:
    DB_URL = "https://reiseauskunft.bahn.de/bin/query.exe/dn?"

    def __default_start_time(self):
        #tomorrow at 06:00
        return (datetime.datetime.now() + datetime.timedelta(days=1)).replace(hour=6,minute=0)

    def __init__(self,start_station,destination_station,start_time=None):
        if start_time == None:
            start_time = self.__default_start_time()
        self.__start_time = start_time
        self.__load_db_trip_data(start_station,destination_station,start_time)

    def load_db_details_data(self,query_string):
        default_query_parameters = {
            "protocol" : "https:",
            "ajax" : 1,
            "rt" : 1,
            "remeberSortType" : "minDeparture",
            "ld" : self.__db_response_cookies["ld"],
            "ident" : self.__db_response_cookies["ident"],
        }
        if "seqnr" in self.__db_response_cookies.keys():
            default_query_parameters["seqnr"] = self.__db_response_cookies["seqnr"]
        else:
            default_query_parameters["seqnr"] = 1

        
        r =  requests.get(self.DB_URL + urlencode(default_query_parameters) + "&" + query_string)
        self.__db_response_cookies = r.cookies

        return r
    def start_time(self):
        return self.__start_time.strftime("%d.%m.%Y %H:%M")
    def __load_db_trip_data(self,start_station,destination_station,start_time):
        
        query = {
            "revia":"yes",
            "existOptimizePrice-deactivated":1,
            "country":"DEU",
            "dbkanal_007":"L01_S01_D001_qf-bahn-svb-kl2_lz03",
            "start":1,
            "protocol":"https:",
            "REQ0JourneyStopsS0A":1,
            "REQ0JourneyStopsZ0A":1,
            "timesel":"depart",
            "returnDate":"",
            "returnTime":"",
            "returnTimesel":"depart",
            "optimize":0,
            "auskunft_travelers_number":1,
            "tariffTravellerType.1":"E",
            "tariffTravellerReductionClass.1":0,
            "tariffClass":2,
            "rtMode":"DB-HYBRID",
            "externRequest":"yes",
            "HWAI":"JS!js=yes!ajax=yes!",
            "externRequest":"yes",
            "HWAI":"JS!js=yes!ajax=yes!"
        }
        
        query["S"] = start_station.db_data()["value"]
        query["REQ0JourneyStopsSID"] = start_station.db_data()["id"]
        query["Z"] = destination_station.db_data()["value"]
        query["REQ0JourneyStopsZID"] = destination_station.db_data()["id"]

        query["date"] = start_time.strftime("%d.%m.%Y")
        query["time"] = start_time.strftime("%H:%M")

        r = requests.get(self.DB_URL + urlencode(query))

        self.__db_response_cookies = r.cookies
        self.__db_results = r.text
        self.__soup = BeautifulSoup(self.__db_results,"html5lib")

    def journies(self):
        #WEB SCRAPING START        
        journies_div = self.__soup.find(id="resultsOverviewContainer")
        journies = [Journey(tbody,self) for tbody in journies_div.find_all("div") if tbody.get("id") is not None and "overview_update" in tbody.get("id")]
        #WEB SCRAPING END
        if len(journies) == 0:
            raise Exception("No journies/trains found. Please supply new url")
        return journies