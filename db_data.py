import requests
from urllib.parse import urlencode
import json
import datetime
import requests_cache

from db_scraper import DB_Journey_Scraper,DB_Trip_Scraper

db_station_cache = requests_cache.CachedSession('db_station_api_cache')

class Station(object):
    __db_data = None
    def __init__(self,name,time=None):
        self.__name = name
        self.__time = time
    def name(self):
        return self.__name.strip()
    def location(self):
        self.__load_db_data()
        lat =  self.__db_data["ycoord"]
        lng = self.__db_data["xcoord"]
        lat = int(lat)/10**6
        lng = int(lng)/10**6
        return [lat,lng]
    
    def __decode_db_ascii_string(self,str):
        raw_characters = list(str)
        real_characters = []
        i=0
        while i < len(raw_characters):
            c = raw_characters[i]
            if i < len(raw_characters)-2 and "".join(raw_characters[i:i+3]) == "&#x":
                c = chr(int("".join(raw_characters[i+3:i+7]),base=16))
                i+=7
            real_characters.append(c)
            i+=1
        return "".join(real_characters)

    def db_name(self):
        self.__load_db_data()
        #Freiburg&#x0028;
        return self.__decode_db_ascii_string(self.__db_data["value"].strip())
        
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
            suggested_train_stations = json.loads(r.text[8:][:-22])['suggestions']
            if len(suggested_train_stations) == 0:
                raise LookupError("Train station not found")
            self.__db_data = suggested_train_stations[0]

    def db_data(self):
        self.__load_db_data()
        return self.__db_data
    
    def __filter_time(self,time_string):
        return time_string.replace("–","").strip()
    def time(self):
        return self.__filter_time(self.__time)
    def is_intermediate(self):
        return False
    

class Journey:
    __all_stations_raw_data = None
    __trip = None

    DB_URL = "https://reiseauskunft.bahn.de/bin/query.exe/dn"

    def __init__(self,table_data,trip):
        self.__scraper = DB_Journey_Scraper(table_data)
        self.__trip = trip
    
    def start_station(self):
        return Station(
                self.__scraper.start_station_name(),
                self.__scraper.start_station_time()
            )
    def end_station(self):
        return Station(
                self.__scraper.destination_station_name(),
                self.__scraper.destination_station_time()
            )
    
    def duration(self):
        return self.__scraper.duration()
    def changes(self):
        return self.__scraper.changes()
    def products(self):
        return self.__scraper.products()

    def __load_all_stations(self):
        if self.__all_stations_raw_data == None:
            query_string = urlencode({"HWAI":self.__build_HWAI_string_for_all_stations()})
            self.__all_stations_raw_data = self.__trip.load_db_details_data(query_string).text

    def __hwai_id(self):
        return self.__scraper.hwai_id()

    def __build_HWAI_string_for_all_stations(self):
        id = self.__hwai_id()
        return f"CONNECTION${id}!id={id}!HwaiConId={id}!HwaiDetailStatus=journeyGuide!"

    def all_stations(self):
        self.__load_all_stations()
        return [[Station(station_data["name"],station_data["time"]) for station_data in train] for train in self.__scraper.all_stations_data_from(self.__all_stations_raw_data)]

class Trip:
    DB_URL = "https://reiseauskunft.bahn.de/bin/query.exe/dn?"
    
    def __default_start_time(self):
        #tomorrow at 06:00
        return (datetime.datetime.now() + datetime.timedelta(days=1)).replace(hour=6,minute=0)

    def start_station(self):
        return self.__start_station
    def destination_station(self):
        return self.__destination_station
    def __init__(self,start_station,destination_station,start_time=None):
        if start_time == None:
            start_time = self.__default_start_time()
        self.__start_time = start_time
        self.__start_station = start_station
        self.__destination_station = destination_station
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
        self.__scraper = DB_Trip_Scraper(r.text)
        if "leider konnte zu Ihrer Anfrage keine Verbindung gefunden werden" in r.text:
            self.__connection_found = False
        else:
            self.__connection_found = True
    def journies(self):
        if self.__connection_found:
            return [Journey(journey_data,self) for journey_data in self.__scraper.journies_data()]
        else:
            return []