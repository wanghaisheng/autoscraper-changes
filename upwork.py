import requests
import time
import os
import optparse
import random
import asyncio
from playwright.async_api import async_playwright
from datetime import datetime
import json
import platform
jobs = []

# Headers to fake the request as browser to avoid blocking
# from .util import *


async def get_playright(proxy:bool=False,headless:bool=True):
    print('proxy',proxy,'headless',headless)
    browser=''
    playwright =await  async_playwright().start()
    PROXY_SOCKS5 = "socks5://127.0.0.1:1080"
    # browser=''
    if 'Linux' in platform.system:
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

async def scrape_pl(search_query="python", topic='upwork'):
    # time.sleep(random.randint(10,50))
    # Sends a request

    start = time.time()
    url = "https://www.upwork.com/search/jobs/?q={}&per_page=50&sort=recency".format(search_query)
    print('user home url', url)
    browser = await  get_playright(False, False)
    context = await browser.new_context()
    context.add_cookies(
                json.loads(
os.environ.get('UPWORK_COOKIE')
                ))
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
                    result.append(job)    #     return jobs
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
asyncio.run(scrape_pl(search_query=keywords, topic=topic))
# scrape_data('youtube')
# scrape_data('nft')
