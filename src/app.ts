//@ts-check
const { chromium, webkit, firefox } = require("playwright");
const http = require('http');
const express = require('express');
import { Request, Response, Application } from 'express';
const cors = require("cors");
const fs = require("fs");
// const cron = require('node-cron')
import https from 'https';
import { GoogleSERP } from 'serp-parser'

const app: Application = express();
app.use(cors());


async function wait(ms: number) {
  return new Promise((resolve, reject) => {
    setTimeout(resolve, ms)
  });
}
async function searchsitemap(url: String) {
  const browser = await webkit.launch();
  // Create a new incognito browser context.
  const context = await browser.newContext(
    {
      headless: false,
      ignoreHTTPSErrors: true,
      proxy: { server: 'socks5://127.0.0.1:1080' }
      ,
    });
  const page = await browser.newPage();

  await page.goto('https://www.google.com/search?q=' + url + '++sitemap.xml');


  const parser = new GoogleSERP(await page.content());
  console.dir(parser.serp['organic']);

  const sitemapcandidate: Array<string> = []
  for (let i = 0; i < parser.serp['organic'].length; i++) {
    let url = parser.serp['organic'][i]['url']
    if (url.includes('.xml')) {

      fs.writeFileSync("shopify-sitemap-mapping.txt", +',' + url)
      sitemapcandidate.push(url)
    }
    //use i instead of 0

  }
  return sitemapcandidate

}

async function parseSitemap(url: string) {
  const browser = await webkit.launch();
  // Create a new incognito browser context.
  const context = await browser.newContext(
    {
      headless: false,
      ignoreHTTPSErrors: true,
      proxy: { server: 'socks5://127.0.0.1:1080' }
      ,
    });
  const page = await browser.newPage();
  const url_list: Array<string> = []
  const res = await page.goto(url);
  if (res.status() == 200) {

    const sitemaps = page.locator('sitemap')
    const sitemaps_count = await sitemaps.count()
    if (sitemaps_count > 1) {
      const cato = []
      for (let i = 0; i < sitemaps_count; i++) {
        const sitemap_url = sitemaps.nth(i).locator('loc').textContent()
        await page.goto(sitemap_url)
        const urls = page.locator('loc')
        for (let i = 0; i < await urls.count(); i++) {
          const url = urls.nth(i).textContent()
          url_list.push(url)
        }
      }
    } else {

      const urls = page.locator('loc')
      for (let i = 0; i < await urls.count(); i++) {
        const url = urls.nth(i).textContent()
        url_list.push(url)
      }


    }
  } else {

    console.log('this url is not a valid sitemap url')

  }
  return url_list


}

async function get_shopify_defaut_sitemap(url: string) {
  let url_list_tmp: Array<string> = []
  let url_list: Array<string> = []

  const default_sitemap_url = new URL(url).hostname + '/sitemap.xml'
  const default_sitemap_url_list = await parseSitemap(default_sitemap_url)
  if (default_sitemap_url_list.length == 0) {
    console.log('try search sitemap url')
    const sitemapcandiates = await searchsitemap(url)
    const sitemapcandiates_url_list: Array<string> = []
    if (sitemapcandiates.length > 1) {
      for (let i = 0; i < sitemapcandiates.length; i++) {
        const sitemapcandiates_url = sitemapcandiates[i]
        const sitemapcandiates_url_list = await parseSitemap(sitemapcandiates_url)
        url_list.push.apply(url_list, sitemapcandiates_url_list)
      }

    } else {

      console.log('there is no candidacted sitemap in serp result')
    }


  } else {
    url_list.push.apply(url_list, default_sitemap_url_list)


  }

  return Array.from(new Set(url_list));
}
function check_url_cato(url: string) {
  if (url.includes('/pages/')) {

  } else if (url.includes('/products/')) {


  } else if (url.includes('/collections/')) {

  } else if (url.includes('/blogs/')) {

  } else {


  }



}
async function checkstoreispassword(url: string) {
  const browser = await webkit.launch();
  // Create a new incognito browser context.
  const context = await browser.newContext(
    {
      headless: false,
      ignoreHTTPSErrors: true,
      proxy: { server: 'socks5://127.0.0.1:1080' }
      ,
    });
  const page = await browser.newPage();

  const res = await page.goto(url);
  const redirect_url = res.url
  if (redirect_url.includes('password')) {
    console.log('this site is under construction')
    return true
  } else {

    return false
  }




}


async function upsertFile(name: string) {
  try {
    // try to read file
    await fs.promises.readFile(name)
  } catch (error) {
    // create empty file, because it wasn't found
    await fs.promises.writeFile(name, '')
  }
}


function createFile(filename: string) {
  fs.open(filename, 'r', function (err: any, fd: any) {
    if (err) {
      fs.writeFile(filename, '', function (err: any) {
        if (err) {
          console.log(err);
        }
        console.log("The file was saved!", filename);
      });
    } else {
      console.log("The file exists!", filename);
    }
  });
}


