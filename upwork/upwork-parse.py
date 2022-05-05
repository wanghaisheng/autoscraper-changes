
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver

from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.common.keys import Keys
# import Action chains
from selenium.webdriver.common.action_chains import ActionChains

# my function
from translator import translate

import urllib.request

from bs4 import BeautifulSoup

from lxml import html

from time import sleep
import datetime
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s:%(name)s:%(levelname)s:%(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    handlers=[logging.FileHandler('./upwork_scraper.log'), logging.StreamHandler()])

TIME_SLEEP = (2, 6)
delayTime  = 2
waitTime   = 50


SEARCH_URL = 'https://www.upwork.com/nx/jobs/search/?page=' # '2&sort=recency'
SEARCH_CAT_URL = "https://www.upwork.com/o/jobs/browse/c/%s/?page="

cats = {
    'All Categories': 'all',
    'Data Science & Analytics': 'data-science-analytics',
    'Web, Mobile & Software Dev': 'web-mobile-software-dev',
    'IT & Networking': 'it-networking',
    'Engineering & Architecture ': 'engineering-architecture',
    'Design & Creative': 'design-creative',
    'Writing': 'writing',
    'Translation': 'translation',
    'Legal': 'legal',
    'Admin Support': 'admin-support',
    'Customer Service': 'customer-service',
    'Sales & Marketing': 'sales-marketing',
    'Accounting & Consulting': 'accounting-consulting'
}


URL = 'https://www.upwork.com'

import demo22 as demo
import GoogleLogIn as GL

from random import uniform


def CheckReCAPTCHA(driver):
    # print('CheckReCAPTCHA(driver): running...' )
    main_page = driver.page_source
    soup = BeautifulSoup(main_page, 'lxml')

    ## Save HTML page to file -------------------------
    # with open('page.html', 'w', encoding='utf-8') as file:
    #     file.write(main_page)
    #     print('Save page to file PAGE.HTML')
    # -------------------------------------------------

    while True:
        ref = soup.find('a', class_='g-recaptcha')
        ref2 = soup.find('div', class_='g-recaptcha')
        if ref or ref2:
            print('BeautifulSoup: ReCAPTCHA founded!')
            if demo.ReCaptchaPass(driver):
                print('Password verified!')
            else:
                print('Password NOT verified...')
                # return False
        else:
            print('BeautifulSoup: ReCAPTCHA NOT founded')
            #
            return True
            #
        sleep(delayTime/10)

    return True


def local_init(url):
    print('- driver_init()')
    option = demo.driver_init(True, False)

    ## Add User acount in to chrome browser -------------------------------
    ## https://stackoverflow.com/questions/31062789/how-to-load-default-profile-in-chrome-using-python-selenium-webdriver
    # C:\Users\Дом\AppData\Local\Google\Chrome\User Data\Default
    # option.add_argument(r"user-data-dir=C:\Users\Дом\AppData\Local\Google\Chrome\User Data\Default")
    # option.add_argument( 'user-data-dir=C:\\Users\\Дом\\AppData\\Local\\Google\\Chrome\\User Data\\' )

    option.add_argument(r"user-data-dir=C:\Users\Дом\AppData\Local\Google\Chrome\User Data\Profile 2")

    option.add_argument('--disable-web-security')
    option.add_argument('--allow-running-insecure-content')

    # # USE THIS IF YOU NEED TO HAVE MULTIPLE PROFILES
    # option.add_argument('--profile-directory=Default')

    # # ----------------------------------------------------------------------
    print('-')
    s = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=s, options=option)
    demo.after_init(driver, False)
    return driver


def GoogleLogin(driver):
    # Start --- Login in google account block -------------------------------------------
    # https://stackoverflow.com/questions/44856887/log-into-gmail-using-selenium-in-python
    import auth_data as data
    driver.get("https://accounts.google.com/signin")
    # driver.get(
    #     "https://accounts.google.com/ServiceLogin?service=mail&passive=true&rm=false&continue=https://mail.google.com/mail/&ss=1&scc=1&ltmpl=default&ltmplcache=2&emr=1&osid=1#identifier")
    email_phone = driver.find_element_by_xpath("//input[@id='identifierId']")
    email_phone.send_keys(data.GOOGLE_LOGIN)
    driver.find_element_by_id("identifierNext").click()
    password = WebDriverWait(driver, 5).until(
         EC.element_to_be_clickable((By.XPATH, "//input[@name='password']")))
    password.send_keys(data.GOOGLE_PASSWORD)
    driver.find_element_by_id("passwordNext").click()
    WebDriverWait(driver, 100).until(
         EC.element_to_be_clickable((By.XPATH, '//*[@id="yDmH0d"]/c-wiz/div/div[2]/div/c-wiz/c-wiz/div/div[1]/div[3]/c-wiz/nav/ul/li[1]/a/div[2]')))
    # //*[@id="yDmH0d"]/c-wiz/div/div[2]/div/c-wiz/c-wiz/div/div[1]/div[3]/c-wiz/nav/ul/li[1]/a/div[2]
    # End ----- Login in google account block --------------------------------------------
    return driver


