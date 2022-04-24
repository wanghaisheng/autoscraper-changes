import requests
import time
import os
import optparse
import random
from bs4 import BeautifulSoup

import asyncio
from playwright.async_api import async_playwright
from datetime import datetime
import json
from undetected_driver import get_undetected_webdriver,get_undetected_webdriver_silence
import platform
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException, WebDriverException

from selenium.webdriver.common.action_chains import ActionChains
from supabase import create_client, Client
from dotenv import load_dotenv
import sys
import logging
from tenacity import *
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

logger = logging.getLogger(__name__)


# 加载文件
load_dotenv(".env")
supabase_url = os.environ.get('supabase_url')
supabase_url='https://bwrzzupfhzjzvuglmpwx.supabase.co'

print(supabase_url)
supabase_apikey = os.environ.get('supabase_apikey')
print(supabase_apikey)

supabase_db: Client = create_client(supabase_url=supabase_url, supabase_key=supabase_apikey)


# Headers to fake the request as browser to avoid blocking
# from .util import *


async def get_playright(proxy:bool=False,headless:bool=True):
    print('proxy',proxy,'headless',headless)
    browser=''
    playwright =await  async_playwright().start()
    PROXY_SOCKS5 = "socks5://127.0.0.1:1080"
    # browser=''
    if 'Linux' in platform.system():
        headless=True    
    if proxy==False:
        try:
            print("start pl without proxy")
            browser = await  playwright.firefox.launch(headless=headless)
            print('start is ok')
            return browser

        except:
            print('pl no proxy start failed')
            browserLaunchOptionDict = {
            "headless": headless,
            "proxy": {
                    "server": PROXY_SOCKS5,
            }
            } 
            browser = await playwright.firefox.launch(**browserLaunchOptionDict)
            # Open new page    
            return browser
    else: 
        print('proxy===',headless)
        browserLaunchOptionDict = {
        "headless": headless,
        "proxy": {
                "server": PROXY_SOCKS5,
        }
        } 
        browser = await playwright.firefox.launch(**browserLaunchOptionDict)
        # Open new page    

        return browser

