import bs4
from bs4 import BeautifulSoup
with open("all_stations.html") as file:
    soup = BeautifulSoup(file.read())
   
           