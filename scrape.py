import requests
from amazon_buddy import Product, AmazonBuddy, Category, SortType

import pandas as pd
from bs4 import BeautifulSoup


ab = AmazonBuddy(debug=True)
df_queries = pd.read_csv("queries.csv")
queries = df_queries.queries
rows = []

for query in queries:

    products = ab.search_products(
        query,
        sort_type=SortType.PRICE_HIGH_TO_LOW,
        min_price=0,
        category=Category.BEAUTY_AND_PERSONAL_CARE,
        max_results=500
    )
    for p in products:
        row={}
        row['asin']=p.asin
        rows.append(p)
        reviews = ab.get_reviews(asin=p.asin)
        print(reviews)
        reviews.save('{}-reviews.json'.format(p.asin))

        ab.get_product_details(p.asin).save('{}.json'.format(p.asin))
# ab.get_product_details(asin).jsonprint()

# for story in stories:
#     row = {}

#     row['title'] = story.select_one('h3').text.strip()

#     try:
#         row['href'] = story.select_one('.media__link, .reel__link')['href']
#     except:
#         pass

#     try:
#         row['tag'] = story.select_one('.media__tag').text.strip()
#     except:
#         pass

#     try:
#         row['summary'] = story.select_one('.media__summary').text.strip()
#     except:
#         pass

#     rows.append(row)

df = pd.DataFrame(rows)
df.to_csv("bbc-headlines.csv", index=False)
