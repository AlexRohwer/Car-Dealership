# import libraries
import requests
from bs4 import BeautifulSoup
import csv
from afinn import Afinn

# create soups list and a base URL used to track current page (1-5)
soups = []
base_url = "https://www.dealerrater.com/dealer/McKaig-Chevrolet-Buick-A-Dealer-For-The-People-dealer-reviews-23685/"

# create an HTML soup for each page
for i in range(1, 6):
    current_page = requests.get(base_url + "page" + str(i))
    current_soup = BeautifulSoup(current_page.text, "html.parser")
    soups.append(current_soup)

# gather each review from each soup corresponding to a particular page    
total_reviews = [soup.findAll("div", {"class":"col-xs-12 col-sm-9 pad-none review-wrapper"}) for soup in soups]
            
# create a new CSV file to store the results of the web scraping
with open("review_info.csv", "w", encoding="utf-8", newline="") as csv_file:
    
    # create a writer object and create headings for each column (title, text, score) for each review
    csv_writer = csv.writer(csv_file)
    headers = ["Title", "Text", "Score", "Sentiment Analysis Score"]
    csv_writer.writerow(headers)
    
    # create a sentiment analyzer
    af = Afinn()
    
    # iterate through each review
    for reviews in total_reviews:
        for review in reviews:
            # gather the title and the body text of the current review
            title = review.find(class_="no-format inline italic-bolder font-20 dark-grey").get_text().replace("\n", "")
            text = review.find(class_="font-16 review-content margin-bottom-none line-height-25").get_text().replace("\n", "")
            
            # calculate an average score for the star ratings of the current review
            # if a star rating is missing, replace it with the average
            current_score = 0
            for i in range(5, -1, -1):
                if (i != 0):
                    current_score += len(review.findAll(class_="rating-static-indv rating-" + str(i*10) + " margin-top-none td"))*i
                else:
                    num_zeroes = len(review.findAll(class_="rating-static-indv rating-00 margin-top-none td"))
                    current_score += num_zeroes*(current_score/(5-num_zeroes))
                 
            # calculate a sentiment score for the text of the review
            sentiment_score = af.score(text)
                    
            # write the result to the CSV file        
            csv_writer.writerow([title, text, current_score/5, sentiment_score])
            
# done writing, close           
csv_file.close()

# gather contents of csv file and close
csv_contents = list(csv.reader(open("review_info.csv", encoding="utf8")))
csv_file.close()

# calculate the top 3 most positive reviews, sorted by star rating first, then sentiment score
top_3 = sorted(csv_contents[1:], key=lambda row: (float(row[2]), float(row[3])), reverse=True)[:3]

# print the results to console
for top_review in top_3:
    print("Review Title:")
    print(top_review[0])
    print()
    
    print(top_review[1])
    print()
    
    print("Review Scores:")
    print("Average Star Rating (out of 5): ", top_review[2])
    print("Calculated Sentiment Score: ", top_review[3])
    print("-------------------------------------------------")
