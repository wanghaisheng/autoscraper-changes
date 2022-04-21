#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: RogerRordo

from itertools import islice
from ast import keyword
import logging
import optparse
import asyncio

import base64
import signal
from datetime import datetime
from datetime import timedelta
from colorlog import ColoredFormatter
from urllib.parse import quote_plus
import requests
import json
import math
import os
import random
import time
from pyairtable.formulas import match
from pyairtable import *
from playwright.async_api import async_playwright, Browser

from enum import Enum


class BrowsersEnum(Enum):
    FIREFOX = 1
    CHROME = 2
    CHROMIUM = 3
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


async def get_playright(proxy:bool=False,headless:bool=True):
    print('proxy',proxy,'headless',headless)
    browser=''
    playwright =await  async_playwright().start()
    PROXY_SOCKS5 = "socks5://127.0.0.1:1080"
    # browser=''
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

def write_file(new_contents,topic):
    if not os.path.exists("web/README-{}.md".format(topic)):
        open("web/README-{}.md".format(topic),'w').write('')
    with open("web/README-{}.md".format(topic),'r',encoding='utf8') as f:
        #去除标题
        for _ in range(7):
            f.readline()

        old = f.read()
    new = new_contents + old
    with open("web/README-{}.md".format(topic), "w") as f:
        f.write(new)

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

