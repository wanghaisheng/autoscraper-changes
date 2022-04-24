from datetime import datetime
import os
import pytz
import logging
import sys
import csv
from proxy_request import ProxyRequest
from bs4 import BeautifulSoup as soup

requests = ProxyRequest()

logger = logging.getLogger(__name__)

class Scraper:
    def __init__(self, keyword: str, client_spent: int, last_posted: str):
        self.keyword = keyword
        self.client_spent = client_spent
        self.current_date = datetime.now().date().strftime("%Y-%m-%d")
        self.last_posted = (datetime.now() - datetime.strptime(last_posted, "%Y-%m-%d")).days
        self.headers = {
            'authority': 'www.upwork.com',
            'sec-ch-ua': '" Not;A Brand";v="99", "Microsoft Edge";v="91", "Chromium";v="91"',
            'x-odesk-user-agent': 'oDesk LM',
            'x-requested-with' : 'XMLHttpRequest',
            'sec-ch-ua-mobile': '?0',
            'accept': 'application/json, text/plain, */*',
            'x-requested-with': 'XMLHttpRequest',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://www.upwork.com/',
            'accept-language': 'en-US,en;q=0.9',
        }

        # preparing csv file for this keyword
        self.data = []
        self.read_data()

        os.makedirs(os.path.join(os.path.dirname(__file__),'temp'), exist_ok=True)
        if os.path.isfile(os.path.join(os.path.dirname(__file__),f'temp/{self.keyword}_last_dt.txt')):
            self.last_dt = datetime.strptime(open(os.path.join(os.path.dirname(__file__),f'temp/{self.keyword}_last_dt.txt'), 'r').readline(), '%Y-%m-%dT%H:%M:%S%z')
        else:
            self.last_dt = datetime(1970, 1, 1,tzinfo=pytz.UTC)

    def save_data(self):
        headers = ['Title', 'Link', 'Posted_on', 'Budget' , 'Description', 'Country', 'Total_jobs_posted', 'Open_jobs', 'Total_reviews', 'Rating', 'Total_hires', 'Client_since', 'Client_spent']
        # writing to csv file
        with open(os.path.join(os.path.dirname(__file__),f'data/{self.keyword}.csv'), 'w', newline='', encoding="utf-8") as csvfile:
            # creating a csv writer object
            csvwriter = csv.writer(csvfile, lineterminator=os.linesep)
            
            # writing the fields
            csvwriter.writerow(headers)
            
            # writing the data rows
            csvwriter.writerows(self.data)

    def read_data(self):
        data = []
        if not os.path.exists(os.path.join(os.path.dirname(__file__),'data')):
            os.mkdir(os.path.join(os.path.dirname(__file__),'data'))
        if not os.path.exists(os.path.join(os.path.dirname(__file__),f'data/{self.keyword}.csv')):
            self.data = data
            self.save_data()
            return None
        with open(os.path.join(os.path.dirname(__file__),f'data/{self.keyword}.csv'), 'r', encoding="utf-8") as csvfile:
            csvreader = csv.reader(csvfile)
            next(csvreader) # ignoring the headers
            for row in csvreader:
                data.append(row)
        self.data = data
        return None
        
        

    def makeUrl(self, page):
        # return f"https://www.upwork.com/search/jobs/url?client_hires=1-9,10-&amount=5000-&payment_verified=1&duration_v3=ongoing&page={page}&per_page=50&q={self.keyword}&sort=recency&t=0,1"
        return f"https://www.upwork.com/search/jobs/?q={self.keyword}&per_page=50&sort=recency&page={page}"

    def scrap(self):
        i = 1
        while True:
            logger.warning('Requsting new page...')
            response = requests.get(self.makeUrl(i), headers=self.headers)
            if not response:
                logger.error('Page not found!')
                break

            logger.warning('Grab page #%i...' % i)
            print(response)
            page_data = response.json()
            print(page_data)
            if page_data['searchResults']['paging']['count'] == 0:
                logger.warning('All pages grabbed! Finished!')
                break
            dt = page_data['searchResults']['jobs'][0]['createdOn']
            dt = datetime.strptime(dt, '%Y-%m-%dT%H:%M:%S%z')
            if i == 1:
                with open(os.path.join(os.path.dirname(__file__),f'temp/{self.keyword}_last_dt.txt'), 'w') as f:
                    f.write(dt.strftime('%Y-%m-%dT%H:%M:%S%z'))
            
            if dt < self.last_dt or (datetime.now(tz=pytz.UTC)- dt).days > self.last_posted:
                logger.error('There is no new jobs!')
                break

            job_links = [job['ciphertext'] for job in page_data['searchResults']['jobs'] if job['client']['totalSpent'] > self.client_spent and job['client']['location']['country'].lower() != 'india' and (datetime.now(tz=pytz.UTC)- datetime.strptime(job['createdOn'], '%Y-%m-%dT%H:%M:%S%z')).days <= self.last_posted]

            # filter the links
            logger.warning("filtering the links")
            for link in job_links:
                self.filter_link_plus(link)

            self.save_data()
            logger.warning('File #%i saved!' % i)
            i += 1
        logger.warning(f"Download Your file: http://127.0.0.1:5000/file/{self.keyword}") #TODO: CHANGE

    def filter_link_plus(self, job_id): 
        url = f'https://www.upwork.com/ab/jobs/search/jobdetails/visitor/{job_id}/details'
        res = requests.get(url, headers=self.headers)
        if not res:
            logger.error(f"link is not filtered: {job_id}")

        job_data = res.json()
        # filter the links
        last_seen_date = job_data["job"]["clientActivity"]["lastBuyerActivity"]
        if not last_seen_date:
            last_seen_date = datetime.strftime(datetime.now(), '%Y-%m-%dT%H:%M:%S.%fZ')
        if job_data["job"]["clientActivity"]["totalHired"] > 0 or (datetime.now()-datetime.strptime(last_seen_date, '%Y-%m-%dT%H:%M:%S.%fZ')).days > 10:
            return None
        
        self.data.append(
            [
                job_data["job"]["title"],
                'https://www.upwork.com/job/'+job_data["job"]["ciphertext"],
                job_data["job"]["postedOn"],
                str(job_data["job"]["budget"]["amount"]) + " " + job_data["job"]["budget"]["currencyCode"],
                job_data["job"]["description"],
                job_data["buyer"]["location"]["country"],
                job_data["buyer"]["jobs"]["postedCount"],
                job_data["buyer"]["jobs"]["openCount"],
                job_data["buyer"]["stats"]["feedbackCount"],
                round(job_data["buyer"]["stats"]["score"],2),
                job_data["buyer"]["stats"]["totalJobsWithHires"],
                job_data["buyer"]["company"]["contractDate"],      
                str(job_data["buyer"]["stats"]["totalCharges"]["amount"]) + " " + job_data["buyer"]["stats"]["totalCharges"]["currencyCode"]   
            ]
        )

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
            sections = page_soup.find_all('section', attrs={'class':'up-card-section'})
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
    keywords=['tiktok']
    print("keywords"+str(keywords))
    for key in keywords:
        logger.warning(f"starting scraping for: {key}")
        # Scraper(key, client_spent=20000, last_posted='2021-07-10').scrap()
        scrap= Scraper(key, client_spent=20000, last_posted='2021-07-10')
        scrap.scrap()



    # Scraper("aws").scrap()
    # Scraper("chatbot").filter_link_plus("~016176b468b8f6e816")
    # r = Scraper("chatbot").filter_links(['https://www.upwork.com/search/jobs/details/~016176b468b8f6e816/'])
    # r = Scraper("chatbot").filter_links(['https://www.upwork.com/job/Need-someone-code-script-amp-webscrape-jewelry-site-for-data-and-images-videos_~01759e0717f4b1a848/'])
    # print(r)