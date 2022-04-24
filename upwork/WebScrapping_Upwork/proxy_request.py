import requests
import time
import json
from bs4 import BeautifulSoup
from itertools import cycle
import traceback
import os 
import logging

logger = logging.getLogger(__name__)

class ProxyRequest:
    def __init__(self,proxy_page=0) -> None:
        self.user_agents = cycle([
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36 Edg/91.0.864.37',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246',
            'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36 Edg/91.0.864.41'
        ])
        self.get_headers = {
            'Host':'www.upwork.com',
            # 'Sec-Ch-Ua':'" Not A;Brand";v="99", "Chromium";v="90"',
            'Sec-Ch-Ua-Mobile':'?0',
            'cache-control': 'max-age=0',
            'Upgrade-Insecure-Requests':'1',
            'User-Agent': next(self.user_agents),
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Sec-Fetch-Site':'same-origin',
            'Sec-Fetch-Mode':'navigate',
            'Sec-Fetch-User':'?1',
            'Sec-Fetch-Dest':'document',
            'Accept-Encoding':'*',
            'Accept-Language':'en-US,en;q=0.9',
            'Connection':'close',
            'referer': 'https://www.upwork.com/search/jobs/t/0,1/details/~018d35a5b9ea4c28e8/?amount=5000-&client_hires=1-9,10-&duration_v3=ongoing&payment_verified=1&q=chatbot&sort=recency'
        }

        self.post_headers = self.get_headers

        self.proxy_page = proxy_page
        self.proxy = {} # trying with no proxy
        self.proxies_cycle = cycle(self.get_proxy())

    def get_proxy(self):
        proxies_list = []
        with open(os.path.join(os.path.dirname(__file__),'proxy_list.json')) as f:
            proxies_list = json.load(f)
        proxies_per_process = len(proxies_list)//1 # change according to no. of processes
        return [{}] + proxies_list[self.proxy_page*proxies_per_process:proxies_per_process+(self.proxy_page*(proxies_per_process))]

    def get(self, url, headers = None, **kwargs):
        r = None
        timeout = time.time() 
        if not headers:
            headers = self.get_headers
        while 1:
            if time.time() - timeout >= 120: # 2 minutes from now
                logger.warning("Request got timeout after 2 min")
                break
            try:
                headers.update({'User-Agent':next(self.user_agents)})
                self.proxy = next(self.proxies_cycle)
                # self.session.proxies.update(self.get_proxy())
                logger.warning('started request')
                tempTime = time.time()
                r = requests.get(url, headers=headers, proxies=self.proxy, timeout=30, **kwargs)
                logger.warning(f'ended request! Time taken : {time.time()-tempTime}')
                if  r.status_code != 200 :
                    logger.error(f"Bad Request: {r.status_code}")
                    if r.status_code == 403:
                        continue
                    break

                soup = BeautifulSoup(r.content, 'lxml')
                mydivs = soup.findAll("div")
                if len(mydivs) > 0:
                    if "Captcha" in str(mydivs[0]):
                        logger.error("got captcha error![GET]")
                        continue
                break
            except Exception as e:
                logger.error(f"Exception occurred: something went wrong!\n{e}")
                break
        return r

    def post(self, url, payload):
        r = None
        timeout = time.time()
        while 1:
            if time.time() - timeout >= 120: # 2 minutes from now
                logger.error("Request got timeout after 2 min")
                break
            try:
                self.post_headers.update({'User-Agent':next(self.user_agents)})
                self.proxy = next(self.proxies_cycle)
                # session.proxies.update(get_proxy())
                logger.warning('started Post request')
                tempTime = time.time()
                r = requests.post(url, headers=self.post_headers, proxies=self.proxy, timeout=30, data=payload)
                logger.warning(f'ended request! Time taken : {time.time()-tempTime}')

                if  r.status_code != 200 :
                    logger.error(f"Bad Request: {r.status_code}")
                    if r.status_code == 403:
                        continue
                    break

                soup = BeautifulSoup(r.content, 'lxml')
                mydivs = soup.findAll("div")
                if len(mydivs) > 0:
                    if "Captcha" in str(mydivs[0]):
                        logger.error("got captcha error![POST]")
                        continue
                break
            except Exception as e:
                traceback.print_exc()
                # logger.error(f"Exception occurred: something went wrong!\n{e}")
                break
        return r