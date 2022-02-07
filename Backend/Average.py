from bs4 import BeautifulSoup
import re
import requests
import sys

#May need to add try and except in for this one because it is only a value
def product_Average(search):
    no_average = sys.float_info.max     #This is infinity because there were not any sold listings on eBay
    
    try:
        products = []

        #for page_num in range(2, 3):
        url = 'https://www.ebay.com/sch/i.html?_nkw=' + search.replace(' ', '+') + '&LH_Sold=1'

        page = requests.get(url, timeout=15)
        page.raise_for_status()     #For HTTP exception

        if page.status_code == 200:
            soup = BeautifulSoup(page.content, 'html.parser')
            all_prod = soup.find_all('div', class_='s-item__detail s-item__detail--primary')

            for prod in all_prod:
                price = prod.find('span', class_='s-item__price') 

                if price is None:
                    continue
                
                price = price.text.replace(' to ',':').split(':')   #The two prices are now separate

                #Gets the highest price of the two
                if len(price) == 1:
                    price = price[0]
                else:
                    price = price[1]

                strip_price = re.sub('[^0-9.]', '', price)

                #Removes all characters that are not a number or a decimal
                if strip_price != '':
                    products.append(strip_price)

            products.sort(key = float)    #Products sorted in order of value via float
            
            #If there are no sold items, the average is very large so items are not omitted
            if len(products) == 0:
                return no_average

            #If there is only one sold item
            elif len(products) == 1:
                return float(products[0])

            #Find the lower quartile
            low1 = products[int(len(products) / 4)]
            low2 = products[int((len(products) / 4) + 1)]
            lowQ = (float(low1) + float(low2)) / 2

            #Find the upper quartile for short products list
            if len(products) < 5:
                up1 = products[int(len(products) * 0.75)]
                upQ = (float(up1) + float(up1))/ 2

            #Find the upper quartile
            else:
                up1 = products[int(len(products) * 0.75)]
                up2 = products[int((len(products) * 0.75) + 1)]
                upQ = (float(up1) + float(up2)) / 2

            #Used to find upper and lower limits
            iqr = upQ - lowQ
            iqr_multi = iqr * 1.5

            #Find the outlier numbers
            low_lim = lowQ - iqr_multi
            up_lim = upQ + iqr_multi

            #Find where the lower outliers start via index
            low_index = 0
            while float(products[low_index]) < low_lim:
                low_index += 1

            #Find where the upper outlier starts via index
            up_index = len(products) - 1
            while float(products[up_index]) > up_lim:
                up_index -= 1

            up_index += 1   #Add one to the upper index to splice correctly

            del products[up_index:]     #Splice out the upper outliers
            del products[:low_index]    #Splice out the lower outliers

            #Sums the values for the prices in the spliced list
            value = 0
            for prices in products:
                value += float(prices)

            #Used for the average price calculator
            divisor = len(products)
            dividend = round(value, 2)

            return round((dividend / divisor), 2)    #Average purcahse price

    #Catches HTTP errors
    except requests.HTTPError as e:
        print({'Error': str(e.response.status_code) + ': ' + e.response.reason})
        return no_average

    #Catches Connection errors
    except requests.ConnectionError:
        print({'Error': 'Connection Error. Check your internet connection.'})
        return no_average

    #Catches all both timeout errors
    except requests.Timeout:
        print({'Error': 'Timeout Error.'})
        return no_average

    #Handles any other error that may occur
    except requests.RequestException:
        print({'Error': 'Unknown Error.'})
        return no_average

if __name__ == '__main__':
    pass
    #print(product_Average('hyperboom'))