def scrape_uc(search_query="tiktok", topic='upwork'):
    web_driver=get_undetected_webdriver_silence(True)    
    print('instance ok')
    #login 


    loginurl='https://www.upwork.com/ab/account-security/login'
    web_driver.get(loginurl)
    wait = WebDriverWait(web_driver, 10)
    
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#login_username')))
    mail =web_driver.find_element(By.CSS_SELECTOR, '#login_username')
    mail.clear()
    mail.send_keys('whs860603@gmail.com')
    next=web_driver.find_element(By.CSS_SELECTOR, '#login_password_continue').click()
    wait = WebDriverWait(web_driver, 10)
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#login_password')))

    passwd =web_driver.find_element(By.CSS_SELECTOR, '#login_password')
    passwd.clear()
    passwd.send_keys('tkYRr9apXDfWSZb')
    next=web_driver.find_element(By.CSS_SELECTOR, '#login_control_continue').click()
    wait = WebDriverWait(web_driver, 10)

    home = "https://www.upwork.com/search/jobs/?q={}&per_page=50&sort=recency".format(search_query)

    out =web_driver.get(home)        
    wait = WebDriverWait(web_driver, 10)
    html = web_driver.execute_script("return document.documentElement.outerHTML")
    upwork_soup = BeautifulSoup(html, 'html.parser')
    total_jobs = upwork_soup.find_all(lambda tag: len(tag.find_all()) == 0 and "found" in tag.text)
    # select_one('strong:-soup-contains("jobs found")')
    # [0].text
    print(total_jobs)
    count=upwork_soup.find_all("div", {"class": "pt-20 d-flex align-items-center justify-space-between"})[0].strong.text


    if ',' in count:
        count=count.replace(',','')
    count =int(count)
    # print(count)
    pages = int(count/50)+1
    print(pages)
    for p in range(pages):

        url = "https://www.upwork.com/search/jobs/?q={}&per_page=50&sort=recency&page={}".format(search_query,p)

        out =web_driver.get(url)        
        wait = WebDriverWait(web_driver, 10)
        html = web_driver.execute_script("return document.documentElement.outerHTML")
        upwork_soup = BeautifulSoup(html, 'html.parser')
        # website = upwork_soup.select('section.up-card-section.up-card-list-section.up-card-hover')        
        # website = upwork_soup.find_all('section', {'class':''})
        # website = upwork_soup.find_all('section', {'class':'up-card-hover'})

        # print('length',len(website))
        counter = 0
        for i in upwork_soup.find_all('a'):
            print(i)
            if i.parent.name == 'h4':
                title = (i.find("up-c-line-clamp").text)
                print(title)
                desc = (upwork_soup.find_all('span', {"class":"js-description-text"})[counter].text[0:(soup.find_all('span', {"class":"js-description-text"})[counter].text.find('.') + 1)] + " (...)\n\n\n\n")
                link = upwork_soup.find_all("a", {"class":"job-title-link break visited"})[counter]['href']
                strong = upwork_soup.find_all("strong", {"class":"js-budget"})[counter]
                price = strong.find("span").text.strip()
                xp = upwork_soup.find_all("strong", {"class":"js-contractor-tier"})[counter].text
                link = f'https://www.upwork.com/freelance-jobs/apply{link[4:]}'
                print('---',link)
                counter=counter+1
            for job_link in link:
                if job_link.has_attr('href'):

                    half_link = job_link['href']
                    job_page_link = "https://upwork.com" + half_link
                    web_driver.get(job_page_link)
                    time.sleep(10)
                    html = web_driver.execute_script("return document.documentElement.outerHTML")
                    job_page_soup = BeautifulSoup(html, 'html.parser')                    
                    job_type = job_page_soup.find_all('strong', {'class':'js-type'})[0].text.strip(" \n\t\r")
                    job_level = job_page_soup.find_all('span', {'class':'js-contractor-tier'})[0].text.strip(" - \n\t\r")
                    print(job_level)

                    try:
                        job_budget = job_page_soup.find_all('span', {'data-itemprop':'baseSalary'})[0].text.strip(" -  \n\t\r")
                    except:
                        job_budget = "No Data"
                    try:
                        job_estimated_time = job_page_soup.find_all('span', {'class':'js-duration'})[0].text.strip("Est. Time -  : \n\t\r ")
                    except:
                        job_estimated_time = "No Data"
                    job_posted_time = job_page_soup.find_all('time', {'data-itemprop':'datePosted'})[0].text.strip(" -  \n\t\r")
                    job_proposals = job_page_soup.find_all('small', {'class':'display-inline-block m-sm-top m-md-right'})[0].text
                    try:
                        job_country = job_page_soup.find_all('strong', {'class':'text-muted client-location'})[0].text
                    except:
                        job_country = "No Data"

                    job_detail = job_page_soup.find_all('p', {'class':'break'})[0].text
                    try:
                        job_skill = job_page_soup.find_all('a', {'class':'o-tag-skill m-0-left m-0-top m-md-bottom'})[0].text
                    except:
                        job_skill = "No Data"
                    job_div = job_page_soup.find_all('div', {'id':'form'})[0].text       
                    job ={
                        "job_title":job_title,
                        "job_type":job_type,
                        "job_level":job_level,
                        "job_budget":job_budget,
                        "job_estimated_time":job_estimated_time,
                        "job_posted_time":job_posted_time,
                        "job_page_link ": job_page_link,
                        "job_detail ": job_detail,
                        "job_skill ": job_skill,
                        "job_div ": job_div,
                        "proposals ": job_proposals,
                        "location ": job_country
                    }
                    print(job)
                    supabaseop("upwork_jobs",job)


@retry(stop=stop_after_attempt(3), before=before_log(logger, logging.DEBUG))
def supabaseop(tablename,users):
    try:
        data = supabase_db.table(tablename).insert(users).execute()    
    except:
        raise Exception


