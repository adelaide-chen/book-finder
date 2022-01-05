from bs4 import BeautifulSoup
import requests
import pyrebase
import api_things

# config for firebase's API
FIREBASE = pyrebase.initialize_app(api_things.CONFIG)
DATABASE = FIREBASE.database()

# API key for NY Times
API_KEY = api_things.API_KEY


def cleanup_string(text):
    # result from HTML tags extracted with BeautifulSoup
    return [string.strip() for string in text.split("\n") if string != ""][0]


def get_goodreads_info(isbn):
    # Given ISBN, return rating value and count for book from Goodreads
    response = requests.get(f"https://www.goodreads.com/search?q={isbn}")
    soup = BeautifulSoup(response.text, "html.parser")
    rating_value = cleanup_string(soup.find(itemprop="ratingValue").text)
    rating_count = cleanup_string(soup.find(itemprop="ratingCount").text)
    title = soup.find(attrs={"property": "og:title"})["content"]
    author = soup.find(attrs={"class": "authorName"}).find(itemprop="name").text
    link = soup.find(attrs={"property": "og:url"})["content"]
    print(title)
    return {
        "title": title,
        "author": author,
        "rating_value": rating_value,
        "rating_count": rating_count,
        "link": link,
        "isbn": isbn,
    }


def add_books_by_genre_and_date(genre, date=None):
    # Given genre and date from NYTimes bestsellers list, retrieve Goodreads details for each book and push to database
    response = requests.get(
        f"https://api.nytimes.com/svc/books/v3/lists.json?list={genre}&api-key={API_KEY}"
    )
    result = response.json()["results"]
    for book in result:
        data = get_goodreads_info(book["book_details"][0]["primary_isbn13"])
        push_book_to_db(genre, data)
    print("done!")


def push_book_to_db(genre, book):
    # Given book details and genre, add to FireBase
    DATABASE.child(genre).child(book["isbn"]).set(book)


# add_books_by_genre_and_date("espionage")