def UpWorkLogin(driver):
    print('0')
    driver.get(URL)
    CheckReCAPTCHA(driver)
    # # Get Driver Version

    # str1 = driver.capabilities['browserVersion']
    # str2 = driver.capabilities['chrome']['chromedriverVersion'].split(' ')[0]
    # print(str1)
    # print(str2)
    # print(str1[0:2])
    # print(str2[0:2])

    # WebDriverWait(driver, waitTime).until(
    #     EC.presence_of_element_located((By.XPATH, "//*[@id='nav-main']/div/a[2][text()='Sign Up']")))
    # sleep(5)
    # print('1')
    #
    # CheckReCAPTCHA(driver)

    #Sign_Up_button = driver.find_element(By.XPATH, "//button[text()='Sign Up']")
    Sign_Up_button = WebDriverWait(driver, waitTime).until(
        EC.element_to_be_clickable((By.XPATH, "//*[@id='nav-main']/div/a[2][text()='Sign Up']")))
        # EC.presence_of_element_located((By.XPATH, "//*[@id='nav-main']/div/a[2][text()='Sign Up']")))
    sleep(5)
    # Sign_Up_button = driver.find_element(By.XPATH, "//*[@id='nav-main']/div/a[2][text()='Sign Up']")
    Sign_Up_button.click()

    print('2')
    # driver.close()
    # driver.quit()
    print('3')
    sleep(5)
    CheckReCAPTCHA(driver)
    print('4')
    # //*[@id="main"]/div/div/div/div/div[1]/div[2]/div[1]/div[1]/button/div/span/span
    # WebDriverWait(driver, waitTime).until(
    #     EC.presence_of_element_located((By.XPATH,
    #        "//*[@id='main']/div/div/div/div/div[1]/div[2]/div[1]/div[1]/button/div/span/span[text()='Continue with Google']")))
    print('5')
    Continue_with_Google = WebDriverWait(driver, waitTime).until(
        EC.element_to_be_clickable((By.XPATH,
        # EC.presence_of_element_located((By.XPATH,
           "//*/span[text()='Continue with Google']")))
    print('6')
    sleep(5)
    CheckReCAPTCHA(driver)
    # Continue_with_Google = driver.find_element(By.XPATH, "//*/span[text()='Continue with Google']")
    Continue_with_Google.click()
    sleep(5)
    print('7')
    return driver


