import requests
import bs4
import json
import time
import random
import os
import re
import lxml.html
from utils import *
import asyncio
from playwright.async_api import async_playwright
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException, WebDriverException

from selenium.webdriver.common.action_chains import ActionChains
jobs = []

# Headers to fake the request as browser to avoid blocking
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:66.0) Gecko/20100101 Firefox/66.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "DNT": "1",
    "Connection": "close",
    "Upgrade-Insecure-Requests": "1"
}


headers = dict(headers)

def scrape_uc(search_query="python", topic='upwork'):
    web_driver=get_undetected_webdriver()
    url = "https://www.upwork.com/search/jobs/?q={}&per_page=50&sort=recency".format(search_query)
    print(url)
    out =web_driver.get(url)        
    wait = WebDriverWait(web_driver, 10)    
    try:
        count=web_driver.find_element(By.CSS_SELECTOR, "div.pt-20:nth-child(3) > div:nth-child(1) > span:nth-child(1) > strong:nth-child(1)")
        print(count.text)
    except:
        print('no result')


async def scrape_data(search_query="python", topic='upwork'):
    # time.sleep(random.randint(10,50))
    # Sends a request
    start = time.time()
    url = "https://www.upwork.com/search/jobs/?q={}&per_page=50&sort=recency".format(search_query)
    print('user home url', url)
    browser,res = await  get_playright('',url, False)
    context = await browser.new_context()

    page = await context.new_page()
    try:
        print('goto url')
        res = await page.goto(url)
        print(res)
        # print(parser.find(string=re.compile("found")))
        # print(parser.find_all(attrs={"data-test": "jobs-count"}))
        prefix = 'https://www.upwork.com/search/jobs/url?q={}&per_page=50&sort=recency&page='
        count =  page.locator('div.pt-20:nth-child(3) > div:nth-child(1) > span:nth-child(1) > strong:nth-child(1)')
        
        print(await count.text_content())

        tree = lxml.html.fromstring(url.content)
        print(tree.cssselect("div.pt-20:nth-child(3)"))
        # print('-',tree.xpath('/html/body/div[1]/div/span/div/div/main/div/div/div/div/div[2]/div/div/div/section/div[3]/div[1]/span/strong') )
        print('===', parser.find_all('span', string=re.compile('jobs found')))
        print('--', parser.find_all("span",
                                    attrs={"data-test": "jobs-count"}))
        pages = int(2980/50)+1
        for page in range(pages):
            url = requests.get(prefix+str(page), headers=headers)
        # Parses the html output
            parser = bs4.BeautifulSoup(url.content, 'lxml')
            # Gathering all the information
            titles = [i.text.replace("\n", "") for i in parser.find_all(
                'a', class_="job-title-link break visited")]
            print(len(titles))
            urls = [i['href'] for i in parser.find_all(
                'a', class_="job-title-link break visited")]
            descriptions = [i.text for i in parser.find_all(
                'span', class_="js-description-text")]

            # Making a list of dicts
            for i in range(10):
                print(i)
                job = f"{{ 'title' : '{titles[i]}', 'url' : 'https://upwork.com/{urls[i]}' , 'description' : '''{ descriptions[i] }''' }}"
                jobs.append(eval(job))
    #     return jobs
        filename = 'data/'+topic+'/{}.json'.format(search_query)

        date = current_date()
        file = os.path.join(search_query, date, filename)
        write_text(file, jobs)

    except:
        print('error')
# print(scrape_data())
opts, args = getOpts()
keywords = opts.keywords
topic = opts.topic
# asyncio.run(scrape_data(search_query=keywords, topic=topic))
scrape_uc(search_query=keywords, topic=topic)
# scrape_data('youtube')
# scrape_data('nft')