async def scrape_pl(search_query="python", topic='upwork'):
    # time.sleep(random.randint(10,50))
    # Sends a request

    start = time.time()
    url = "https://www.upwork.com/search/jobs/?q={}&per_page=50&sort=recency".format(search_query)
    print('user home url', url)
    browser = await  get_playright(False, False)
    context = await browser.new_context()
    # print(os.environ.get('UPWORK_COOKIE'))
    # await context.add_cookies(
                # json.loads(os.environ.get('UPWORK_COOKIE')))
    await context.add_cookies(
                    json.load(
                        open(
                            'cookie.json', 
                            'r'
                        )
                    )
                )                       
    homepage = await context.new_page()
    try:
        res = await homepage.goto(url)
        # print(parser.find(string=re.compile("found")))
        # print(parser.find_all(attrs={"data-test": "jobs-count"}))
        avatar=homepage.locator('.nav-d-none > button:nth-child(1) > div:nth-child(1) > img:nth-child(2)')
        print('is login in')
    
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
            print('deal page',p+1,url)
            fenyepage = await context.new_page()

            await fenyepage.goto(url)
            jobs=fenyepage.locator('.up-card-list-section')
            jobcount=await jobs.count()
            print('jobcount',jobcount)
            if jobcount>0:
                for i in range(0,jobcount):
                    # time.sleep(random.randint(10, 30))    
                    print('no',i,'in this page',p)
                    title= jobs.nth(i).locator("div > div> h4 >a")
                    title=await title.text_content()
                    print(title,'-')
                    href=await jobs.nth(i).locator("div > div> h4 > a").get_attribute('href')
                    print('111')
                    id =href.replace('/job/','').replace('/','')
                    url='https://www.upwork.com'+href
                    print('222')

                    tagscount=jobs.nth(i).locator('div.up-skill-wrapper>a')
                    tags=''
                    for i in range(await tagscount.count()):
                        tags=tags+','+await tagscount.nth(i).text_content()

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
                    await asyncio.sleep(6)                     
                     
                      #     return jobs
        filename = 'data/'+topic+'/{}.json'.format(search_query)

        date = current_date()
        file = os.path.join(search_query, date, filename)
        write_text(file, result)

    except:
        print('error')
def ensure_dir(file):
    directory = os.path.abspath(os.path.dirname(file))
    if not os.path.exists(directory):
        os.makedirs(directory)


def write_text(file: str, text: str):
    ensure_dir(file)
    with open(file, mode='w') as f:
        f.write(text)        
def getOpts():
    parser = optparse.OptionParser()
    parser.add_option('-m', '--module', dest='module',
                      default='ruijie_eg', type=str, help='Module name')
    parser.add_option('-k', '--keywords', dest='keywords',
                      default='genshin', type=str, help='keyword list')
    parser.add_option('-n', '--topic', dest='topic',
                      default='genshin', type=str, help='topic name')
    parser.add_option('-p',
                      '--proxypool',
                      dest='proxypool',
                      default='https://proxypool.scrape.center/random',
                      type=str,
                      help='Host and port of ProxyPool (default = 127.0.0.1:5010)')
    parser.add_option('-d',
                      '--delay',
                      default=5,
                      type=float,
                      dest='delay',
                      help='Seconds to delay between requests for each proxy (default = 5)')
    parser.add_option('-T', '--threads', default=15, type=int,
                      dest='threads', help='Number of threads (default = 15)')
    parser.add_option('-t', '--timeout', default=6, type=float,
                      dest='timeout', help='Seconds of Timeout (default = 6)')

    (opts, args) = parser.parse_args()
    return opts, args
def current_time():
    return datetime.now().astimezone().strftime('%Y-%m-%d %H:%M:%S %z')


def current_date():
    return datetime.now().astimezone().strftime('%Y-%m-%d')

# print(scrape_data())
opts, args = getOpts()
keywords = opts.keywords
topic = opts.topic
keywords='tiktok'
# asyncio.run(scrape_data(search_query=keywords, topic=topic))
asyncio.run(scrape_uc(search_query=keywords, topic=topic))
# scrape_data('youtube')
# scrape_data('nft')
