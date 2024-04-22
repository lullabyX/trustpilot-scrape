from bs4 import BeautifulSoup
import requests
import pandas as pd
import datetime as dt
import time

# Initialize lists
review_titles = []
review_dates_original = []
review_dates = []
review_ratings_original = []
review_ratings = []
review_texts = []
page_number = []
reviewer_names = []

# Set Trustpilot page numbers to scrape here
from_page = 1
to_page = 50

def extract_rating(rating_text):
    # Split the text on spaces and extract the second element, which is the rating
    rating = int(rating_text.split()[1])
    return rating

for i in range(from_page, to_page + 1):
    response = requests.get(f"https://www.trustpilot.com/review/COMPANY_NAME?page={i}")
    web_page = response.text
    soup = BeautifulSoup(web_page, "html.parser")

    for review in soup.find_all(class_ = "styles_cardWrapper__LcCPA styles_show__HUXRb styles_reviewCard__9HxJJ"):
        # Review titles
        review_title = review.find(class_ = "typography_heading-s__f7029 typography_appearance-default__AAY17")
        review_titles.append(review_title.getText())

        # Review dates
        review_date_original = review.select_one(selector="time")
        review_dates_original.append(review_date_original.getText())

        # Convert review date texts into Python datetime objects
        review_date = review.select_one(selector="time").getText().replace("Updated ", "")
        if "hours ago" in review_date.lower() or "hour ago" in review_date.lower():
            review_date = dt.datetime.now().date()
        elif "a day ago" in review_date.lower():
            review_date = dt.datetime.now().date() - dt.timedelta(days=1)
        elif "days ago" in review_date.lower():
            review_date = dt.datetime.now().date() - dt.timedelta(days=int(review_date[0]))
        else:
            review_date = dt.datetime.strptime(review_date, "%b %d, %Y").date()
        review_dates.append(review_date)

        # Review ratings
        review_rating = review.find(class_ = "star-rating_starRating__4rrcf star-rating_medium__iN6Ty").findChild()
        review_ratings_original.append(review_rating["alt"])
        review_ratings.append(extract_rating(review_rating["alt"]))

        # Reviewer name
        reviewer_name = review.find(class_ = "typography_heading-xxs__QKBS8 typography_appearance-default__AAY17")
        reviewer_names.append(reviewer_name.getText())
        # When there is no review text, append "" instead of skipping so that data remains in sequence with other review data e.g. review_title
        review_text = review.find(class_ = "typography_body-l__KUYFJ typography_appearance-default__AAY17 typography_color-black__5LYEn")
        if review_text == None:
            review_texts.append("")
        else:
            review_texts.append(review_text.getText())
        
        # Trustpilot page number
        page_number.append(i)

# Create final dataframe from lists
df_reviews = pd.DataFrame(list(zip(review_titles, reviewer_names, review_dates_original, review_dates, review_ratings_original, review_ratings, review_texts, page_number)),
                columns =['review_title', 'reviewer_name', 'review_date_original', 'review_date', 'review_ratings_original', 'review_rating', 'review_text', 'page_number'])

# Convert to dataframe to JSON
json_data = df_reviews.to_json(orient='records', lines=False)

# Generate a timestamp in milliseconds
timestamp = int(time.time() * 1000)

# Create filename using the timestamp
filename = f"review_{timestamp}.json"

# Write JSON data to a file
with open(filename, 'w') as file:
    file.write(json_data)

print(f"Data saved to {filename}")