def ClearFile(filename):
    with open(filename, "w", encoding='utf-8') as file:
        file.write(datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"+'\n\n'))


def UpWorkParseLinks(driver):
    print('UpWorkParseLinks...')

    FindWorkBtn = WebDriverWait(driver, waitTime).until(
        EC.element_to_be_clickable((By.XPATH, "//*/a/span[1][text()='Find Work']")))
        # EC.presence_of_element_located((By.XPATH, "//*/a/span[1][text()='Find Work']")))
    FindWorkBtn.click()

    print('7')
    WebDriverWait(driver, waitTime).until(
        EC.presence_of_element_located((By.XPATH,
           "//*/h2[contains(@class, 'col mb-10')]")))
    print('8')
    print('Parsing...')
    main_page = driver.page_source
    soup = BeautifulSoup(main_page, 'lxml')

    with open('pages/main_page.html', "w", encoding='utf-8') as file:
        file.write(main_page)

    jobs = soup.find_all('h4', class_='my-0 p-sm-right job-tile-title')
    print(len(jobs))
    # main_url = 'https://www.upwork.com'

    # ClearFile(f'pages/url_pages.html')

    with open(f'pages/url_pages.html', "a") as file:
        for i, job in enumerate(jobs):
            text = job.find('a').get_text()
            print(text)
            href = job.find('a').attrs['href']
            print(href)
            print()
            # with open(f'pages/href_page{i:03d}.html', "w") as file:
            #     file.write(href)

            # file.write(text + '\n')
            translate_text = str(translate(text))
            file.write('\n' + text + '\n\n' + translate_text + '\n\n' + URL + href + '\n\n\n')

    # Scrolling block ------------

    # Delay time for UpWork
    sleep(2)

    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(uniform(TIME_SLEEP[0], TIME_SLEEP[1]))
        new_height = driver.execute_script("return document.body.scrollHeight")

        if new_height == last_height:
            break
        last_height = new_height
    # Scrolling block - end ------

    # xpath1 = '//*/footer/button/text()'
    # ---- xpath1 = '//*/footer/button[@text()]'
    # xpath1 = '//*/footer/button'
    xpath1 = '//*/footer/button[@type="button"]'
    # ---- xpath1 = r'//*/footer/button[@text()=" \n        Load More Jobs\n      "]'
    # ----- xpath1 = r'//*/footer/button[@text()="Load More Jobs"]'
    xpath2 = "//*/button[@data-test='load-more-button']/text()"
    print('finding Load More Jobs = ' + xpath1)

    try:
        print('Wait Button')
        # WebDriverWait(driver, waitTime).until(
        #     EC.element_to_be_clickable((By.XPATH, xpath1)))
        # find_element_by_xpath("//input[@type='file']")
        # print('Find Button')
        # NextBtn = driver.find_element(By.XPATH, xpath1)
        NextBtn = WebDriverWait(driver, waitTime).until(
             EC.element_to_be_clickable((By.XPATH, xpath1)))
        print('Button1 found')
    except Exception as Error:
        print('Button1 not found', Error)
        NextBtn = None
    # print('finding2 Load More Jobs  =' + xpath1)
    # try:
    #     NextBtn = WebDriverWait(driver, waitTime).until(
    #         EC.presence_of_element_located((By.XPATH, xpath2)))
    #     print('Button2 found')
    # except Exception as Error:
    #     print('Button2 not found:', Error)
    print(isBSfindInHTML(main_page, xpath1), '   ', xpath1)
    # print(isBSfindInHTML(main_page, xpath2), '   ', xpath2)
    print('end finding Load More Jobs\n\n\n')
    sleep(delayTime)
    if NextBtn:
        print('before NextBtn.click()')
        if NextBtn.is_enabled():
            print('Enabled')
            try:
                # # print(f'{len(NextBtn)=}')
                # print(f'{type(NextBtn)=}')
                # print(f'{type(NextBtn[0])=}')
                """
                print('driver.refresh()')
                driver.refresh()
                sleep(5)
                """

                print('action = ActionChains(driver)')
                action = ActionChains(driver)
                print('action.move_to_element(NextBtn).perform()')
                action.move_to_element(NextBtn).perform()
                sleep(10)
                # # wait.until(
                # #     EC.presence_of_element_located((By.XPATH, xpath1))).send_keys(Keys.RETURN)
                # sleep(5)
                print('\naction.send_keys(Keys.RETURN)')
                action.send_keys(Keys.RETURN)
                sleep(10)
                print('\nNextBtn.send_keys(Keys.RETURN)')
                NextBtn.send_keys(Keys.RETURN)
                sleep(10)
                print('\naction.move_to_element(NextBtn).click().perform()')
                action.move_to_element(NextBtn).click().perform()
                # action.move_to_element(NextBtn).click().perform()
                # sleep(5)
                # print('driver.execute_script("arguments[0].click();", NextBtn)')
                # driver.execute_script("arguments[0].click();", NextBtn)
                sleep(10)
                print('\nNextBtn.click()')
                NextBtn.click()
                sleep(10)
                print('\nNextBtn.send_keys(Keys.ENTER)')
                NextBtn.send_keys(Keys.ENTER)
                # sleep(5)
                # print('NextBtn.submit()')
                # NextBtn.submit()
                # print('NextBtn.submit()')
                # print(f'{(NextBtn)=}')
                print(f'{type(NextBtn)=}')
                print(f'{dir(NextBtn)=}')
                sleep(10)
                print("\ndriver.execute_script(\"document.getElementsByClassName(\'up-btn up-btn-default up-btn-sm mb-0\')[0].click();\")")
                driver.execute_script("document.getElementsByClassName('up-btn up-btn-default up-btn-sm mb-0')[0].click();")

                # driver.execute_script("document.getElementById('theIdName').click()")
                # print( "driver.execute_script(\"document.getElementByXpath('//*/footer/button[@type=\"button\"]').click()\")")
                # driver.execute_script("document.getElementByXpath('//*/footer/button[@type=\"button\"]').click()")
                sleep(10)
                print("driver.execute_script(\"\n(document.evaluate(\"//*/footer/button[@type=\'button\']\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue).click();\")")

                driver.execute_script(
                    "\n(document.evaluate(\"//*/footer/button[@type=\'button\']\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue).click();")
                sleep(10)
                print('driver.execute_script("arguments[0].click();", NextBtn)')
                driver.execute_script("arguments[0].click();", NextBtn)
                # sleep(2)
                # print(f'{NextBtn.getText()=}')
                # # release()
            except Exception as Err:
                print('Error: ', Err)
    else:
        print('if NextBtn: else !!!!')
    sleep(delayTime)
    return driver


def _get_selenium_html_page(url):
    # driver = local_init(url)
    driver = GL.GoogleAccountInit()
    demo.after_init(driver, True)
    driver.implicitly_wait(2)
    #
    driver.maximize_window()
    #
    driver = GoogleLogin(driver)
    driver = UpWorkLogin(driver)
    CheckReCAPTCHA(driver)

    driver = UpWorkParseLinks(driver)
    sleep(2000)


def isBSfindInFile(filename, xpath):
    with open(filename, "r") as file:
        main_page = file.read()
    tree = html.fromstring(main_page)
    text = tree.xpath(xpath)
    if text:
        print(text)
        return True
    else:
        return False


def isBSfindInHTML(source_html, xpath):
    tree = html.fromstring(source_html)
    text = tree.xpath(xpath)
    if text:
        print(type(text), ' | ', text)
        filename = 'text-'+str(text).replace('<','').replace('>','').replace('\n','')\
            .replace('/','').replace('\\','')+'.txt'
        print(f'{filename=}')
        with open(f'{filename}', 'w', encoding='utf-8') as file:
            file.write(str(dir(text)))
        return True
    else:
        return False


def test():
    with open('pages/main_page.html', "r") as file:
        main_page = file.read()
    soup = BeautifulSoup(main_page, 'lxml')
    jobs = soup.find_all('h4', class_='my-0 p-sm-right job-tile-title')
    print(len(jobs))
    main_url = 'https://www.upwork.com'
    with open(f'pages/url_pages.html', "a") as file:
        file.write('\n\n')
    for i, job in enumerate(jobs):
        print(job.find('a').get_text())
        href = job.find('a').attrs['href']
        print(URL+href)
        req = requests.get(URL+href, headers=header )
        sleep(10)
        with open(f'pages/url_pages.html', "a") as file:
            file.write(req.text+'\n')
    return


def test2():
    option = demo.driver_init(True, False)
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=option)
    driver.maximize_window()
    driver.get('https://beta.speedtest.net/ru')
    demo.after_init(driver, False)
    path = '//*[@id="container"]/div/div[3]/div/div/div/div[2]/div[3]/div[1]/a/span[4]'
    btn = WebDriverWait(driver, 100).until(
         EC.element_to_be_clickable((By.XPATH, path)))
    print('action = ActionChains(driver)')
    action = ActionChains(driver)
    # //*[@id="main-menu"]/nav[1]/ul/li[1]/a/span[2]
    #btn.click()
    print('action.move_to_element(btn).perform()')
    action.move_to_element(btn).perform()
    for i in range(20):
        print('action.send_keys(Keys.TAB)')
        action.send_keys(Keys.TAB)
        sleep(3)
    sleep(10)



if __name__ == '__main__':
    # test2()
    # file = 'pages/main_page.html'
    # path1 = '//*/footer/button/text()'
    # path2 = "//*/button[@data-test='load-more-button']/text()"
    # print(isBSfindInFile(file, path1), '   ', path1)
    # # print(isBSfind(file, "//*/footer/button[@text()='Load More Jobs]'"),
    # #         '   ', "//*/footer/button[@text()='Load More Jobs']")
    # print(isBSfindInFile(file, path2), '   ', path2)

    ClearFile(f'pages/url_pages.html')
    _get_selenium_html_page(URL)
    print('OK   ')
    # run()
