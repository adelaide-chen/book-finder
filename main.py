from bs4 import BeautifulSoup
import requests
import pyrebase


CONFIG = {
  "apiKey": "AIzaSyCppLTkbikfSJBXS5aY9uW7iEoqQsEHlz4",
  "authDomain": "find-books-by-rating.firebaseapp.com",
  "databaseURL": "https://find-books-by-rating-default-rtdb.firebaseio.com",
  "projectId": "find-books-by-rating",
  "storageBucket": "find-books-by-rating.appspot.com",
  "messagingSenderId": "590127508190",
  "appId": "1:590127508190:web:8884527a31e6bfac93b04f",
  "measurementId": "G-DEYZRLW2V0"
}

FIREBASE = pyrebase.initialize_app(CONFIG)

API_KEY = "1OAz00GvVLfXiOnfQ6BP1M2GVRS8qpCa"

response = requests.get(f"https://api.nytimes.com/svc/books/v3/lists/names?api-key={API_KEY}")
body = response.json()


def cleanup_string(text):
    # result from HTML tags extracted with BeautifulSoup
    return [string.strip() for string in text.split('\n') if string is not ''][0]


def get_goodreads_info(isbn):
    # Given ISBN, return rating value and count for book from Goodreads
    response = requests.get(f"https://www.goodreads.com/search?q={isbn}")
    soup = BeautifulSoup(response.text, 'html.parser')
    rating_value = cleanup_string(soup.find(itemprop='ratingValue').text)
    rating_count = cleanup_string(soup.find(itemprop='ratingCount').text)
    title = soup.find(attrs={'property': 'og:title'})['content']
    author = soup.find(attrs={'class': 'authorName'}).find(itemprop='name').text
    link = soup.find(attrs={'property': 'og:url'})['content']
    return (title, author, rating_value, rating_count, link)


def get_books(genres, date=None):
    # Given genre from NYTimes bestsellers list, return Goodreads rating values and counts for each book
    books = []
    for genre in genres:
        response = requests.get(f"https://api.nytimes.com/svc/books/v3/lists.json?list={genre}&api-key={API_KEY}")
        result = response.json()['results']
        books += [get_goodreads_info(book['book_details'][0]['primary_isbn13']) for book in result]
    return books

get_books(["espionage"])