from bs4 import BeautifulSoup
from Scraper_Class import Scraper, requests
import re

class eCrater(Scraper):
    def __init__(self):
        super().__init__(this_products=[], listing={})      #Same parameters as Scraper class and reset the values

    def site_scrape(self, search, average, filters):
        #If the value difference does not cause a negative average
        if filters[1] is not None and float(filters[1]) < average:
            average = average - float(filters[1])

        url = 'https://www.ecrater.com/filter.php?keywords=' + search.replace(' ', '+') + '&to=' + str(average)

        page = requests.get(url, headers=self.header(), timeout=15)
        page.raise_for_status()     #For HTTP exception

        if page.status_code == 200:
            soup = BeautifulSoup(page.content, 'html.parser')
            all_prod = soup.find_all('li', class_='product-item')
            
            id_num = 0      #Each listed item will have a unique id; used in individual listing

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
                listing = {}    #New dictionary for each item

                listing['site'] = 'eCrater'     #Used to distiguish when displaying on html site

                #Scrapes the desired html tags for each variable
                price = prod.find(class_='btn btn-inverse')
                
                #Only add to products if the proce is in the user selected range
                if price is not None and filters[0] is not None:
                    price = price.text.split()
                    price = price[0]
                    price = price.replace('$', '')
                    #Stops this iteration if the price is out of the           
                    if float(price) > price_high or float(price) < price_low:
                        continue

                name = prod.find(class_='product-details').find('a')
                link = prod.find(class_='product-image')
                image = prod.find(class_='product-image').find('img')
                
                #Checks for None values for name and price
                if None in (name, price):
                    continue
                
                if filters[0] is None and price is not None:
                    price = price.text.split()
                    price = price[0]
                    price = price.replace('$', '')

                #Creating 'key':value pair for each scraped value
                listing['name'] = name['title']
                listing['link'] = 'https://www.ecrater.com' + link['href']
                listing['price'] = float(price)
                listing['image'] = image['src']

                listing['id'] = 'e ' + str(id_num)

                id_num += 1

                self.this_products.append(listing)    #Appends product dictionary to list
            
            if filters[3] is not None:
                id_num = 0
                for item in self.this_products:
                    item.update({'id':'e ' + str(id_num)})
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
                
                #Broad scrapes to help find the desired values
                price = soup.find(id='product-title-actions').find(class_='btn btn-inverse')
                name = soup.find(id='product-title').find('h1')
                seller = soup.find(class_='seller-username')
                rating = soup.find(class_='stars stars-5')
                condition = soup.find(id='product-details')
                images = soup.find(class_='scrolling-thumbnails')
                shipping = soup.find(id='product-details')
                iframe = soup.find(id='description')

                #If the initial scrape returns a value other than None
                if name is not None:
                    name = name.text

                #If the initial scrape returns a value other than None
                if price is not None:
                    price = price.text
                    try:
                        price = "${:.2f}".format(price)
                    except ValueError:
                        pass

                #If the initial scrape returns a value other than None
                if seller is not None:
                    seller = seller.text

                #All rating classes in html
                stars = ['stars stars-0half', 'stars stars-1half', 'stars stars-2half', 'stars stars-3half', 
                        'stars stars-4half', 'stars stars-1', 'stars stars-2', 'stars stars-3', 'stars stars-4']

                #If the initial scrape of class 5 stars is not None
                if rating is not None:
                    rating = rating.text.split('/')[0]

                #If the initial scrape of class 5 stars is None, iterate through the stars list
                else:
                    for i in stars:
                        rating = soup.find('span', class_=i)

                        #If one of the classes in stars returns a value other than None
                        if rating is not None:
                            rating = rating.text.replace('half', '.5').split('/')[0]
                            break
                
                #If the initial scrape returns a value other than None
                if condition is not None:
                    condition = condition.text.replace('\t', '').replace('\n', '').split('Condition:')[1].strip()

                #If the initial scrape returns a value other than None
                if images is not None:
                    image_list = []
                    images = images.find_all('li') 

                    #Iterate through images to get the link for each
                    for i in images:
                        image_link = i.find('img')['src']
                        image_list.append(image_link)

                #If the initial scrape is None (for a product with a single image)
                else:
                    images = soup.find(id='product-image')

                    #Get the link for the single image
                    if images is not None:
                        images = images.find('img')['src']
                        image_list = [images]
                
                #If the initial scrape returns a value other than None
                if shipping is not None:
                    shipping = shipping.text.split()

                    #Iterate through the shipping list
                    for i in shipping:

                        #Find a string value of 'free' or '$value' and store the string in shipping
                        if i == 'free' or i.startswith('$'):
                            shipping = i
                            break

                        #If there is no shipping info
                        else:
                            shipping = 'none'
                
                #If the initial scrape returns a value other than None
                if iframe is not None:
                    iframe = iframe.text.replace('\r', '').replace('\n', '').replace('\t', '')  #here are two that may work .replace('_', '').replace('=', '')

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
                self.listing['site'] = 'eCrater'    #Used to distiguish when displaying on html site

if __name__ == '__main__':
    pass
    '''eCrater = eCrater()
    filters = [',', None, None, None]
    eCrater.ExceptionsTest(eCrater.site_scrape(input('Query: '), 100, filters))
    eCrater.this_products
    eCrater.ExceptionsTestInd(eCrater.ind_site_scrape(int(10)))
    print(eCrater.listing)'''
