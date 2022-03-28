import bs4
from bs4 import BeautifulSoup
with open("response.html") as file:
    soup = BeautifulSoup(file.read())
   
           