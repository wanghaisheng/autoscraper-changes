# Application: Web Crawler 
# Created by: Abemelech Mesfin Belachew
# Date: 4/2/2022
# Description: Web Crawler parses through websites and collects the urls inside a single url and continuously loops inside the collected urls to collect more urls


# Import Request, BeautifulSoup, Concurrent Future for the webcrawler app
# Request - to get access to the urls and html file
# BeautifulSoup - to search the html file for links
# Concurrent Future - for threading/parallel processing
import requests
from bs4 import BeautifulSoup
import concurrent.futures
import util
import os

from sitecrawl import crawl

class WebCrawler:

    def __init__(self,input_url):
        '''
        Web Crawler Initializer

        The initializer creates multitreader to reduce load time

        Argument:
        input_url: UserInput Url to start the webcrawler
        '''

        # Stores the user input into a list
        url_list = [input_url]

        # Use the concurrent.futures threading pool manager to create multiple threads
        # max_workers isn't set because the default value is based on the system (Version 3.5+)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            
            # A True while loop to continue the loop forever
            while(True):
                # The link_print function is mapped for every url in the url list and run parrallelly 
                # Return values are stores results
                results = executor.map(self.link_print, url_list)

                # Empty the url_list to repopulate
                url_list = []

                # Concatnate the returned urls into the url_list
                for result in results:
                    url_list += result

    def link_print(self, url):
        '''
        Returns the collected url found inside the requested url

        Arguments:
        url - the url that will be parsed

        '''

        # Storage of the list of urls collected
        url_collection = []

        # Try Except incase the request fails
        try:
            # Retrieves the urls data
            r = requests.get(url)
        except:
            return []

        # Store the url html text into beautiful soup to search
        soup = BeautifulSoup(r.text, 'html.parser')

        # Save all the <a> html tags into the variable to later parse through
        all_link = soup.find_all('a')

        # Log the urls site being parsed
        print(url)

        # Loop into every link collected and check if the link is "http" or "https"
        for http_link in all_link:

            # Try Excpet incase the <a> doesn't contain an href
            try:
                if "https://" in http_link.get('href') or "http://" in http_link.get('href'):
                    # If the link has an http or https print with an indentation and store the link
                    print(f"\t{http_link.get('href')}")
                    url_collection.append(http_link.get('href'))

            except:
                continue
        
        # After collecting all the links return the collection
        # return url_collection
        filename = '{}.txt'.format(url)

        date = util.current_date()
        file = os.path.join('websites', date, filename)
        util.write_text(file, url_collection)

def crawl(url):

    crawl.base_url = url
    crawl.deep_crawl(depth=10)

    print('Internal URLs:', crawl.get_internal_urls())
    print('External URLs:', crawl.get_external_urls())
    print('Skipped URLs:', crawl.get_skipped_urls())    
    filename_internal = '{}-internal.txt'.format(url)

    date = util.current_date()
    file = os.path.join('websites', date, filename_internal)
    util.write_text(file, crawl.get_internal_urls())

url='indiehackers.com'
w = WebCrawler(url)


