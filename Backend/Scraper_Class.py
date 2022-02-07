import random, requests
from abc import ABC, abstractmethod

class Scraper(ABC):
    def __init__(self, this_products=[], listing={}):
        self.this_products = this_products      #List for all products scrape
        self.listing = listing                  #Dictionary for single product scrape

    #Used to pass a random header into the site request
    def header(self):
        headers = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36',
        ]

        return {'User-Agent': random.choice(headers)}   #Return the random header with key User-Agent

    #Used to scrape search product page
    @abstractmethod                         #All child classes must have a site_scrape
    def site_scrape(self, search):
        pass

    #Used to scrape a single product page
    @abstractmethod                         #All child classes must have a ind_site_scrape
    def ind_site_scrape(self, search):
        pass

    #Used to error check a site_scrape method
    def ExceptionsTest(self, scrape):
        try:
            scrape  #site_scrape(query)

        #Catches HTTP errors
        except requests.HTTPError as e:
            self.this_products = [{'Error': str(e.response.status_code) + ': ' + e.response.reason}]

        #Catches Connection errors
        except requests.ConnectionError:
            self.this_products = [{'Error': 'Connection Error. Check your internet connection.'}]

        #Catches all both timeout errors
        except requests.Timeout:
            self.this_products = [{'Error': 'Timeout Error.'}]

        #Handles any other error that may occur
        except requests.RequestException:
            self.this_products = [{'Error': 'Unknown Error.'}]

    #Used to error check a ind_site_scrape
    def ExceptionsTestInd(self, scrape):
        try:
            scrape  #ind_site_scrape(ids)

        #Catches HTTP errors
        except requests.HTTPError as e:
            self.listing = {'Error': str(e.response.status_code) + ': ' + e.response.reason}

        #Catches Connection errors
        except requests.ConnectionError:
            self.listing = {'Error': 'Connection Error. Check your internet connection.'}

        #Catches all both timeout errors
        except requests.Timeout:
            self.listing = {'Error': 'Timeout Error.'}

        #Handles any other error that may occur
        except requests.RequestException:
            self.listing = {'Error': 'Unknown Error.'}
