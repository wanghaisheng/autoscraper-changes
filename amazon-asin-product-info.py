from amazon_buddy import Product, AmazonBuddy, Category, SortType
import pandas as pd
from pathlib import Path
import random

OUTPUT_DIR = Path("data")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR = str(OUTPUT_DIR)

ab = AmazonBuddy(debug=True)


df_queries = pd.read_csv("asins.csv")



for i, asin in df_queries.iterrows():
    print(asin)
    asinid=asin['asin']
    print(asinid)
    
    if  asinid.empty():
        pass
    elif asinid=='asin':
        pass
    else:
        reviews = ab.get_reviews(asin=asinid)
        print(asinid)
        reviews.save(OUTPUT_DIR+'{}-reviews.json'.format(asinid))

        ab.get_product_details(asinid).save(OUTPUT_DIR+'{}.json'.format(asinid))

        time.sleep(random.randint(5,50))