async function homepage(browser: { newPage: () => any; newContext: (arg0: { headless: boolean; ignoreHTTPSErrors: boolean; }) => any; }, url: String) {

  const context = await browser.newContext(
    {
      headless: false,
      ignoreHTTPSErrors: true,
      // proxy: { server: 'socks5://127.0.0.1:1080' },
    });
  const page = await browser.newPage();


  await page.goto('https://www.merchantgenius.io')
  // console.log(await page.content())
  const yuefen = page.locator('xpath=//html/body/main/div/div[2]/a')
  // console.log('1-', await yuefen.count())
  const yuefen2 = page.locator('div.container > a')
  // console.log('2-', await yuefen2.count())


  const yuefen3 = page.locator('[href^="/shop/date/"]')
  // console.log('-', await yuefen3.count())

  createFile('shopify-catalog.txt')

  const cato = []
  for (let i = 0; i < await yuefen.count(); i++) {
    const suburl = await yuefen.nth(i).getAttribute('href')
    const filename = suburl.split('/').pop()
    console.log('name', filename)
    const url = 'https://www.merchantgenius.io' + suburl
    console.log(url)
    // <a href="/shop/date/2020-08-29"
    const history = fs.readFileSync('shopify-catalog.txt').toString().replace(/\r\n/g, '\n').split('\n');
    const log = fs.createWriteStream('shopify-catalog.txt', { flags: 'a' });

    // on new log entry ->
    console.log(history.includes(url))
    if (history.includes(url) == false) {
      log.write(url + "\n");

    }
    // you can skip closing the stream if you want it to be opened while
    // a program runs, then file handle will be closed
    log.end();

    cato.push(filename)

  }
  return cato


}

async function leibiexiangqing(browser: { newPage: () => any; newContext: (arg0: { headless: boolean; ignoreHTTPSErrors: boolean; }) => any; }, cato: Array<string>) {
  const context = await browser.newContext(
    {
      headless: false,
      ignoreHTTPSErrors: true,
      // proxy: { server: 'socks5://127.0.0.1:1080' },
    });
  const p_page = await browser.newPage();

  createFile('shopify-merchantgenius.txt')

  for (let i = 0; i < cato.length; i++) {
    const filename = cato[i]
    const url = 'https://www.merchantgenius.io/shop/date/' + filename
    console.log('dig url published on ', url)
    let domains: Array<string> = []


    await p_page.goto(url, { timeout: 0 })
    // console.log(await p_page.content())
    const shopurls = p_page.locator('[href^="/shop/url/"]')
    const history = fs.readFileSync("merchantgenius/shopify-" + filename + ".txt").toString().replace(/\r\n/g, '\n').split('\n');
    console.log('loading exisit domain', history.length)

    const tmp = p_page.locator('div.container:nth-child(4) > table:nth-child(1)').textContent()
    const url_count = tmp.split('A total of').pop().split('stores')[0]
    console.log('total count in page', url_count, 'we detected ', await shopurls.count())

    if (await shopurls.count() < history.length) {
      console.log('there is need to   saving')
    } else {

      for (let i = 0; i < await shopurls.count(); i++) {
        const url = await shopurls.nth(i).getAttribute('href')
        const domain = url.split('/shop/url/').pop()
        if (domains.includes(domain)) {

        } else {
          domains.push(domain)
          console.log('bingo', domain)

        }
      }
      const uniqdomains = Array.from(new Set(domains));
      console.log('founded domains', uniqdomains.length, ' under ', filename)
      console.log('============start saving==========', filename)

      createFile("merchantgenius/shopify-" + filename + ".txt")
      savedomains(uniqdomains, filename)
      console.log('============finish saving==========', filename)

    }
  }
}
function savedomains(uniqdomains: Array<string>, filename: string) {

  const catohistory = fs.readFileSync('shopify-merchantgenius.txt').toString().replace(/\r\n/g, '\n').split('\n');
  console.log('loading exisit domain', catohistory.length)
  const log1 = fs.createWriteStream('shopify-merchantgenius.txt', { flags: 'a' });
  // console.log('saving domain to index text',uniqdomains[i])
  const history = fs.readFileSync("merchantgenius/shopify-" + filename + ".txt").toString().replace(/\r\n/g, '\n').split('\n');
  console.log('loading exisit domain', catohistory.length)

  const log = fs.createWriteStream("merchantgenius/shopify-" + filename + ".txt", { flags: 'a' });

  for (let i = 0; i < uniqdomains.length; i++) {

    if (catohistory.includes(uniqdomains[i]) == false) {
      log1.write(uniqdomains[i] + "\n");
    }
    // console.log('saving domain to ',"merchantgenius/shopify-" + filename + ".txt")


    // on new log entry ->
    if (history.includes(uniqdomains[i]) == false) {
      log.write(uniqdomains[i] + "\n");
    }
  }
  log1.end();

  log.end();


}

