import time
import os
import optparse
import random
import asyncio
from playwright.async_api import async_playwright
from datetime import datetime
import json
# from undetected_driver import get_undetected_webdriver
import platform
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException, WebDriverException

# from selenium.webdriver.common.action_chains import ActionChains

from supabase import create_client, Client
from dotenv import load_dotenv

# 加载文件
load_dotenv(".env")

supabase_url = os.environ.get('supabase_url')
supabase_apikey = os.environ.get('supabase_apikey')
print(supabase_url)

supabase: Client = create_client(
    supabase_url=supabase_url, supabase_key=supabase_apikey)

jobs = []

# Headers to fake the request as browser to avoid blocking
# from .util import *


async def get_playright(proxy: bool = False, headless: bool = True):
    print('proxy', proxy, 'headless', headless)
    browser = ''
    playwright = await async_playwright().start()
    PROXY_SOCKS5 = "socks5://127.0.0.1:1080"
    # browser=''
    if 'Linux' in platform.system():
        headless = True
    if proxy == False:
        try:
            print("start pl without proxy")
            browser = await playwright.firefox.launch(headless=headless)
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
        print('proxy===', headless)
        browserLaunchOptionDict = {
            "headless": headless,
            "proxy": {
                "server": PROXY_SOCKS5,
            }
        }
        browser = await playwright.firefox.launch(**browserLaunchOptionDict)
        # Open new page

        return browser


# def scrape_uc(search_query="tiktok", topic='upwork'):
#     web_driver = get_undetected_webdriver()
#     url = "https://www.upwork.com/search/jobs/?q={}&per_page=50&sort=recency".format(
#         search_query)

#     out = web_driver.get(url)
#     wait = WebDriverWait(web_driver, 10)
#     try:
#         web_driver.find_element(
#             By.CSS_SELECTOR, "img[class^='captcha_verify_img_slide']")

#         piece_url = wait.until(EC.element_to_be_clickable(
#             (By.CSS_SELECTOR, "img[class^='captcha_verify_img_slide react-draggabl']"))).get_attribute('src')
#     except:
#         print()


