from amazon_buddy import Product, AmazonBuddy, Category, SortType
import pandas as pd
from pathlib import Path


OUTPUT_DIR = Path("data")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR = str(OUTPUT_DIR)

ab = AmazonBuddy(debug=True)


df_queries = pd.read_csv("asins.csv")



for i, asin in df_queries.iterrows():
    if not asin=='' or not asin=='asin' or not asin==' ' or not pd.isna(asin):
        print(asin)
        reviews = ab.get_reviews(asin=asin)
        # print(reviews)
        reviews.save(OUTPUT_DIR+'{}-reviews.json'.format(asin))

        ab.get_product_details(asin).save(OUTPUT_DIR+'{}.json'.format(asin))

