from datetime import datetime
import os
import pytz
import logging
import sys
import csv
from proxy_request import ProxyRequest
from bs4 import BeautifulSoup as soup
import time
from supabase import create_client, Client
from dotenv import load_dotenv
import sys
import logging
from tenacity import *
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)


# 加载文件
load_dotenv(".env")
supabase_url = os.environ.get('supabase_url')
supabase_url = 'https://bwrzzupfhzjzvuglmpwx.supabase.co'

print(supabase_url)
supabase_apikey = os.environ.get('supabase_apikey')
print(supabase_apikey)

supabase_db: Client = create_client(
    supabase_url=supabase_url, supabase_key=supabase_apikey)

requests = ProxyRequest()

logger = logging.getLogger(__name__)


class Scraper:
    def __init__(self, keyword: str, client_spent: int, last_posted: str):
        self.keyword = keyword
        self.client_spent = client_spent
        self.current_date = datetime.now().date().strftime("%Y-%m-%d")
        self.last_posted = (
            datetime.now() - datetime.strptime(last_posted, "%Y-%m-%d")).days
        self.headers = {
            'Host': 'www.upwork.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:99.0) Gecko/20100101 Firefox/99.0',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'x-odesk-user-agent': 'oDesk LM',
            'x-requested-with': 'XMLHttpRequest',
            'vnd-eo-trace-id': '700d43b87ba66927-SEA',
            'vnd-eo-span-id': '6236f5fa-e8eb-4373-82f8-f0b906075a64',
            'vnd-eo-parent-span-id': 'cd146679-1104-4196-9750-cbc5abc8fedd',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Authorization': 'Bearer oauth2v2_00ce50f322951b7f8e6b8ef7037afa4e',
            'Referer': 'https://www.upwork.com/nx/jobs/search',
            'Connection': 'keep-alive',
            'Cookie': '_pxhd=H50eKNBi5HYWGTM7YEcuQiUcMgPL0EnfC6FxPy9gKSIfUTurAoL4FyrRmfIMufjAJwO5l9nMSf4AH3A5JeMiRw==:olDGDS9q-faX00iNiTPjA1rNTcAZlvUVNrpYV8olRItBXSj2c-u08Aplzabr12DBTIipCxpxCcv3z8J3bXk4XtS5ek4y4LTArGuWcl1YY90=; visitor_id=165.154.226.51.1650334686155000; lang=en; _pxvid=f2c484a3-bf86-11ec-a1d5-6b494c47634d; spt=5fa967f7-b267-488a-b9fb-f7c9a8a42f90; OptanonConsent=isGpcEnabled=0&datestamp=Tue+Apr+19+2022+10%3A18%3A28+GMT%2B0800+(China+Standard+Time)&version=6.28.0&isIABGlobal=false&hosts=&consentId=32c3fa85-d886-476d-9424-3a80356f8f08&interactionCount=1&landingPath=https%3A%2F%2Fwww.upwork.com%2F&groups=C0001%3A1%2CC0002%3A1%2CC0003%3A1%2CC0004%3A1; device_view=full; _sp_id.2a16=eaf6e4b0-bebb-4e29-af12-0852977c0a15.1650334697.5.1650786855.1650781434.00f9723b-7483-4170-a66e-52e814b3940d; AWSALB=AQU9T4qCw350qbiSMpEZPzvAVCwmiePl02vV0XFjTytpZnFVB2VNoDtFKi265gLDEQOqm3wcZA9dKPE152jcUcrLu8TPe1nOXBbsgvdl+wTvcHuRchrKmwaMgvuD; AWSALBCORS=AQU9T4qCw350qbiSMpEZPzvAVCwmiePl02vV0XFjTytpZnFVB2VNoDtFKi265gLDEQOqm3wcZA9dKPE152jcUcrLu8TPe1nOXBbsgvdl+wTvcHuRchrKmwaMgvuD; _gcl_au=1.1.699357622.1650334700; G_ENABLED_IDPS=google; _ga_KSM221PNDX=GS1.1.1650784853.7.1.1650786822.0; _ga=GA1.2.2035527311.1650334726; _rdt_uuid=1650334742890.c272f459-e78d-4af3-b881-cc49543a49be; __pdst=d9072ccb9caf460e9504f4f9b41cee53; _fbp=fb.1.1650334748591.1485276984; recognized=803e5d8b; company_last_accessed=d1013673067; current_organization_uid=1510642430206709761; enabled_ff=OTBnrOn,!air2Dot76Qt,!CI10270Air2Dot5QTAllocations,!CI10857Air3Dot0,CI11132Air2Dot75,!air2Dot76,!SSINav,CI9570Air2Dot5,!CI12577UniversalSearch,!OTBnr; visitor_gql_token=oauth2v2_02da1558ceeb9e37e7143e7465be28dc; cookie_prefix=; cookie_domain=.upwork.com; __cfruid=2aa348ba27ebd7054a696433c6f6d823f98816ae-1650772536; pxcts=d982cd5c-c378-11ec-86bc-53645367537a; XSRF-TOKEN=a3d48666d183ebb4dd618f8fb2208139; _px3=6d3cd72d76da9f5e554a7908aaf48d4549f8df8de4c006d7140c7528c5123277:fJMP7opE2gdLHagaj1c8thaEA/LZaZJFXutpM9VDc0Hr3OyXTdx62ZSLo8jjk/HMJH9nxLZgQzLLk8QRp2aHXw==:1000:SJ902gkyxqtz7hv+Ij/XGfERry4IYJBVL209WS1rBABwbwkqfKhpwsOQ1u4FbfTci1RmyX2jRRqQOa/ACm1eqoK9ZLADZeFUbonMFSL8FGU5Z84gXscbpRlk+lNi3xtqTnWoLBt1tmMGM25M/LsIfNVRHtE9DOcOZGALvwJd90/hxmOWwmk0coaobTdJICK8QAseK2Tl6oajqH4V2EFlDg==; _gid=GA1.2.1223786565.1650768462; UserPrivacySettings=%7B%22AlertBoxClosed%22%3A%222022-04-24T02%3A55%3A50.814Z%22%2C%22Groups%22%3A%7B%22Targeting%22%3Atrue%7D%7D; _hp2_props.2858077939=%7B%22user_context%22%3A%22unknown%22%2C%22user_logged_in%22%3Afalse%2C%22container_id%22%3A%22GTM-WNVF2RB%22%7D; _hp2_id.2858077939=%7B%22userId%22%3A%228536547390087702%22%2C%22pageviewId%22%3A%22932722710261455%22%2C%22sessionId%22%3A%227048527622264698%22%2C%22identity%22%3Anull%2C%22trackerVersion%22%3A%224.0%22%7D; _uetsid=6ecf5470c37a11ec94449dc35e8be9db; _uetvid=6ecf9f40c37a11ec992b838c7cc40e3b; IR_gbd=upwork.com; IR_13634=1650769115466%7C0%7C1650769115466%7C%7C; _dpm_id.5831=e55df5d9-7f50-40d7-b0cf-212077273150.1650769115.3.1650776141.1650773037.8a342b7f-7309-44e2-a0a5-13c892eea419; _clck=foxrdl|1|f0w|0; _clsk=1r80gte|1650769118453|1|0|d.clarity.ms/collect; __zlcmid=19eksHDPRjkECT3; g_state={"i_p":1650780196001,"i_l":1}; channel=other; console_user=803e5d8b; user_uid=1510642430206709760; master_access_token=49fb7f9b.oauth2v2_99e87790ddb26a68d7e721774f15ba0a; oauth2_global_js_token=oauth2v2_00ce50f322951b7f8e6b8ef7037afa4e; SZ=a66f9e551d895b180016ba1ee8c95b53187560394443252ff3808ca8267f1f37; user_oauth2_slave_access_token=49fb7f9b.oauth2v2_99e87790ddb26a68d7e721774f15ba0a:1510642430206709760.oauth2v2_5c9a9326bbfb0b8df55968cc4fc80ca3; JobSearchUI_tile_size_1510642430206709760=medium; __cf_bm=dUjVrCVxDd2IKbZbAcfoT2kmynP2_fSVHP0loGl_ZLg-1650786346-0-AbB+QmypiLl045zskUdqijRx6x5hX1NWQVx/7Wi3DlkzR/GwvapYR+VYRstRC2YaYPC5+3bDSOuxeMDlipCIVHI=; keen={%22uuid%22:%22d6565737-664b-4572-8dbb-093fdf75b234%22%2C%22initialReferrer%22:%22https://www.upwork.com/nx/find-work/best-matches%22}; _sp_ses.2a16=*; prodperfect_session={%22session_uuid%22:%223c821be6-1ac5-4e29-a2cc-326dd90932d0%22}; odesk_signup.referer.raw=https%3A%2F%2Fwww.upwork.com%2Fab%2Fjobs%2Fsearch%2Fjobdetails%2Fvisitor%2F%7E016176b468b8f6e816%2Fdetails; _dc_gtm_UA-62227314-1=1; _dc_gtm_UA-62227314-13=1',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache'
        }

        # preparing csv file for this keyword
        self.data = []
        self.read_data()

        os.makedirs(os.path.join(os.path.dirname(
            __file__), 'temp'), exist_ok=True)
        if os.path.isfile(os.path.join(os.path.dirname(__file__), f'temp/{self.keyword}_last_dt.txt')):
            self.last_dt = datetime.strptime(open(os.path.join(os.path.dirname(
                __file__), f'temp/{self.keyword}_last_dt.txt'), 'r').readline(), '%Y-%m-%dT%H:%M:%S%z')
        else:
            self.last_dt = datetime(1970, 1, 1, tzinfo=pytz.UTC)

    def save_data(self):
        headers = ['Title', 'Link', 'Posted_on', 'Budget', 'Description', 'Country', 'Total_jobs_posted',
                   'Open_jobs', 'Total_reviews', 'Rating', 'Total_hires', 'Client_since', 'Client_spent']
        # writing to csv file
        with open(os.path.join(os.path.dirname(__file__), f'data/{self.keyword}.csv'), 'w', newline='', encoding="utf-8") as csvfile:
            # creating a csv writer object
            csvwriter = csv.writer(csvfile, lineterminator=os.linesep)

            # writing the fields
            csvwriter.writerow(headers)

            # writing the data rows
            csvwriter.writerows(self.data)

    def read_data(self):
        data = []
        if not os.path.exists(os.path.join(os.path.dirname(__file__), 'data')):
            os.mkdir(os.path.join(os.path.dirname(__file__), 'data'))
        if not os.path.exists(os.path.join(os.path.dirname(__file__), f'data/{self.keyword}.csv')):
            self.data = data
            self.save_data()
            return None
        with open(os.path.join(os.path.dirname(__file__), f'data/{self.keyword}.csv'), 'r', encoding="utf-8") as csvfile:
            csvreader = csv.reader(csvfile)
            next(csvreader)  # ignoring the headers
            for row in csvreader:
                data.append(row)
        self.data = data
        return None

    def makeUrl(self, page):
        # return f"https://www.upwork.com/search/jobs/url?client_hires=1-9,10-&amount=5000-&payment_verified=1&duration_v3=ongoing&page={page}&per_page=50&q={self.keyword}&sort=recency&t=0,1"
        # return f"https://www.upwork.com/search/jobs/?q={self.keyword}&per_page=50&sort=recency&page={page}"
        return f"https://www.upwork.com/ab/jobs/search/url?q={self.keyword}&per_page=50&sort=recency&page={page}"

    def scrap(self):
        i = 1
        while True:
            logger.warning('Requsting new page...', self.makeUrl(i))
            response = requests.get(self.makeUrl(i), headers=self.headers)
            # url=f"https://www.upwork.com/ab/jobs/search/url?q={self.keyword}&per_page=50&sort=recency&page={i}"
            # response = requests.get(url, headers=self.headers)

            if not response:
                logger.error('Page not found!')
                break

            logger.warning('Grab page #%i...' % i)
            # print(response.text)
            page_data = response.json()
            # print(page_data)
            if page_data['searchResults']['paging']['count'] == 0:
                logger.warning('All pages grabbed! Finished!')
                break
            dt = page_data['searchResults']['jobs'][0]['createdOn']
            dt = datetime.strptime(dt, '%Y-%m-%dT%H:%M:%S%z')
            if i == 1:
                with open(os.path.join(os.path.dirname(__file__), f'temp/{self.keyword}_last_dt.txt'), 'w') as f:
                    f.write(dt.strftime('%Y-%m-%dT%H:%M:%S%z'))

            if dt < self.last_dt or (datetime.now(tz=pytz.UTC) - dt).days > self.last_posted:
                logger.error('There is no new jobs!')
                break

            job_links = [job['ciphertext'] for job in page_data['searchResults']['jobs'] if job['client']['totalSpent'] > self.client_spent and job['client']['location']
                         ['country'].lower() != 'india' and (datetime.now(tz=pytz.UTC) - datetime.strptime(job['createdOn'], '%Y-%m-%dT%H:%M:%S%z')).days <= self.last_posted]

            # filter the links
            logger.warning("filtering the links")
            for link in job_links:
                
                self.filter_link_plus(link)
                time.sleep(30)

            self.save_data()
            logger.warning('File #%i saved!' % i)
            i += 1
        # TODO: CHANGE
        logger.warning(
            f"Download Your file: http://127.0.0.1:5000/file/{self.keyword}")

    def filter_link_plus(self, job_id):
        # url = f'https://www.upwork.com/ab/jobs/search/jobdetails/visitor/{job_id}/details'
        url = f'https://www.upwork.com/jobdetails/api/job/{job_id}/summary'

        res = requests.get(url, headers=self.headers)
        print('detail job url', url)
        if not res:
            logger.error(f"link is not filtered: {job_id}")

        job_data = res.json()
        # filter the links
        last_seen_date = job_data["job"]["clientActivity"]["lastBuyerActivity"]
        if not last_seen_date:
            last_seen_date = datetime.strftime(
                datetime.now(), '%Y-%m-%dT%H:%M:%S.%fZ')
        if job_data["job"]["clientActivity"]["totalHired"] > 0 or (datetime.now()-datetime.strptime(last_seen_date, '%Y-%m-%dT%H:%M:%S.%fZ')).days > 10:
            return None

        self.data.append(
            [
                job_data["job"]["title"],
                'https://www.upwork.com/job/'+job_data["job"]["ciphertext"],
                job_data["job"]["publishedOn"],
                str(job_data["job"]["budget"]["amount"]) + " " +
                job_data["job"]["budget"]["currencyCode"],
                job_data["job"]["description"],
                job_data["buyer"]["location"]["country"],
                job_data["buyer"]["jobs"]["postedCount"],
                job_data["buyer"]["jobs"]["openCount"],
                job_data["buyer"]["stats"]["feedbackCount"],
                round(job_data["buyer"]["stats"]["score"], 2),
                job_data["buyer"]["stats"]["totalJobsWithHires"],
                job_data["buyer"]["company"]["contractDate"],
                str(job_data["buyer"]["stats"]["totalCharges"]["amount"]) +
                " " +
                job_data["buyer"]["stats"]["totalCharges"]["currencyCode"]
            ]
        )
        job = {
            "job_title": job_data["job"]["title"],
            "job_type": job_data["job"]["type"],
            "job_level": job_data["job"]["tier"],
            "job_budget": str(job_data["job"]["budget"]["amount"]),
            "job_estimated_time": job_data["job"]["durationLabel"],
            "job_posted_time": job_data["job"]["postedon"],
            "job_page_link ": 'https://www.upwork.com/job/'+job_data["job"]["ciphertext"],
            "job_detail ": job_data["job"]["description"],
            # "job_skill ": ','.join([i['prettyName'] for i in job_data["job"]["attrs"]]),
            # "job_div ": '',
            # "proposals ": job_data["job"]['proposalsTier'],
            # "location ": job_data["job"]["locations"]
        }
        print(job)
        supabaseop("upwork_jobs", job)

    @retry(stop=stop_after_attempt(3), before=before_log(logger, logging.DEBUG))
    def supabaseop(tablename, users):
        try:
            data = supabase_db.table(tablename).insert(users).execute()
        except:
            raise Exception

    def filter_links(self, links: list):
        i = 0
        while i < len(links):
            res = requests.get(links[i])
            if not res:
                logger.error(f"link is not filtered: {links[i]}")
                links.pop(i)
                continue
            # with open('index.html','wb') as f:
            #     f.write(res.content)
            page_soup = soup(res.text, 'html.parser')
            sections = page_soup.find_all(
                'section', attrs={'class': 'up-card-section'})
            client_activity = None
            for section in sections:
                h4 = section.find('h4')
                if h4:
                    if h4.text.lower() == 'activity on this job':
                        client_activity = str(section).lower()
                        break
            if not client_activity:
                links.pop(i)
                continue
            if client_activity.find('hires') != -1:
                links.pop(i)
                continue
            last_seen = client_activity.find(' day ago')
            if last_seen != -1:
                if client_activity[last_seen-2:last_seen].isnumeric():
                    links.pop(i)
                    continue
            last_seen = client_activity.find('month ago')
            if last_seen != -1:
                links.pop(i)
                continue
            i += 1
        return links


if __name__ == '__main__':
    # Scraper(sys.argv[1]).scrap()
    print(os.getcwd())
    # with open('keywords.txt','r') as f:
    # keywords = [key.strip() for key in f.read().split('\n')]
    keywords = ['tiktok']
    print("keywords"+str(keywords))
    for key in keywords:
        logger.warning(f"starting scraping for: {key}")
        # Scraper(key, client_spent=20000, last_posted='2021-07-10').scrap()
        scrap = Scraper(key, client_spent=20000, last_posted='2021-07-10')
        scrap.scrap()

    # Scraper("aws").scrap()
    # Scraper("chatbot").filter_link_plus("~016176b468b8f6e816")
    # r = Scraper("chatbot").filter_links(['https://www.upwork.com/search/jobs/details/~016176b468b8f6e816/'])
    # r = Scraper("chatbot").filter_links(['https://www.upwork.com/job/Need-someone-code-script-amp-webscrape-jewelry-site-for-data-and-images-videos_~01759e0717f4b1a848/'])
    # print(r)