async def scrape_pl(search_query="python", topic='upwork', db='CFLS'):
    # time.sleep(random.randint(10,50))
    # Sends a request
    print('=============', search_query, topic, db)
    shuobo = False
    if db == 'CDMD':
        shuobo = True
    start = time.time()

    loginurl = 'https://user.cn-ki.net/login'

    url = "https://search.cn-ki.net/search?keyword={}&db={}".format(
        search_query, db)
    print('user home url', url)
    browser = await get_playright(False, False)
    context = await browser.new_context()
    # print(os.environ.get('UPWORK_COOKIE'))
    # await context.add_cookies(
    # json.loads(os.environ.get('UPWORK_COOKIE')))
    # await context.add_cookies(
    #     json.load(
    #         open(
    #             'idata-cookie.json',
    #             'r'
    #         )
    #     )
    # )
    homepage = await context.new_page()
    try:
        res = await homepage.goto(loginurl)
        ua = os.environ.get('ua')
        us = os.environ.get('us')

        await homepage.fill('#num', ua)
        # passwd
        await homepage.fill('#passwd', us)
        await homepage.locator('#app > div > div > div:nth-child(3) > div > div > div.card__title.card__title--primary > div:nth-child(3) > button > div').click()
        res = await homepage.goto('https://search.cn-ki.net/advance_search')
        # print(parser.find(string=re.compile("found")))
        # print(parser.find_all(attrs={"data-test": "jobs-count"}))
        time.sleep(3)

        avatar = homepage.locator(
            'span.mdui-float-right:nth-child(4) > a:nth-child(1)')
        print('is login in')

        await homepage.fill('#keyword', search_query)
        print('input keyword')
        time.sleep(1)
        if db=='CDMD':
            print('choose shuobo')
            await homepage.locator('label.mdui-radio:nth-child(3)').click()   
        # await homepage.locator('div.mdui-col-xs-2:nth-child(3)').click()
        await homepage.locator('div.mdui-col-xs-2:nth-child(3)').click()
        print('action to search')
        time.sleep(3)

        await homepage.locator('div.mdui-col-xs-10:nth-child(1) > span:nth-child(2)').click()
        # count = 0
        # try:

        #     count = homepage.locator('.pagerTitleCell')
        #     count = await count.text_content()
        #     print('count', count)
        #     count = count.strip().replace('找到', '').replace('条结果', '')
        # except:

        #     error = homepage.locator('.TitleLeftCell')
        #     error_msg = await error.text_content()
        #     print('error_msg', error_msg)
        #     error_flag = True
        #     while error_flag:
        #         if '系统' in error_msg:
        #             await homepage.reload()
        #             await homepage.locator('.mdui-btn-dense').click()
        #             time.sleep(6)
        #             print('detected error refresh')
        #             print('retry count no')
        #             count = homepage.locator('.pagerTitleCell')
        #             count = await count.text_content()
        #             print('count', count)
        #             count = count.strip().replace('找到', '').replace('条结果', '')
        #             if count:
        #                 error_flag = False
        #                 break
        #         else:
        #             print('no error at all')

        #             error_flag = False
        #             break

        #     print('retry count no')

        count = homepage.locator('div.mdui-col-xs-2:nth-child(2)')
        count = await count.text_content()
        print('total papers', count)
        count = count.strip().replace('找到', '').replace('条结果', '')

        if ',' in count:
            count = count.replace(',', '')
        count = int(count)
        pages = 1
        if count > 20:
            pages = int(count/20)+1
        result = []
        print('need click times',pages)
           
        for p in range(pages):
            jobs = homepage.locator('#result_main > div.mdui-row')
            
            jobcount = await jobs.count()
            await asyncio.sleep(1)
            print('this pagi',jobcount)
            # jobs = jobs[0+p*20:0+p*19+19]
            for i in range(0+p*20, p*19+19):
                print('dealing index',i,'paper')
                url = await jobs.nth(i).locator('div:nth-child(1) > h3:nth-child(1) > a:nth-child(1)').get_attribute('href')
                url = 'https://search.cn-ki.net'+url
                print('url',url)
                title = await jobs.nth(i).locator('div:nth-child(1) > h3:nth-child(1) > a:nth-child(1)').text_content()
                print('title',title)

                raw = await jobs.nth(i).locator('div:nth-child(1) > div:nth-child(2)').text_content()
                raw=raw.strip().split('，')
                raw = list(filter(None, raw))
                print('raw',raw)
                if len(raw)==3:
                    author = raw[0].strip()
                    institute = raw[1].strip()
                    journal=''
                    journal_time=''
                    if ' 'in institute:
                        journal=institute.split(' ')[0]
                        journal_time=institute.split(' ')[1]
                    shuobo = raw[2].strip()

                else:
                    author = raw[0].strip()
                    # print('raw',raw[1])
                    institute=''
                    print('author',author)
                    journal = raw[1].strip().split(' ')[0]
                    print('journal',journal)

                    journal_time= raw[1].strip().split(' ')[1]
                    print('journal_time',journal_time)

                # journal_time= raw[1].strip().split(' ')[1]

                abstract = await jobs.nth(i).locator('div:nth-child(1) > div:nth-child(3)').text_content()
                pdflink = await jobs.nth(i).locator('div:nth-child(1) > div:nth-child(4) > a:nth-child(1)').get_attribute('href')
                print('pdflink',pdflink)

                paperbrief = {
                    "url": url.strip(),
                    "title": title,
                    "author": author,
                    "shuobo": shuobo,
                    "keywords": '',
                    "institute":institute,
                    "abstract": abstract.strip(),
                    "journal": journal,
                    "journal_time": journal_time,
                    "pdflink":pdflink,
                    "topic": topic,
                    "pdfdone":False
                }
                print('save db',paperbrief)
                data = supabase.table("papers_bianmi").insert(
                    paperbrief).execute()
                print('delay for later',data)

                # jobpage.close()
            await homepage.locator('.mdui-m-b-5').click()
            time.sleep(10)                
# create table papers_bianmi (
#   id bigint generated by default as identity primary key,
#   inserted_at timestamp with time zone default timezone('utc'::text, now()) not null,
#   updated_at timestamp with time zone default timezone('utc'::text, now()) not null,
#   url text,
#   title text,
#   author text,
#   keywords text,
#   abstract text,
#   topic text,
#   institute text
# );

    except:
        print('error')

def  cnki_mirror():
    # https://en.yaodeyo.com:92/scholar?start=768&q=%E4%BE%BF%E7%A7%98&hl=en&scisbd=1&as_sdt=0,5
# http://cnki.cn-ki.net/kns/brief/Default_Result.aspx?txt_1_sel=FT%24%25%3D%7C&txt_1_value1=%E4%BE%BF%E7%A7%98&txt_1_special1=%25&txt_extension=&currentid=txt_1_value1&dbJson=coreJson&dbPrefix=SCDB&db_opt=CJFQ%2CCDFD%2CCMFD%2CCPFD%2CIPFD%2CCCND%2CCJRF%2CCCJD&singleDB=SCDB&db_codes=CJFQ%2CCDFD%2CCMFD%2CCPFD%2CIPFD%2CCCND%2CCJRF%2CCCJD&singleDBName=&againConfigJson=false&action=scdbsearch&ua=1.11
    pass
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
                      default='便秘', type=str, help='keyword list')
    parser.add_option('-n', '--topic', dest='topic',
                      default='bianmi', type=str, help='topic name')
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
keywords = '便秘'
# asyncio.run(scrape_data(search_query=keywords, topic=topic))

asyncio.run(scrape_pl(search_query=keywords, topic=topic, db='CDMD'))

# asyncio.run(scrape_pl(search_query=keywords, topic=topic,db='CFLS'))

# scrape_data('youtube')
# scrape_data('nft')
