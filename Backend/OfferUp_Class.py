from bs4 import BeautifulSoup
from Scraper_Class import Scraper, requests
import re
from pprint import pprint

class OfferUp(Scraper):
    def __init__(self):
        super().__init__(this_products=[], listing={})      #Same parameters as Scraper class and reset the values

    def site_scrape(self, search, average, filters):
        #If the value difference does not cause a negative average
        if filters[1] is not None and float(filters[1]) < average:
            average = average - float(filters[1])

        url = 'https://offerup.com/search/?q=' + search.replace(' ', '+') + '&price_max=' + str(average)

        page = requests.get(url, headers=self.header(), timeout=15)
        page.raise_for_status()     #For HTTP exception

        #Page can be reached and scraped
        if page.status_code == 200:
            soup = BeautifulSoup(page.content, 'html.parser')
            all_prod = soup.find_all('a', class_='_109rpto _1anrh0x')

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

                listing['site'] = 'Offerup'     #Used to distiguish when displaying on html site

                #Scrapes the desired html tags for each variable
                price = prod.find('span', class_='_s3g03e4')

                if price is not None:
                    #Change string FREE to negative 5
                    if price.text == 'FREE':
                        price = -5

                    #Skip string SOLD items
                    elif price.text == 'SOLD':
                        continue

                #Only add to products if the proce is in the user selected range
                if price is not None and filters[0] is not None and price != -5:
                    price = price.text.split()
                    price = price[0]
                    price = price.replace('$', '')
                    #Stops this iteration if the price is out of the           
                    if float(price) > price_high or float(price) < price_low:
                        continue

                name = prod.find('span', class_='_nn5xny4 _y9ev9r')
                link = prod['href']
                image = prod.find('div', class_='_1pq2f04')

                #Checks for None values for name and price
                if None in (name, price):
                    continue
                
                name = name.text    #Get name text

                if filters[0] is None and price is not None and price != -5:
                    price = price.text.split()
                    price = price[0]
                    price = price.replace('$', '')

                if image is not None:
                    image = image.find('img')['data-src']

                listing['name'] = name
                listing['link'] = 'https://offerup.com' + link
                listing['price'] = float(price)
                listing['image'] = image
                listing['id'] = 'O ' + str(id_num)      #Adds the id number with letter O for OfferUp identifier

                id_num += 1

                self.this_products.append(listing)    #Appends product dictionary to list
                    
            if filters[3] is not None:
                id_num = 0
                for item in self.this_products:
                    item.update({'id':'O ' + str(id_num)})
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
                name = soup.find('h1', class_='_t1q67t0 _1juw1gq')
                shipping = soup.find('span', class_='_11uidyww _17axpax')   #Not done
                seller = soup.find('span', class_='_1o4bzwg1')
                rating = soup.find('span', {'data-test': 'star-rate'})
                condition = soup.find('span', {'data-test': 'item-condition'})
                images = soup.find('tr', {'style': 'vertical-align:top'})
                iframe = soup.find('div', {'data-test': 'item-description'})

                #If the initial scrape returns a value other than None
                if name is not None:
                    name = name.text

                #If the initial scrape returns a value other than None
                if shipping is not None:
                    shipping = shipping.text
                    shipping = re.sub('[^$0-9.]', '', shipping)

                #If the initial scrape returns a value other than None
                if seller is not None:
                    seller = seller.text

                #If the initial scrape returns a value other than None
                if rating is not None:
                    rating = rating.find_all('span', class_='_1wmlxe4y _ps5463')

                    fstar = 0
                    hstar = 0
                    for r in rating:
                        full_star = r.find_all('span', class_='_wt1sp7u')   #Full star
                        half_star = r.find_all('span', class_='_zegxq1t')   #Half star
                        
                        #Check for a full star
                        if full_star != []:
                            fstar += 1

                        #Else check for a half star
                        elif half_star != []:
                            hstar += 0.5

                    rating = fstar + hstar      #Sum of full and half star

                    #If there was not a full star or a half star
                    if rating == 0:
                        rating = 'none'

                #If the initial scrape returns a value other than None
                if condition is not None:
                    condition = condition.text

                #No condition value
                else:
                    condition = 'none'

                #If the initial scrape returns a value other than None
                if images is not None:
                    image_list = []

                    images = images.find_all('img')

                    for i in images:
                        image_list.append(i['src'])

                #Not an iframe, but is a description 
                if iframe is not None:
                    iframe = iframe.text
                else:
                    iframe = 'No description available'

                try:
                    if float(the_one['price']) > 0:
                        price = "${:.2f}".format(the_one['price'])
                    else:
                        price = the_one['price']
                except ValueError:
                    price = the_one['price']

                #Creating 'key':value pair for each scraped value
                self.listing['name'] = name
                self.listing['price'] = price     #Used from initial scrape
                self.listing['link'] = product_link
                self.listing['seller'] = seller
                self.listing['rating'] = rating
                self.listing['condition'] = condition
                self.listing['images'] = image_list
                self.listing['shipping'] = shipping
                self.listing['iframe'] = iframe
                self.listing['site'] = 'Offerup'    #Used to distiguish when displaying on html site

if __name__ == '__main__':
    pass
    OU = OfferUp()
    filters = [',', None, None, None]
    OU.ExceptionsTest(OU.site_scrape(input('Query: '), 10, filters))
    pprint(OU.this_products)
    OU.ExceptionsTestInd(OU.ind_site_scrape(int(10)))
    pprint(OU.listing)
