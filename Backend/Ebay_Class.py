from bs4 import BeautifulSoup
from Scraper_Class import Scraper, requests
import re

class Ebay(Scraper):
    def __init__(self):
        super().__init__(this_products=[], listing={})      #Same parameters as Scraper class and reset the values

    def site_scrape(self, search, average, filters):
        #If the value difference does not cause a negative average
        if filters[1] is not None and float(filters[1]) < average:
            average = average - float(filters[1])

        #Ebay uses numbers to represent conditions
        if filters[2] is not None:
            if filters[2] == 'New':
                the_condition = '3000'  #New
            else:
                the_condition = '1000'  #Used

            url = 'https://www.ebay.com/sch/i.html?_nkw=' + search.replace(' ', '+') + '&_udhi=' + str(average) + '&LH_ItemCondition=' + the_condition

        else:
            url = 'https://www.ebay.com/sch/i.html?_nkw=' + search.replace(' ', '+') + '&_udhi=' + str(average)   #'https://www.ebay.com/n/error'-->Test HTTP exception

        page = requests.get(url, headers=self.header(), timeout=15)
        page.raise_for_status()     #For HTTP exception

        #Page can be reached and scraped
        if page.status_code == 200:
            soup = BeautifulSoup(page.content, 'html.parser')
            all_prod = soup.find_all('li', class_='s-item')

            id_num = 0      #Each listed item will have a unique id; used in individual listing

            #Used to find the low and high price that the user wants
            #if filters[0] is not None and filters[0] != ',':
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
                listing = {}    #New dictionary for each item
                
                listing['site'] = 'Ebay'    #Used to distiguish when displaying on html site

                #Scrapes the desired html tags for each variable
                price = prod.find(class_='s-item__price') 

                #Only add to products if the proce is in the user selected range
                if price is not None and filters[0] is not None:
                    price = price.text.split()
                    price = price[0]
                    price = price.replace('$', '') 

                    #Fixes issue when finding price 'Tap'
                    if price == 'Tap':
                        continue
                    
                    #Stops this iteration if the price is out of the           
                    if float(price) > price_high or float(price) < price_low:
                        continue

                name = prod.find(class_='s-item__title')
                link = prod.find(class_='s-item__link')  
                image = prod.find(class_='s-item__image-img')

                #Checks for None values for name and price
                if None in (name, price):  
                    continue
                
                if filters[0] is None and price is not None:
                    price = price.text.split()
                    price = price[0]
                    price = price.replace('$', '')

                if image is not None:
                    image = image['src'].replace('225', '500')
                    
                #Creating 'key':value pair for each scraped value
                listing['name'] = name.text
                listing['link'] = link['href']  
                listing['price'] = float(price)
                listing['image'] = image
                listing['id'] = 'E ' + str(id_num)      #Adds the id number with letter E for eBay identifier

                id_num += 1

                self.this_products.append(listing)    #Appends product dictionary to list

            if filters[3] is not None:
                id_num = 0
                for item in self.this_products:
                    item.update({'id':'E ' + str(id_num)})
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

            #Page can be reached and scraped
            if page.status_code == 200:
                soup = BeautifulSoup(page.content, 'html.parser')

                #Scrapes the desired values from the url
                name = soup.find('h1', class_='it-ttl')
                shipping = soup.find(id='fshippingCost')
                price = soup.find(id='prcIsum')
                seller = soup.find('span', class_='mbg-nw')
                rating = soup.find('span', itemprop='ratingValue')
                condition = soup.find(itemprop='itemCondition')
                images = soup.find_all('td', class_='tdThumb')
                iframe = soup.find(id='desc_ifr')['src']

                #If the initial scrape returns a value other than None
                if name is not None:
                    name = name.text[13:].strip()

                #For a current price
                if price is not None:
                    price = price.text
                    price = re.sub('[^$0-9.]', '', price)
                
                #For a bid price
                else:
                    price = soup.find(id='prcIsum_bidPrice')
                    if price is not None:
                        price = price.text
                        price = re.sub('[^$0-9.]', '', price)

                #If the initial scrape returns a value other than None
                if seller is not None:
                    seller = seller.text

                #If the initial scrape returns a value other than None
                if rating is not None:
                    rating = rating.attrs['content']

                #If there is no shipping info
                else:
                    rating = 'none'

                #If the initial scrape returns a value other than None
                if condition is not None:
                    condition = condition.text

                #If there is no condition info
                else:
                    condition = 'none'

                #Gets all images for the listing if there is more than one image
                if len(images) > 1:
                    image_list = []
                    
                    #Iterate through scraped list to find all images
                    for i in images:
                        image_link = i.find('img')['src'].replace('64', '500')
                        image_list.append(image_link)
                    image_list = image_list[:int(len(image_list)/2)]    #Removes the double apended items

                #If there is only one image for the listing
                else:
                    images = soup.find('img', itemprop='image')
                    image_list = [images['src'].replace('64', '500')]

                #If the initial scrape returns a value other than None
                if shipping is not None:
                    shipping = shipping.text.replace('\n', '')

                #If the shipping section has Ebay "FAST 'N FREE"
                else:
                    shipping = soup.find('strong', class_='sh_gr_bld')

                    #Check to ensure new scrape is not None
                    if shipping is not None:
                        shipping = shipping.text[-4:]

                #Creating 'key':value pair for each scraped value
                self.listing['name'] = name
                self.listing['price'] = price
                self.listing['link'] = product_link
                self.listing['seller'] = seller
                self.listing['rating'] = rating
                self.listing['condition'] = condition
                self.listing['images'] = image_list
                self.listing['shipping'] = shipping
                self.listing['iframe'] = iframe
                self.listing['site'] = 'Ebay'    #Used to distiguish when displaying on html site

if __name__ == '__main__':
    pass
    '''Ebay = Ebay()
    filters = [',', '1', 'New', 'name d']
    Ebay.ExceptionsTest(Ebay.site_scrape(input('Query: '), 100, filters))
    Ebay.this_products
    Ebay.ExceptionsTestInd(Ebay.ind_site_scrape(int(54)))
    pprint(Ebay.listing)'''
