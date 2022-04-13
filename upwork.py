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


async def scrape_pl(search_query="python", topic='upwork'):
    # time.sleep(random.randint(10,50))
    # Sends a request
    start = time.time()
    url = "https://www.upwork.com/search/jobs/?q={}&per_page=50&sort=recency".format(search_query)
    print('user home url', url)
    browser = await  get_playright(False, True)
    context = await browser.new_context()

    homepage = await context.new_page()
    try:
        res = await homepage.goto(url)
        # print(parser.find(string=re.compile("found")))
        # print(parser.find_all(attrs={"data-test": "jobs-count"}))

        count =  homepage.locator('div.pt-20:nth-child(3) > div:nth-child(1) > span:nth-child(1) > strong:nth-child(1)')
        count =await count.text_content()

        if ',' in count:
            count=count.replace(',','')
        print(count)
        count=int(count)
        pages = int(count/10)+1
        result=[]
        print(pages)
        for p in range(pages):
            print(p,'---')
            prefix = 'https://www.upwork.com/nx/jobs/search/?q={}&sort=recency'.format(search_query)
            print('prefix',prefix)
        #3089
        # https://www.upwork.com/nx/jobs/search/?q=tiktok&sort=recency  
        # 550            
            url=prefix+'&page='+str(p+1)
            print('goto url',url)
            fenyepage = await context.new_page()

            await fenyepage.goto(url)
            jobs=fenyepage.locator('.up-card-list-section')
            jobcount=await jobs.count()
            print('jobcount',jobcount)
            if jobcount>0:
                for i in range(0,jobcount):
                    print('no',i,'in this ',p)
                    title= jobs.nth(i).locator("div > div> h4 >a")
                    title=await title.text_content()
                    print(title,'-')
                    href=await jobs.nth(i).locator("div > div> h4 >a").get_attribute('href')
                    tagscount=jobs.nth(i).locator('div.up-skill-wrapper>a')
                    tags=''
                    for i in range(await tagscount.count()):
                        tags=tags+','+await tagscount.nth(i).text_content()
                    id =href.replace('/job/','').replace('/','')
                    url='https://www.upwork.com'+href
                    jobpage = await context.new_page()

                    await jobpage.goto(url)
                    des=jobpage.locator('.job-description')
                    # print('des',des)
                    des=await des.text_content()
                    # print('des',des)

                    des =des.strip().replace('\r','').replace('\n','')
                    # print('des',des)

            # Making a list of dicts
                    job = {"id":id,
                    "url":url,
                    "title":title,
                    "tags":tags,
                    "des":des
                    }
                    print('===',job)
                    result.append(job)
                    print('add one',i)
    #     return jobs
        filename = 'data/'+topic+'/{}.json'.format(search_query)

        date = current_date()
        file = os.path.join(search_query, date, filename)
        write_text(file, result)

    except:
        print('error')
# print(scrape_data())
opts, args = getOpts()
keywords = opts.keywords
topic = opts.topic
keywords='tiktok'
# asyncio.run(scrape_data(search_query=keywords, topic=topic))
asyncio.run(scrape_pl(search_query=keywords, topic=topic))
# scrape_data('youtube')
# scrape_data('nft')
