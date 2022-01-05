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
    attempts = 0
    while attempts < 5:
        try:
            response = requests.get(f"https://www.goodreads.com/search?q={isbn}")
            soup = BeautifulSoup(response.text, "html.parser")
            rating_value = cleanup_string(soup.find(itemprop="ratingValue").text)
            rating_count = cleanup_string(soup.find(itemprop="ratingCount").text)
            link = soup.find(attrs={"property": "og:url"})["content"]
            break
        except AttributeError:
            attempts += 1
            print(isbn)
    return {
        "rating_value": rating_value,
        "rating_count": rating_count,
        "link": link,
        "isbn": isbn,
    }


def add_books_by_genre_and_date(genre, date="current"):
    # Given genre and date from NYTimes bestsellers list, retrieve Goodreads details for each book and push to database
    response = requests.get(
        f"https://api.nytimes.com/svc/books/v3/lists/{date}/{genre}.json?api-key={API_KEY}"
    )
    result = response.json()["results"]
    books = result["books"]
    previous_published_date = result["previous_published_date"]
    already_in_database = [entry.key() for entry in DATABASE.child(genre).get().pyres]
    for book in books:
        isbn = book["primary_isbn13"]
        if isbn not in already_in_database:
            data = get_goodreads_info(isbn)
            additional_data = {
                "author": book["author"],
                "title": book["title"],
                "book_image": book["book_image"],
            }
            data.update(additional_data)
            push_book_to_db(genre, data)
    print("done!")
    return previous_published_date


def push_book_to_db(genre, book):
    # Given book details and genre, add to FireBase
    DATABASE.child(genre).child(book["isbn"]).set(book)


def get_all_books_of_genre(genre, date="current"):
    # Iterates backwards through all published bestseller lists given a genre and optional date
    previous = date
    while previous != "":
        previous = add_books_by_genre_and_date(genre, date=previous)
        print(previous)
    print("all done with books!")