app.get("/:targetName", async (req: Request, res: Response) => {


  try {
    const browser = await webkit.launch();
    const context = await browser.newContext(
      {
        headless: false,
        ignoreHTTPSErrors: true
        // proxy: { server: 'socks5://127.0.0.1:1080' },
      });

    const cato = await homepage(browser, '')
    const uniqdomains = await leibiexiangqing(browser, cato)

  } catch (error) {
    console.log('error===', error)


  }

  //   {
  //     "keyword: "google",
  //     "totalResults": 15860000000,
  //     "timeTaken": 0.61,
  //     "currentPage": 1,
  //     "pagination": [
  //       { page: 1,
  //         path: "" },
  //       { page: 2,
  //         path: "/search?q=google&safe=off&gl=US&pws=0&nfpr=1&ei=N1QvXKbhOLCC5wLlvLa4Dg&start=10&sa=N&ved=0ahUKEwjm2Mn2ktTfAhUwwVkKHWWeDecQ8tMDCOwB" },
  //       ...
  //     ],
  //     "videos": [
  //       { title: "The Matrix YouTube Movies Science Fiction - 1999 $ From $3.99",
  //         sitelink: "https://www.youtube.com/watch?v=3DfOTKGvtOM",
  //         date: 2018-10-28T23:00:00.000Z,
  //         source: "YouTube",
  //         channel: "Warner Movies On Demand",
  //         videoDuration: "2:23" },
  //       ...
  //     ],
  //     "thumbnailGroups": [
  //         { "heading": "Organization software",
  //           "thumbnails:": [ {
  //             "sitelink": "/search?safe=off&gl=US&pws=0&nfpr=1&q=Microsoft&stick=H4sIAAAAAAAAAONgFuLUz9U3MDFNNk9S4gAzi8tMtGSyk630k0qLM_NSi4v1M4uLS1OLrIozU1LLEyuLVzGKp1n5F6Un5mVWJZZk5ucpFOenlZQnFqUCAMQud6xPAAAA&sa=X&ved=2ahUKEwjm2Mn2ktTfAhUwwVkKHWWeDecQxA0wHXoECAQQBQ",
  //             "title": "Microsoft Corporation"
  //           },
  //           ...
  //         ]
  //       },
  //       ...
  //     ],
  //     "organic": [
  //       {
  //         "domain": "www.google.com",
  //         "position": 1,
  //         "title": "Google",
  //         "url": "https://www.google.com/",
  //         "cachedUrl": "https://webcache.googleusercontent.com/search?q=cache:y14FcUQOGl4J:https://www.google.com/+&cd=1&hl=en&ct=clnk&gl=us",
  //         "similarUrl": "/search?safe=off&gl=US&pws=0&nfpr=1&q=related:https://www.google.com/+google&tbo=1&sa=X&ved=2ahUKEwjm2Mn2ktTfAhUwwVkKHWWeDecQHzAAegQIARAG",
  //         "linkType": "HOME",
  //         "sitelinks": [
  //           { "title": "Google Docs",
  //             "snippet": "Google Docs brings your documents to life with smart ...",
  //             "type": "card" },
  //           { "title": "Google News",
  //             "snippet": "Comprehensive up-to-date news coverage, aggregated from ...",
  //             "type": "card" },
  //           ...
  //         ],
  //         "snippet": "Settings Your data in Search Help Send feedback. AllImages. Account · Assistant · Search · Maps · YouTube · Play · News · Gmail · Contacts · Drive · Calendar."
  //       },
  //       {
  //         "domain": "www.google.org",
  //         "position": 2,
  //         "title": "Google.org: Home",
  //         "url": "https://www.google.org/",
  //         "cachedUrl": "https://webcache.googleusercontent.com/search?q=cache:Nm9ycLj-SKoJ:https://www.google.org/+&cd=24&hl=en&ct=clnk&gl=us",
  //         "similarUrl": "/search?safe=off&gl=US&pws=0&nfpr=1&q=related:https://www.google.org/+google&tbo=1&sa=X&ved=2ahUKEwjm2Mn2ktTfAhUwwVkKHWWeDecQHzAXegQIDBAF",
  //         "linkType": "HOME",
  //         "snippet": "Data-driven, human-focused philanthropy powered by Google. We bring the best of Google to innovative nonprofits that are committed to creating a world that..."
  //       },
  //       ...
  //     ],
  //     "relatedKeywords": [
  //       { keyword: google search,
  //         path: "/search?safe=off&gl=US&pws=0&nfpr=1&q=google+search&sa=X&ved=2ahUKEwjm2Mn2ktTfAhUwwVkKHWWeDecQ1QIoAHoECA0QAQ" },
  //       { keyword: google account,
  //         path: "/search?safe=off&gl=US&pws=0&nfpr=1&q=google+account&sa=X&ved=2ahUKEwjm2Mn2ktTfAhUwwVkKHWWeDecQ1QIoAXoECA0QAg" },
  //       ...
  //     ]
  //   }



})


app.listen(8083, () => {
  console.log("server started");

  // cron.schedule("* * * * *", function () {
  //   // API call goes here
  //   console.log("running a task every minute");
    const options = {
      hostname: 'localhost',
      port: 8082,
      path: '/todos',
      method: 'GET'
    }    
    http.get(options, function (error: any, response: { statusCode: number; }, body: any) {
      if (!error && response.statusCode == 200) {
        console.log(body) // Print the google web page.
      }
    })
  // })
})
