import pandas as pd
import numpy as np

import requests
from bs4 import BeautifulSoup

import random
import time

import json

import gspread
from datetime import datetime

class ClogauScraper:

    def write_to_googlesheets(self, df, filename):
        ''' Creates a google sheet, and pushes the product data from a pandas dataframe 
            Parameters:
                df : pandas dataframe with product data

            Returns:
                None
        '''

        try:
            sa = gspread.service_account('config/service_account.json')
            sh = sa.open(filename)
            wks = sh.worksheet('Sheet1')

            wks.update([df.columns.values.tolist()] + df.values.tolist())
            
            f = open('config/email.json')
            configdata = json.load(f)
            sheets_email = configdata['config']['email']
            f.close()

            sh.share(sheets_email, perm_type='user', role='writer')
        except Exception as e:
            print(e)

        return 
    
    def run(self):
        ''' Scrapes ClogauOutlet product pages, starting from a list of all products from the sitemap''' 

        # Acquire list of all product links from website sitemap.xml
        sitemap_url = 'https://www.clogauoutlet.co.uk/sitemap-product-0.xml.gz'
        soup = BeautifulSoup(requests.get(sitemap_url).text, 'lxml')

        url_list = []
        for loc in soup.select('url > loc'):
            url_list.append(loc.text)

        products = []
        skus = []
        mpns = []
        rrps = []
        cur_prices = []
        urls = []
            
        for url in url_list[0:5]:
            print("Scraping " + url)
            page = requests.get(url)
            soup = BeautifulSoup(page.text, 'html.parser')
            
            prod = soup.find(name='h1', attrs={'class':"productName_title"})
            products.append(prod.text if prod else 'None')

            sku = url.split('.html')[0].split('/')[-1]
            skus.append(sku if sku else 'None')

            mpn_soup = soup.find(name='script', attrs={'type':"application/ld+json"})
            json_object = json.loads(mpn_soup.contents[0])
            mpns.append(json_object['mpn'] if json_object['mpn'] else 'None')

            sold_out_button = soup.find(name='button', attrs={'class':'productAddToBasket productAddToBasket-soldOut'})

            rrp = soup.find(name='p', attrs={'class':"productPrice_rrp"})
            if rrp:
                rrps.append(rrp.text.strip('RRP: '))
            else:
                if sold_out_button:
                    rrps.append('SoldOut')
                else:
                    rrps.append('None')

            cur_pr = soup.find(name='p', attrs={'class':"productPrice_price"})
            if cur_pr:
                cur_prices.append(cur_pr.text.strip())
            else:
                if sold_out_button:
                    cur_prices.append('SoldOut')
                else:
                    cur_prices.append('None')

            urls.append(url)
            time.sleep(1 + random.random())

        now = datetime.now()
        dt_string = now.strftime("%Y-%m-%d")
        dt_array = [dt_string] * len(url_list)
        # Create pandas dataframe
        data = {'Product':products,
                    'SKU':skus,
                    'MPN':mpns,
                    'RRP':rrps,
                    'CurrentPrice':cur_prices, 
                    'URL':urls,
                    'Date':dt_string}
        self.df = pd.DataFrame(data=data)

        self.results = []
        for i in range(len(self.df)):
            self.results.append(self.df.iloc[i].tolist())
        
        self.filename = 'CloguaGold_Product_Scrape'

        self.write_to_googlesheets(self.df, self.filename)

if __name__ == '__main__':
    scraper = ClogauScraper()
    scraper.run()






