from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import math
import pandas as pd
from random import randint
import re
import requests
from requests_html import HTMLSession
import time
from typing import Union

       
class Scraper:
    def __init__(self, number_of_items:int, room_min=1,room_max=None)->None:
        self.room_min = room_min
        self.room_max = room_max
        self.__number_of_items = number_of_items
        self.__session = HTMLSession()
        self.default_url = "https://en.aruodas.lt/butu-nuoma/vilniuje/puslapis/"
        self.urls = []
        self.links_listings = []
        self.full_data = [] 
         
    def validate_input(self, value)->None:   
        if not isinstance (value,  (int,float)):
            raise TypeError("Value entered is not numeric \n Enter a numeric input!!!!")  
          
    def count_pages(self)-> int:
        ''' 
        Finds the number of pages   that should be scrapped to get the number of items from the website
        Returns the number of pages that should be scrapped to get the number of items
        '''  
        no_of_pages = math.ceil(abs(self.__number_of_items / 25))
        return no_of_pages

    def generate_urls(self)-> None:
        """
        Generates urls for for all the pages to be scraped given
        Returns a list of urls
        """ 
        number_of_pages = self.count_pages()
        for page_number in range(1,number_of_pages+1):
            url = self.default_url + f"{page_number}/FRoomNumMin={self.room_min}&FRoomNumMax={self.room_max}"
            self.urls.append(url)        
    
    def extract_url_listing(self)->None:
        ''' Extracts necessary fields from the web page
            Returns dictionary containing scrapped fields '''
        for url in self.urls:
            page = self.__session.get(url)
            page.html.render(sleep=1, timeout=20)
            link_container = page.html.find('td.list-adress')
            for item in link_container:
                self.links_listings.extend(item.absolute_links)
                  
    def extract_features(self, url:str)->dict:
        '''Extracts required data points from page'''
        page = self.__session.get(url)
        page.html.render(sleep=1, scrolldown=6, timeout=20)
        page_data = {}
        attributes_names = []
        values = []
        listing_name = page.html.find("h1.obj-header-text", first=True)
        if listing_name is not None and listing_name.html:
            listing_name = listing_name.text.strip()
            address = listing_name.split(', ')
            page_data['city'] = address[0] or ""
            page_data['neighbourhood'] = address[1] or ""
            page_data['description'] = listing_name or ""
            page_data['link'] = url         
            table = page.html.find('dl.obj-details', first=True)
            raw = table.text.replace(':', '')
            other_attrs = raw.split('\n')
            i = 0
            while i in range(len(other_attrs)):
                page_data[other_attrs[i]] = other_attrs[i+1]
                i += 2
            energy = page.html.find('span.energy-class-tooltip', first=True)
            if energy is not None:
                page_data['energy_class'] = energy.text
            divs = page.html.find('div.statistic-info-cell-main')
            for div in divs:
                feature = div.text
                attr = feature.split("\n~ ")
                page_data[attr[0]] = attr[1] or ""
            # page_data['crime'] = page.html.find('div.arrow_line_left', first=True).text or ""
        return page_data
    
    def scrape_listings(self):
        self.validate_input(self.room_min)
        self.validate_input(self.room_max)
        self.validate_input(self.__number_of_items)
        self.generate_urls()
        self.extract_url_listing()
        num = 1
        for url in self.links_listings[0:self.__number_of_items+1]:
            data = self.extract_features(url)  
            print( f"Extracted {num} listing successfully")
            num += 1
            if data != {}:
                self.full_data.append(data)
            time.sleep(randint(1, 5))    
        return self.full_data
    
class DataTransformation:
    def __init__(self, data:list) ->pd.DataFrame:
        try:
            self.df = pd.DataFrame.from_dict(data, orient='columns')
        except Exception as error:
            raise error(" There was an error converting list to dataframe", error)
        try:
            self.clean()            
        except Exception as error:
            raise error("There was a  problem  cleaning the dataframe", error) 
            
    def clean(self) ->pd.DataFrame:
        """
        Cleans scraped DataFrame and returns cleaned dataframe
        """ 
        self.df['Price per month'] = self.df['Price per month'].apply(lambda x :float(re.sub("[^0-9 ,.]", "",x).replace(",", ".").replace(" ","")))
        self.df['Area'] = self.df['Area'].apply(lambda x :re.sub("[^0-9 ,.]", "",x).replace(",", "."))
        self.df['Nearest educational institution'].fillna("0km",inplace=True)
        self.df['Nearest educational institution'] = self.df['Nearest educational institution'].apply(lambda x: float(re.sub("[^0-9 ,.]", "",str(x)).replace(",", ".") )*1000 if 'km' in str(x) else float(re.sub("[^0-9 ,.]", "",str(x)).replace(",", ".")))
        self.df['Nearest shop'].fillna("0km",inplace=True)
        self.df['Nearest shop'] = self.df['Nearest shop'].apply(lambda x: float(re.sub("[^0-9 ,.]", "",str(x))
                            .replace(",", ".") )*1000 if 'km' in str(x) else
                            float(re.sub("[^0-9 ,.]", "",str(x)).replace(",", ".")))
        self.df['Public transport stop'].fillna("0km",inplace=True)
        self.df['Public transport stop'] = self.df['Public transport stop'].apply(lambda x: float(re.sub("[^0-9 ,.]", "",x)
                                    .replace(",", ".") )*1000 if 'km' in str(x) else
                                    float(re.sub("[^0-9 ,.]", "",str(x)).replace(",", "."))) 
        self.df['Nearest kindergarten'].fillna("0km",inplace=True)
        self.df['Nearest kindergarten'] = self.df['Nearest kindergarten'].apply(lambda x: float(re.sub("[^0-9 ,.]", "",str(x))
                                    .replace(",", ".") )*1000 if 'km' in str(x) else
                                    float(re.sub("[^0-9 ,.]", "",str(x)).replace(",", ".")))
        self.df['Build year'] = self.df['Build year'].apply(lambda x: int(re.sub("[^0-9]","",x.split(",")[0])))                     
        return self.df                                          

if __name__ == '__main__':
    room_min = int(input("Enter the minimum number of room:"))
    room_max = int(input("Enter the maximum number of rooms:"))
    number_of_items = int(input("Enter the number of items you want to scrape:"))
    x = Scraper(room_max =room_max, number_of_items =number_of_items)
    # print(x.scrape_listings())
    data= DataTransformation(data=x.scrape_listings()).df
    data.to_csv("data_y.csv", index =False)