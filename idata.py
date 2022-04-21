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


async def scrape_pl(search_query="python", topic='upwork',db='CFLS'):
    # time.sleep(random.randint(10,50))
    # Sends a request
    print('=============',search_query,topic,db)
    shuobo=False
    if db=='CDMD':
        shuobo =True
    start = time.time()

    loginurl='https://user.cn-ki.net/login'

    url = "https://search.cn-ki.net/search?keyword={}&db={}".format(
        search_query,db)
    print('user home url', url)
    browser = await get_playright(False, False)
    context = await browser.new_context()
    # print(os.environ.get('UPWORK_COOKIE'))
    # await context.add_cookies(
    # json.loads(os.environ.get('UPWORK_COOKIE')))
    await context.add_cookies(
        json.load(
            open(
                'idata-cookie.json',
                'r'
            )
        )
    )
    homepage = await context.new_page()
    try:
        res = await homepage.goto(loginurl)
        ua = os.environ.get('ua')
        us = os.environ.get('us')
        

        await homepage.fill('#num', ua)
        #passwd
        await homepage.fill('#passwd', us)
        await homepage.locator('#app > div > div > div:nth-child(3) > div > div > div.card__title.card__title--primary > div:nth-child(3) > button > div').click()
        time.sleep(3)
        res = await homepage.goto(url)
        # print(parser.find(string=re.compile("found")))
        # print(parser.find_all(attrs={"data-test": "jobs-count"}))
        avatar = homepage.locator(
            'span.mdui-float-right:nth-child(4) > a:nth-child(1)')
        print('is login in')
        await homepage.fill('#keyword',search_query)
        count=0
        try:
        
            count = homepage.locator('.pagerTitleCell')
            count = await count.text_content()
            print('count', count)
            count = count.strip().replace('找到', '').replace('条结果', '')
        except:

            error = homepage.locator('.TitleLeftCell')
            error_msg = await error.text_content()
            print('error_msg',error_msg)
            error_flag=True
            while error_flag:
                if '系统' in error_msg:
                    await homepage.reload()
                    await homepage.locator('.mdui-btn-dense').click()
                    time.sleep(6)
                    print('detected error refresh')
                    print('retry count no')
                    count = homepage.locator('.pagerTitleCell')
                    count = await count.text_content()
                    print('count', count)
                    count = count.strip().replace('找到', '').replace('条结果', '')
                    if count:
                        error_flag=False
                        break
                else:
                    print('no error at all')

                    error_flag=False
                    break

            print('retry count no')
            count = homepage.locator('.pagerTitleCell')
            count = await count.text_content()
            print('count', count)
            count = count.strip().replace('找到', '').replace('条结果', '')

        if ',' in count:
            count = count.replace(',', '')
        print(count)
        count = int(count)
        pages = int(count/20)+1
        result = []
        print(pages)
        for p in range(pages):
            print(p, '---')
            prefix = 'https://search.cn-ki.net/search?keyword={}&db={}'.format(
                search_query,db)
            print('prefix', prefix)
        # 3089
        # https://www.upwork.com/nx/jobs/search/?q=tiktok&sort=recency
        # 550
            url = prefix+'&p='+str(p+1)
            print('deal page', p+1, url)
            # fenyepage = await context.new_page()
            fenyepage =homepage
            await fenyepage.fill('#keyword',search_query)
            print('type input',search_query)

            # await fenyepage.goto(url)
            try:
            
                count = fenyepage.locator('.pagerTitleCell')
                count = await count.text_content()
                print('count', count)
                count = count.strip().replace('找到', '').replace('条结果', '')
            except:

                error = fenyepage.locator('.TitleLeftCell')
                error_msg = await error.text_content()
                print('error_msg',error_msg)
                error_flag=True
                while error_flag:
                    if '系统' in error_msg:
                        await fenyepage.reload()
                        await homepage.locator('.mdui-btn-dense').click()

                        time.sleep(6)
                        print('detected error refresh')
                        print('retry count no')
                        count = fenyepage.locator('.pagerTitleCell')
                        count = await count.text_content()
                        print('count', count)
                        count = count.strip().replace('找到', '').replace('条结果', '')
                        if count:
                            error_flag=False
                            break
                    else:
                        print('no error at all')

                        error_flag=False
                        break

            jobs = fenyepage.locator('a[href^="/doc_detail"]')
            jobcount = await jobs.count()
            print('jobcount', jobcount)
            await asyncio.sleep(1)
            if jobcount > 0:
                for i in range(0, jobcount):
                    # time.sleep(random.randint(10, 30))
                    print('no ', i, ' of total paper ',
                            jobcount, 'in this page', p)
                    # title= jobs.nth(i).locator("div > h3 >a")
                    # title=await title.text_content()
                    # print('title',title)
                    # href= jobs.nth(i).locator('a[href^="/shop/url/"]')
                    # print(href)
                    href = await jobs.nth(i).get_attribute('href')
                    print('href', href)

                    url = 'https://search.cn-ki.net'+href

                    jobpage = await context.new_page()

                    await jobpage.goto(url)
                    title = jobpage.locator('.headline')
                    title = await title.text_content()
                    print('title', title)
                    await asyncio.sleep(3)
                    container = jobpage.locator('div.card >div.container >div.layout')
                    journal=''
                    institute=''
                    journal_time=''
                    keywords=''
                    author=''
                    print(await container.count(),'jibnexinxi ')
                    for i in range(0, await container.count()):
                        alltext= await container.nth(i).text_content()
                        alltext=alltext.strip().replace('\r', '').replace('\n', '')
                        alltext=alltext.replace(' ','')
                        print('jibenxinx--',alltext)
                        if '单位' in alltext:
                            institute = alltext.replace('单位','').strip()
                        elif '期刊' in alltext:
                            journal = alltext.replace('期刊','').strip()
                        elif '时间' in alltext:
                            journal_time= alltext.replace('时间','').strip()
                        elif '关键词' in alltext:
                            keywords= alltext.replace('关键词','').strip()
                        elif '作者' in alltext:
                            author= alltext.replace('作者','').strip()
                                                        
                    abstract = jobpage.locator('.card__text')
                    abstract = await abstract.text_content()
                    abstract = abstract.strip().replace('\r', '').replace('\n', '')
                    print('abstract',abstract)


                    async with jobpage.expect_download() as download_info:
                        # Perform the action that initiates download
                        # await jobpage.click("a.success--text")
                        await jobpage.click('text=下载')
                    download = await download_info.value
                    print('downloadinfo',download)

                    # Wait for the download process to complete
                    path = await download.path()
                    print('downloadpath',path)

                    filename=download.suggested_filename
                    print(filename)

                    await download.save_as('./data/bianmi/'+filename)
        # Making a list of dicts
                    paper = {
                        "url": url,
                        "title": title,
                        "author": author,
                        "keywords": keywords,
                        "shuobo":shuobo,
                        "abstract": abstract,
                        "institute": institute,
                        "journal":journal,
                        "journal_time":journal_time,
                        "topic": topic
                    }
                    print('save db')
                    data = supabase.table("papers_bianmi").insert(paper).execute()
                    print('delay for later')
                    # await asyncio.sleep(3)
                    # jobpage.close()
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

asyncio.run(scrape_pl(search_query=keywords, topic=topic,db='CDMD'))

# asyncio.run(scrape_pl(search_query=keywords, topic=topic,db='CFLS'))

# scrape_data('youtube')
# scrape_data('nft')
