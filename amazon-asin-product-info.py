from amazon_buddy import Product, AmazonBuddy, Category, SortType
import pandas as pd
from pathlib import Path


OUTPUT_DIR = Path("data")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR = str(OUTPUT_DIR)

ab = AmazonBuddy(debug=True, user_agent='ADD_USER_AGENT')


df_queries = pd.read_csv("asin-queries-unique.csv")



for i, query in df_queries.iterrows():
    # print(query)
    asin=query['asin']
    print(asin)
    if not asin=='' or not asin=='asin' or not asin==' ':
        reviews = ab.get_reviews(asin=asin)
        # print(reviews)
        reviews.save(OUTPUT_DIR+'{}-reviews.json'.format(asin))

        ab.get_product_details(asin).save(OUTPUT_DIR+'{}.json'.format(asin))

