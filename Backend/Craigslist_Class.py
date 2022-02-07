from bs4 import BeautifulSoup
from selenium import webdriver
from Scraper_Class import Scraper, requests
import re

class Craigslist(Scraper):
    def __init__(self):
        super().__init__(this_products=[], listing={})      #Same parameters as Scraper class and reset the values

    def site_scrape(self, search, average, filters):
        #If the value difference does not cause a negative average
        if filters[1] is not None and float(filters[1]) < average:
            average = average - float(filters[1])

        url = 'https://harrisburg.craigslist.org/search/sss?query=' + search.replace(' ', '+') + '&max_price=' + str(average)

        #-----------------------------
        options = webdriver.ChromeOptions()     #Instance to edit Chrome settings
        options.headless = True     #Uses headless browser
        options.add_argument('log-level=3')     #Disables console logging errors
        browser = webdriver.Chrome(options=options)     #Instace to create chrome browser with new settings

        browser.get(url)    #Opens the URL in the headless browser
        #browser.raise_for_status()     #For HTTP exception
        page = browser.page_source      #Stores the html to parse
        browser.quit()      #Closes all browsers, not just current one
        #----------------------------- 

        soup = BeautifulSoup(page, 'html.parser')
        all_prod = soup.find_all('li', class_='result-row')
        
        if all_prod != []:      #Temporary fix for status code check
            id_num = 0
            
            #Used to find the low and high price that the user wants
            if filters[0] != ',':
                priceRange = filters[0].split(',')

                #User did not enter a min value
                if priceRange[0] == '':
                    price_low = 0
                    price_high = float(priceRange[1])

                #User did not enter a max value
                elif priceRange[1] == '':
                    price_low = float(priceRange[0])
                    price_high = average

                #Both min and max were entered
                else:
                    price_low = float(priceRange[0])
                    price_high = float(priceRange[1])
            
            #There was no min or max entered
            else:
                price_low = 0
                price_high = average

            for prod in all_prod:
                listing = {}     #New dictionary for each item

                listing['site'] = 'Craigslist'      #Used to distiguish when displaying on html site
                
                #Scrapes the desired html tags for each variable
                price = prod.find(class_='result-price')

                if price is not None:
                    price = price.text.replace('$', '')

                    #Only add to products if the proce is in the user selected range
                    if filters[0] is not None and (float(price) > price_high or float(price) < price_low):
                        continue

                name = prod.find(class_='result-title hdrlnk')
                link = prod.find(class_='result-title hdrlnk')
                image = prod.find('div', class_='swipe')

                #Checks for None values for name and price
                if None in (name, price):
                    continue
                
                #Creating 'key':value pair for each scraped value
                link = link['href']
                listing['link'] = link        
                listing['name'] = name.text          
                listing['price'] = float(price)

                #If there is an image get the first one
                if image is not None:
                    image = image.find('img')['src'].replace('600x450', '300x300')      #Resizes images to smaller image
                
                #Store no_photo.png in for image
                else:
                    image = 'https://pngimage.net/wp-content/uploads/2018/06/no-photo-png-1.png'

                listing['image'] = image
                listing['id'] = 'C ' + str(id_num)
                
                id_num += 1
                
                self.this_products.append(listing)    #Appends product dictionary to list

                #Craigslist will have 100+ items if I don't break here
                if len(self.this_products) == 50:
                    break
            
            if filters[3] is not None:
                id_num = 0
                for item in self.this_products:
                    item.update({'id':'C ' + str(id_num)})
                    id_num += 1
        
    def ind_site_scrape(self, number):
        #If the intial site was not reachable; not neccessary, but redundant
        if 'Error' in self.this_products[0]:
            pass    #Passed to the return statement
        
        #The first site was reached and scraped
        else:
            the_one = self.this_products[number]    #Get the correct listing
    
            product_link = the_one['link']      #Pull the link to request
            
            page = requests.get(product_link, headers=self.header(), timeout=15)
            page.raise_for_status()     #For HTTP exception

            if page.status_code == 200:
                soup = BeautifulSoup(page.content, 'html.parser')

                #Broad scrapes to help find the desired values
                name = soup.find(id='titletextonly')
                price = soup.find(class_='price')
                shipping = soup.find(class_='postingtitletext').find('small')
                images = soup.find(id='thumbs')
                iframe = soup.find(id='postingbody')
                
                #If the initial scrape returns a value other than None
                if name is not None:
                    name = name.text.replace('\n', '').strip()
                
                #If the initial scrape returns a value other than None
                if price is not None:
                    price = price.text.replace('$', '')
                    try:
                        price = "${:.2f}".format(float(price))
                    except ValueError:
                        pass

                #This works so I will keep it, but there might be a better way
                conditions = ['fair', 'excellent', 'good', 'used', 'new', 'like new']
                
                for i in conditions:
                    condition = soup(text=i)    #Search for the string in the body of the html
                    
                    #Fix for if there is not a condition field when i is 'new'
                    if i == 'new' and len(condition) < 2:
                        condition = 'none'
                        break

                    #Get the first index of the found string
                    elif condition != []:
                        condition = condition[0]
                        break

                    #The condition is unknown otherwise
                    else:
                        condition = 'none'

                image_list = []
                #If the initial scrape returns a value other than None
                if images is not None:
                    for i in images:
                        image_link = i.find('img')['src']
                        image_link = image_link.replace('50x50c', '600x450')    #Used to change link to get clearer image
                        image_list.append(image_link)

                #If the initial scrape returns a value other than None
                if shipping is not None:
                    shipping = shipping.text.replace('(', '').replace(')', '').strip()

                if iframe is not None:
                    iframe = iframe.text.replace('QR Code Link to This Post', '').strip()

                #Creating 'key':value pair for each scraped value
                self.listing['name'] = name
                self.listing['price'] = price
                self.listing['link'] = product_link
                self.listing['seller'] = 'none'     #No seller field, only says 'Owner'
                self.listing['rating'] = 'none'   #No rating field
                self.listing['condition'] = condition
                self.listing['images'] = image_list
                self.listing['shipping'] = shipping
                self.listing['iframe'] = iframe
                self.listing['site'] = 'Craigslist'

    def site_areas(self):
        pass

if __name__ == '__main__':
    pass
    '''Craigslist = Craigslist()
    filters = [',', '1', 'New', 'price d']
    Craigslist.ExceptionsTest(Craigslist.site_scrape(input('Query: '), 100, filters))
    Craigslist.ExceptionsTestInd(Craigslist.ind_site_scrape(int(10)))
    print(Craigslist.listing)'''
