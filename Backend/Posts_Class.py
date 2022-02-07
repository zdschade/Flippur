from Ebay_Class import Ebay
from OfferUp_Class import OfferUp
from Letgo_Class import Letgo
from Bonanza_Class import Bonanza
from eCrater_Class import eCrater
from Craigslist_Class import Craigslist
from Average import product_Average

class Posts():
    def __init__(self, sites):
        self.siteIds = {}   #Store the Ids for each of the sites to be scraped
        
        #Create an object for each site to be scraped
        for i in sites:
            self.i = eval(i)()
            self.siteIds[i[0]] = self.i

    #Uses user search to execute initial scrape
    def posts(self, query, filters):
        average = product_Average(query)    #Average value calculated by sold items from Ebay

        all_products = []   #Where all site products are to be added
        filterisLetgo = False   #Used to place Letgo based on filter

        #Each of the sites will be visited to execute a scrape
        for key in self.siteIds:
            i = self.siteIds[key]
            i.ExceptionsTest(i.site_scrape(query, average, filters))      #Calling the exceptions test on the specific site

            #Letgo does not have a price to scrape from initial page, so if there is sort by price, Letgo products go at the bottom
            if key == 'L' and filters[3] is not None and 'price' in filters[3]:
                filterisLetgo = True
                continue    #Do not add Letgo to product sort before sort if the filter is by price

            all_products += i.this_products     #Add the specific sites products to the all site products

        #Only need to sortby if the user wants to
        if filters[3] is not None:
            sort_condition = filters[3].split()     #Split into key and inorder or reverse
            sort_key = sort_condition[0]            #Key to sort by

            #If the sort condition is not relevance
            if len(sort_condition) != 1: 
                sort_way = sort_condition[1]            #Which way the sorting will go

            #Sorts the list if necessary
            if sort_key == 'relevance':
                pass
            elif sort_way == 'd':
                all_products = sorted(all_products, key=lambda i: i[sort_key], reverse=True)
            else:
                all_products = sorted(all_products, key=lambda i: i[sort_key])

        #Will place Letgo at the end if the filter was by price
        if filterisLetgo:
            all_products += self.siteIds['L'].this_products
            #all_products += self.Letgo.this_products

        #Change value of OfferUp FREE from -5 back to FREE
        for item in all_products:
            if item['price'] == -5:  
                item.update({'price': 'FREE'})

            #Fixes prices to have dollar sign and two decimals
            try:
                item['price'] = "${:.2f}".format(float(item['price']))
            except ValueError:
                pass
        
        if average < float(filters[1]):
            average = "{:.2f} (Average is lower than selected value difference)".format(average)
        else:
            average = "{:.2f}".format(average)

        all_products.insert(0, average)     #Add average to the all_products list

        return all_products     #Return the all sites products list

    #Uses user selected product to execute specific scrape
    def ind_posts(self, ids):   
        #Each site has a specific ID e.g. Ebay's first scraped product is 'E 0'
        ids = ids.split()   #Splits the ID into an letter and number
        
        letter = ids[0]     #Used to select site
        number = int(ids[1])    #used to select listing from site

        siteProducts = self.siteIds[letter]       #Get the object for the specific site
        siteProducts.ExceptionsTestInd(siteProducts.ind_site_scrape(number))    #Calling ind exceptions test on the specific site

        return siteProducts.listing     #Returns the dictionary of the product'''

if __name__ == '__main__':
    pass
    '''sites = ['Letgo']
    new = Posts(sites)
    print(new.siteIds)
    filters = [',', 1, 'New', 'relevance']
    print(new.posts('chair', filters))'''
