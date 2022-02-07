from bs4 import BeautifulSoup
from Scraper_Class import Scraper, requests
import re

class Bonanza(Scraper):
    def __init__(self):
        super().__init__(this_products=[], listing={})      #Same parameters as Scraper class and reset the values

    def site_scrape(self, search, average, filters):
        #If the value difference does not cause a negative average
        if filters[1] is not None and float(filters[1]) < average:
            average = average - float(filters[1])

        url = 'https://www.bonanza.com/items/search?q[country_to_filter]=US&q[ship_country]=1' + '&q[max_price]=' + str(average) + '&q[search_term]=' + search.replace(' ', '+')

        page = requests.get(url, headers=self.header(), timeout=15)
        page.raise_for_status()     #For HTTP exception

        #Page can be reached and scraped
        if page.status_code == 200:
            soup = BeautifulSoup(page.content, 'html.parser')
            all_prod = soup.find_all('div', class_='browsable_item order_1 search_result_item')
            
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

                listing['site'] = 'Bonanza'     #Used to distiguish when displaying on html site

                #Scrapes the desired html tags for each variable
                price = prod.find(class_='item_price')

                #Only add to products if the proce is in the user selected range
                if price is not None and filters[0] is not None:
                    price = price.text.replace(' + ',':').split(':')[0]     #Removes the shipping price
                    price = re.sub('[^0-9.]', '', price)       #Removes the \n at the beginning and end
                    #Stops this iteration if the price is out of the           
                    if float(price) > price_high or float(price) < price_low:
                        continue
                
                name = prod.find(class_='item_title')
                link = prod.find(class_='item_image_container')
                image = prod.find(class_='item_image_container').find('img')
                
                #Checks for None values for name and price
                if None in (name, price):
                    continue
                
                #Creating 'key':value pair for each scraped value
                name = name.text
                name = re.sub('\n', '', name)   #Removes the \n at the beginning and end, but leaves the ...
                listing['name'] = name
            
                listing['link'] = 'https://www.bonanza.com' + link['href']  
                
                if filters[0] is None and price is not None:
                    price = price.text.replace(' + ',':').split(':')[0]     #Removes the shipping price
                    price = re.sub('[^0-9.]', '', price)       #Removes the \n at the beginning and end

                listing['price'] = float(price)

                listing['image'] = image['src']

                listing['id'] = 'B ' + str(id_num)      #Adds the id number with letter B for Bonanza identifier

                id_num += 1
                
                self.this_products.append(listing)     #Appends product dictionary to list

            if filters[3] is not None:
                id_num = 0
                for item in self.this_products:
                    item.update({'id':'B ' + str(id_num)})
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
                name = soup.find(itemprop='name')
                price = soup.find(class_='item_price')
                seller = soup.find(class_='booth_link')
                rating = soup.find(class_='sr-only')
                condition = soup.find(itemprop='itemCondition')
                images = soup.find_all(class_='image_thumbnail_container')
                info = soup.find_all(class_='additional_details_container')

                iframe = soup.find(class_='html_description').find('iframe')['src']

                descriptionLink = 'https://www.bonanza.com' + iframe    #Link to scrape the description from
                descriptionPage = requests.get(descriptionLink, headers=self.header(), timeout=15)
                
                soupDescription = BeautifulSoup(descriptionPage.content, 'html.parser')
                descriptionTextList = soupDescription.find_all('p')

                #Will store the all description text in a single string
                descriptionText = ''
                if descriptionTextList == []:
                    descriptionText = 'No description available'
                else:
                    for paragraph in descriptionTextList:
                        descriptionText = descriptionText + '\n' + paragraph.text

                #If the initial scrape returns a value other than None
                if name is not None:
                    name = name.text

                #If the initial scrape returns a value other than None
                if price is not None:
                    price = price.text.replace('\n', '').strip()

                #If the initial scrape returns a value other than None
                if seller is not None:
                    seller = seller.text

                #If the initial scrape returns a value other than None
                if rating is not None:
                    rating = rating.text
                    rating = re.sub('[^0-9.]', '', rating)

                #If the initial scrape returns a value other than None
                if condition is not None:
                    condition = condition.text

                #Stores all image links in a list and returns (empty list if no images)
                image_list = []
                if images is not None:
                    for i in images:
                        image_link = i.find('img')['src']
                        image_list.append(image_link)

                #If the initial scrape returns a value other than None
                if info is not None:
                    shipping = info[0].find_all('span', class_='details_text')

                    #For all the text in the shipping variable split at spaces
                    for i in shipping:
                        words = i.text.split(' ')
                    
                    #For the created list from split shipping
                    for i in words:

                        #Find a string value of 'FREE' or '$value' and store the string in shipping
                        if i == 'FREE' or i.startswith('$'):
                            shipping = i
                            break

                        #If there is no shipping info
                        else:
                            shipping = 'none'
                
                #Creating 'key':value pair for each scraped value
                self.listing['name'] = name
                self.listing['price'] = price
                self.listing['link'] = product_link
                self.listing['seller'] = seller
                self.listing['rating'] = rating
                self.listing['condition'] = condition
                self.listing['images'] = image_list
                self.listing['shipping'] = shipping
                self.listing['iframe'] = descriptionText
                self.listing['site'] = 'Bonanza'    #Used to distiguish when displaying on html site

if __name__ == '__main__':
    pass
    '''Bonanza = Bonanza()
    filters = [',', None, None, None]
    Bonanza.ExceptionsTest(Bonanza.site_scrape(input('Query: '), 100, filters))
    Bonanza.this_products
    Bonanza.ExceptionsTestInd(Bonanza.ind_site_scrape(int(5)))
    print(Bonanza.listing)'''
