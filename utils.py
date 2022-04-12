#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: RogerRordo

from itertools import islice
from ast import keyword
import logging
import optparse
import asyncio
import undetected_chromedriver as uc
import seleniumwire.undetected_chromedriver as webdriver
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.utils import ChromeType
import base64
import signal
from datetime import datetime
from datetime import timedelta
from httpx import AsyncClient
from colorlog import ColoredFormatter
from urllib.parse import quote_plus
import requests
import math
import os
import random
import time
from pyairtable.formulas import match
from pyairtable import *
from playwright.async_api import async_playwright, Browser
HEADERS = {
    'User-Agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
    'Accept': 'application/json, text/plain, */*'
}
LOG_LEVEL = logging.INFO
log = logging.getLogger('pythonConfig')

signalTag = False

proxylist = []

logging.basicConfig(format='%(asctime)s %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)


def current_time():
    return datetime.now().astimezone().strftime('%Y-%m-%d %H:%M:%S %z')


def current_date():
    return datetime.now().astimezone().strftime('%Y-%m-%d')


def ensure_dir(file):
    directory = os.path.abspath(os.path.dirname(file))
    if not os.path.exists(directory):
        os.makedirs(directory)


def write_text(file: str, text: str):
    ensure_dir(file)
    with open(file, mode='w') as f:
        f.write(text)


def signalHandler(signal, frame):
    log.warning('Signal catched...')
    global signalTag
    signalTag = True
# from .util import *


async def get_playright(proxy, url, headless: bool = True):
    async with async_playwright() as playwright:

        if headless == '' or headless is None:
            headless = True
        PROXY_SOCKS5 = "socks5://127.0.0.1:1080"

        if proxy is None:
            try:
                browser = await playwright.firefox.launch(headless=headless)
                print('start is ok')
                return browser
            except:
                print('pl start failed')

        else:
            browserLaunchOptionDict = {
            "headless": headless,
            "proxy": {
                    "server": PROXY_SOCKS5,
            }
            }
            browser = await playwright.firefox.launch(**browserLaunchOptionDict)
            # Open new page
            if url is None or url == '':
                page = await browser.new_page()

                res = ''
            else:
                page = await browser.new_page()
                res = await page.goto(url)
            # print((await page.goto("1.html")).url)
    return browser, page,res


def write_file(new_contents, topic):
    if not os.path.exists("web/README-{}.md".format(topic)):
        open("web/README-{}.md".format(topic), 'w').write('')
    with open("web/README-{}.md".format(topic), 'r', encoding='utf8') as f:
        # 去除标题
        for _ in range(7):
            f.readline()

        old = f.read()
    new = new_contents + old
    with open("web/README-{}.md".format(topic), "w") as f:
        f.write(new)


def url_ok(url):
    print('check network')
    try:
        response = requests.head(url)
        print('proxy', response.status_code)
    except Exception as e:
        # print(f"NOT OK: {str(e)}")
        return False
    if response.status_code == 400 or response.status_code == 404:
        # print("OK")
        print(f"NOT OK: HTTP response code {response.status_code}")

        return False
    else:

        return True


def coldstart(topic):
    item_list = []

    with sync_playwright() as p:
        start = time.time()
        url = "https://github.com/search?o=desc&q={}&s=updated&type=Repositories".format(
            topic)
        print('user home url', url)
        page = get_playright(p, url, True)
        try:
            res = page.goto(url)
            total_count = int(page.locator(
                'div.flex-column:nth-child(1) > h3:nth-child(1)').split(' repository results').replace(',', ''))
            if total_count < 30:
                for_count = 0
            for_count = math.ceil(total_count / 30) + 1
        # item_list = reqtem["items"]
            for j in range(0, for_count, 1):
                try:
                    url = "https://api.github.com/search/repositories?q={}&sort=updated&per_page=30&page={}".format(
                        topic, j)
                    res = page.goto(url)

                    items = res.json()["items"]
                    item_list.extend(items)
                    print("第{}轮，爬取{}条".format(j, len(items)))
                except Exception as e:
                    print("网络发生错误", e)
                    continue

                time.sleep(random.randint(30, 60))
        except:
            print("请求数量的时候发生错误")

    return item_list


async def worker(id: int, st: datetime, ed: datetime, proxylist: list, delay: float, timeout: float, topic: str, keyword: str, index: int, table: Table) -> dict:
    workerRes = {}  # e.g. {'22.3.4.5': '2021-04-26 03:53:41'}
    # proxy = await popProxy(id, proxypool, timeout)
    # get latest 1000 results

    item_list = []
    j = index
    global signalTag
    # while not signalTag:
    result = False
    while not result:
        try:
            proxy = random.choice(proxylist)

            url = "https://api.github.com/search/repositories?q={}&sort=updated&per_page=100&page={}".format(
                topic, j)
                # client.get() may get stuck due to unknown reasons
                # resp = await client.get(url=url, headers=HEADERS, timeout=timeout)
            resp = requests.get(url, proxies={'http': proxy})
            req = resp.json()
            items = []
            if 'items' in req:
                items = req["items"]
            print("第{}轮，爬取{}条".format(j, len(items)))
            if(len(items)) > 0:
                save(table, keyword, topic, items)
                result = True
                item_list.extend(items)
                proxylist.append(proxy)
                result = True
            else:
                proxypool = 'https://proxypool.scrape.center/random',

                newProxy = requests.get(proxypool).text
                log.warning('[{}] Proxy EXP: proxy={} newProxy={} st={} ed={}'.format(id, proxy, newProxy, time2str(st),
                                                                                        time2str(ed)))
                log.debug('[{}] Proxy EXP: {}'.format(id, e))
                proxy = newProxy
                result = False
        except Exception as e:
            print(index, "网络发生错误", e, proxy)
            proxylist.remove(proxy)
            newproxy = random.choice(proxylist)
            proxy = newproxy
            result = False
            print('another try', index)

    return item_list


def str2time(x: str) -> datetime:
    return datetime.strptime(x, "%Y-%m-%d %H:%M:%S")


def time2str(x: datetime) -> str:
    return x.strftime("%Y-%m-%d %H:%M:%S")


def chunk(it, size):
    it = iter(it)
    while slice := tuple(islice(it, size)):
        yield slice


async def main(opts):
    # Catch signal to exit gracefully
    signal.signal(signal.SIGINT, signalHandler)
    timeSt = '2021-05-01 00:00:00'
    timeEd = '2021-05-01 01:00:00'
    keywords = []
    print('keywords list ', opts.keywords)

    if ',' in opts.keywords:
        keywords = opts.keywords.split(',')
    else:
        keywords.append(opts.keywords)
    topic = opts.topic
    print('keywords list ', keywords)
    apikey = os.environ['AIRTABLE_API_KEY']
    baseid = os.environ[topic.upper()+'_AIRTABLE_BASE_KEY']
    tableid = os.environ[topic.upper()+'_AIRTABLE_TABLE_KEY']
    api = Api(apikey)
    table = Table(apikey, baseid, tableid)

    for k in keywords:
        # Assign tasks
        timeSt = str2time(timeSt)
        timeEd = str2time(timeEd)
        dt = (timeEd - timeSt) / opts.threads
        try:
            url = "https://api.github.com/search/repositories?q={}&sort=updated".format(
                topic)

            reqtem = requests.get(url).json()
            # print('raw json',reqtem)
            total_count = reqtem["total_count"]
            if total_count < 100:
                for_count = 0
            for_count = math.ceil(total_count / 100) + 1

            if total_count < 100:
                for_count = 0
            for_count = math.ceil(1000 / 100) + 1
            # https://docs.github.com/en/rest/reference/search
            # The Search API helps you search for the specific item you want to find. For example, you can find a user or a specific file in a repository. Think of it the way you think of performing a search on Google. It's designed to help you find the one result you're looking for (or maybe the few results you're looking for). Just like searching on Google, you sometimes want to see a few pages of search results so that you can find the item that best meets your needs. To satisfy that need, the GitHub Search API provides up to 1,000 results for each search.
            print(total_count)
        except:
            print('here=========')
        proxypool = opts.proxypool
        times = list(chunk(range(for_count), 10))
        for item in times:
            proxylist = []

            while len(proxylist) < 20:
                proxy = requests.get(proxypool).text
                if requests.get('https://api.github.com', proxies={'http': proxy}).status_code == 200:
                    proxylist.append(proxy)
                    print('add one', proxy)
            print('page ', item)
            coroutines = []

            for i in item:
                proxy = random.choice(proxylist)

                coroutines.append(
                    worker(id=i,
                        st=timeSt + dt * i,
                        ed=timeSt + dt * (i + 1),
                        proxylist=proxylist,
                        delay=opts.delay,
                        timeout=opts.timeout,
                        topic=topic,
                        keyword=k,
                        index=i,
                        table=table))
            # Run tasks
            print('run task', item)
            workerRes = await asyncio.gather(*coroutines)
            proxylist = []
            print(item, 'task result', len(workerRes))

            time.sleep(60)
        page(table, topic)


def write_file(new_contents, topic):
    if not os.path.exists("web/README-{}.md".format(topic)):
        open("web/README-{}.md".format(topic), 'w').write('')
    with open("web/README-{}.md".format(topic), 'r', encoding='utf8') as f:
        # 去除标题
        for _ in range(7):
            f.readline()

        old = f.read()
    new = new_contents + old
    with open("web/README-{}.md".format(topic), "w") as f:
        f.write(new)


def url_ok(url):
    try:
        response = requests.head(url)
    except Exception as e:
        # print(f"NOT OK: {str(e)}")
        return False
    else:
        if response.status_code == 400 or response.status_code == 404:
            # print("OK")
            print(f"NOT OK: HTTP response code {response.status_code}")

            return False
        else:

            return True


def get_info(topic):
    # 监控用的
    try:

        api = "https://api.github.com/search/repositories?q={}".format(topic)
        # 请求API
        req = requests.get(api).json()
        items = req["items"]
        total_count = req["total_count"]
        for_count = math.ceil(total_count / 100) + 1
        # print(total_count)
        return total_count
    except Exception as e:
        print("网络请求发生错误", e)
        return None


def newbase(dbname):
    db = Base('apikey', dbname)
    return dbname


def newtable(db, table_name):
    api_key = os.environ['AIRTABLE_API_KEY']

    table = Table(api_key, db, table_name)
    return table


def insert2airtable(table, rows):
    # print(rows,'====',type(rows[0]))
    if len(rows) == 1:

        table.create(rows[0])
    else:
        table.create(rows)


def getrowid(table, row):

    formula = match(row)
    try:
        id = table.first(formula=formula)['id']
    except:
        id = None
    return id


def updaterow(table, rows):
    if len(rows) == 1:
        id = getrowid(table, rows[0])
        if id is None:
            insert2airtable(table, rows)
        else:
            table.update(id, rows[0])
    else:
        for row in rows:
            id = getrowid(table, [row])
            if id is None:
                insert2airtable(table, [row])
            else:
                table.update(id, [row])


def db_match_airtable(table, items, keyword):
    print('waiting to check', len(items))
    r_list = []
    for item in items:
        if item['id'] == "" or item['id'] == None:
            pass
        else:
            # print('valid  to save',item)

            full_name = item["full_name"]
            description = item["description"]
            if description == "" or description == None:
                description = 'no description'
            else:
                description = description.strip()
            url = item["html_url"]
            created_at = item["created_at"]
            topics = ''
            if item["topics"] == "" or item["topics"] == None:
                topics = keyword
            else:
                topics = ','.join(item["topics"])
            language = item['language']
            if language == "" or language == None:
                language = 'unknown'
            row = [{
                "name": full_name,
                "description": description,
                "url": url,
                "topic": topics,
                "language": language,
                "created_at": created_at
            }]
            updaterow(table, row)

    return ''


def save(table, keyword, topic, items):
    # 下面是监控用的
    year = datetime.now().year
    sorted_list = []
    total_count = get_info(keyword)
    print("获取原始数据:{}条".format(total_count))
    # items=craw_all(keyword)
    print("获取dao原始数据:{}条".format(len(items)))

    sorted = db_match_airtable(table, items, keyword)
    print("record in db:{}条".format(len(sorted)))


def page(table, topic):
    result = []
    for idx, item in enumerate(table.all()):
        print(idx, item['fields'])
        result.append(item['fields'])
    # print(sorted_list)
    DateToday = datetime.today()
    day = str(DateToday)
    newline = ""
    urls = []
    for idx, s in enumerate(sorted):
        print(s, '-')
        if not s['url'] in urls:
            line = "|{}|{}|{}|{}|{}|{}|{}|\n".format(str(idx),
            s["name"], s["description"], s["created_at"], s["url"], s["topic"], s["language"])

            newline = newline+line
            urls.append(s['url'])
    # print(newline)
    if newline != "":
        old = f"## {day}\n"
        old = old+"|id|name|description|update_at|url|topic|language|\n" + \
            "|---|---|---|---|---|---|---|\n"
        newline = "# Automatic monitor github {} using Github Actions \n\n > update time: {}  total: {} \n\n \n ![star me](https://img.shields.io/badge/star%20me-click%20--%3E-orange) [code saas idea monitor](https://github.com/wanghaisheng/code_saas_idea_hunter)  [Browsing through the web](https://wanghaisheng.github.io/code_saas_idea_hunter/)  ![visitors](https://visitor-badge.glitch.me/badge?page_id=code_saas_idea_hunter) \n\n{}".format(
            topic,
            datetime.now(),
            len(sorted), old) + newline

        write_file(newline, topic)


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


def initLog():
    LOGFORMAT = "  %(log_color)s%(asctime)s  %(levelname)-8s%(reset)s | %(log_color)s%(message)s%(reset)s"

    logging.root.setLevel(LOG_LEVEL)
    formatter = ColoredFormatter(LOGFORMAT)

    stream = logging.StreamHandler()
    stream.setLevel(LOG_LEVEL)
    stream.setFormatter(formatter)

    log.setLevel(LOG_LEVEL)
    log.addHandler(stream)


def get_undetected_webdriver():

    seleniumwire_options = {
        'proxy': {
            'http': 'socks5://127.0.0.1:1080',  # user:pass@ip:port
            'https': 'socks5://127.0.0.1:1080',
            'no_proxy': 'localhost,127.0.0.1'
        }
    }
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    # options.add_argument("--headless")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")

    if os.environ.get("GOOGLE_CHROME_BIN"):
        options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    # ChromeDriverManager().install()
    # Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())
    driver = ''
    if os.environ.get("CHROMEDRIVER_PATH"):
        executable_path = os.environ.get("CHROMEDRIVER_PATH")
    # driver = webdriver.Chrome(options = options, seleniumwire_options = seleniumwire_options, version_main = my_version)
        if url_ok('www.google.com'):
              driver = webdriver.Chrome(
            options=options, executable_path=executable_path)
        else:
            driver = webdriver.Chrome(
            options=options, executable_path=executable_path, seleniumwire_options=seleniumwire_options)
    else:
        if url_ok('www.google.com'):
            print('start uc no proxy')
            driver = webdriver.Chrome(
            options=options)
        else:
            print('start uc with proxy')

            driver = webdriver.Chrome(
            options=options, seleniumwire_options=seleniumwire_options)
    return driver
