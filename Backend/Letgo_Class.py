from bs4 import BeautifulSoup
from Scraper_Class import Scraper, requests
import re

class Letgo(Scraper):
    def __init__(self):
        super().__init__(this_products=[], listing={})      #Same parameters as Scraper class and reset the values
        
    def site_scrape(self, search, average, filters):
        #If the value difference does not cause a negative average
        if filters[1] is not None and float(filters[1]) < average:
            average = average - float(filters[1])

        url = 'https://www.letgo.com/en-us?searchTerm=' + search.replace(' ', '+') + '&price&Bmax&D=' + str(int(average))

        page = requests.get(url, headers=self.header(), timeout=15)
        page.raise_for_status()     #For HTTP exception

        #Page can be reached and scraped
        if page.status_code == 200:
            soup = BeautifulSoup(page.content, 'html.parser')
            all_prod = soup.find_all('div', {'data-testid': 'feed-grid-item'})

            id_num = 0      #Each listed item will have a unique id; used in individual listing
            
            for prod in all_prod:
                listing = {}

                listing['site'] = 'Letgo'

                link_area_name = prod.find_all('p')
                image = prod.find('a', {'rel': 'nofollow'}).find('img')

                #Checks for None values for link, name, and price
                if None in (link_area_name):
                    continue

                name = link_area_name[0].text   #Name text

                area = link_area_name[1].text   #Area text

                link = link_area_name[0].find('a')['href']  #The link

                if image is not None:
                    image = image['src']

                listing['name'] = name
                listing['link'] = link
                listing['price'] = area
                listing['image'] = image
                listing['id'] = 'L ' + str(id_num)      #Adds the id number with letter L for Letgo identifier

                id_num += 1
                
                self.this_products.append(listing)    #Appends product dictionary to list

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
                name = soup.find('div', {'data-test': 'name'})
                price = soup.find('div', {'data-test': 'price'})
                seller = soup.find('a', {'data-test': 'item-link-user-profile'})
                #rating = soup.find_all('svg', {'viewbox': '0 0 24 24'})    Needs work
                images = soup.find('ul', {'tabindex': '0'})
                iframe = soup.find('div', {'data-test': 'description'})
                
                #If the initial scrape returns a value other than None
                if name is not None:
                    name = name.text

                #If the initial scrape returns a value other than None
                if price is not None:
                    price = price.text 
                    try:
                        price = "${:.2f}".format(float(price[1:]))
                    except ValueError:
                        pass
            
                    '''
                    clean = True
                    #Looking for a decimal
                    for i in price:
                        if i == '.':
                            clean = False

                    #There was no decimal
                    if clean:
                        price += '.00'
                        '''

                #If the initial scrape returns a value other than None
                if seller is not None:
                    seller = seller.find('p')
                    if seller is not None:
                        seller = seller.text

                image_list = []
                #If the initial scrape returns a value other than None
                if images is not None:
                    images = images.find_all('li')
                    
                    for i in images:
                        image_list.append(i['src'])

                #If the initial scrape returns a value other than None
                if iframe is not None:
                    iframe = iframe.text.replace('\n', '')

                else: 
                    iframe = 'No description available'

                #Creating 'key':value pair for each scraped value
                self.listing['name'] = name
                self.listing['price'] = price
                self.listing['link'] = product_link
                self.listing['seller'] = seller
                self.listing['rating'] = 'none'
                self.listing['condition'] = 'none'
                self.listing['images'] = image_list
                self.listing['shipping'] = 'none'
                self.listing['iframe'] = iframe
                self.listing['site'] = 'Letgo'    #Used to distiguish when displaying on html site

if __name__ == '__main__':
    pass
    '''Letgo = Letgo()
    filters = [',', None, None, None]
    Letgo.ExceptionsTest(Letgo.site_scrape(input('Query: '), 10.34, filters))
    Letgo.this_products
    Letgo.ExceptionsTestInd(Letgo.ind_site_scrape(int(5)))
    print(Letgo.listing)'''
