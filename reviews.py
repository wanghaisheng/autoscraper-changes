from google_play_scraper import reviews_all
from app_store_scraper import AppStore
from google_play_scraper import app
import csv
from pathlib import Path
import pandas as pd

OUTPUT_DIR = Path("data")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR = str(OUTPUT_DIR)
# package_name = 'com.netcompany.smittestop_exposure_notification'
package_name= 'com.bemyeyes.bemyeyes'

googlerows = []
def play_store_scraper(package):
    results = reviews_all(package)


    # Adds the fields to the CSV
    for x, item in enumerate(results):
        googlerows.append(item)

    

    df = pd.DataFrame(googlerows)
    df.to_csv("google-app-review.csv", index=False)

applerows = []

def app_store_scraper(app_name):
    app = AppStore(country="dk", app_name=app_name)
#     app.review(how_many=1000)
    app.review()



    for review in app.reviews:
        score = review['rating']
        username = review['userName']
        review = review['review']
        applerows.append(review)

        try:
            print(f'{username} says: {review}')
            writer.writerow({'username': username, 'review': review, 'score': score})
        except:
            print('Failed to add entry XXX')
    df = pd.DataFrame(applerows)
    df.to_csv("apple-app-review.csv", index=False)

play_store_scraper(package_name)
app_store_scraper('be-my-eyes')