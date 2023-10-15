import asyncio

import pandas
from fastapi import APIRouter, Query, Path

import data_loader
from classes.book import Book

app = APIRouter()


user_ratings, library = data_loader.data_reader("Downloads/BX-Books.csv", "Downloads/BX-Book-Ratings.csv")


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/")
async def get_all_books(rating: float | None = None, ratings_amount: float | None = None, author: str | None = None) -> \
        dict[str, Book]:
    if rating is None and ratings_amount is None:
        return library
    books = {}
    for isbn, book in library.items():
        if (rating is None or book.avg_rating() > rating) and \
                (ratings_amount is None or book.num_of_ratings() > ratings_amount) and \
                (author is None or author.lower() in book.author.lower()):
            books[isbn] = book

    return books


@app.get("/{isbn}")
async def get_by_isbn(isbn: str):
    book = library.get(isbn)
    return book


@app.get("/{isbn}/getreadersrating/{id}")
def get_rating_of_a_reader(isbn: str, id: float) -> str | float:
    if library.get(isbn) is None:
        return "Book doesnt exist"
    book = library.get(isbn)
    if book.ratings.get(id) is None:
        return "Reader hasnt rated this book"
    return float(library.get(isbn).ratings.get(id))


# @app.get("/books/findbyauthor/{author}")
# async def get_by_author(author: str):
#     return [book for _, book in test.items() if book.author and author.lower() in book.author.lower()]


@app.get("/{isbn}/getreaders")
async def get_readers_by_books(isbn: str) -> list[str]:
    readers = set()
    for tmp in isbn.split(","):
        for user_id, _ in library[tmp].ratings.items():
            readers.add(str(user_id))
    return list(readers)


@app.get("/reader/getbooks/")
async def get_books_of_reader(user_id: str) -> list[str]:
    books = set()
    for tmp in user_id.split(","):
        for isbn in user_ratings[tmp]:
            books.add(isbn)
    return list(books)


@app.get("/{isbn}/recommendbooks")
async def recommend_book(isbn: str = Path(description="ISBN code of the book"), rating: float | None = Query(None, description="Rating threshold"), ratings_amount: float | None = Query(None, description="Amount of ratings threshold"), top: int = Query(10, description="Specifies how many of recommendations to return")):
    '''
      Returns a list of reccomended books for given book.

      ---

      '''
    readers = await get_readers_by_books(isbn)

    tasks = [get_books_of_reader(",".join(readers)), get_all_books(rating, None, None)]
    result = await asyncio.gather(*tasks)
    books_of_readers, rated_books = result[0], result[1]

    rated_books_of_readers = [book for isbn, book in rated_books.items() if isbn in books_of_readers
                              and (ratings_amount is None or len([rating for rating in book.ratings.keys() if str(rating) in readers]) >= ratings_amount)]
    print(rated_books_of_readers)
    book = library[isbn]
    if book in rated_books_of_readers:
        rated_books_of_readers.remove(book)
    df = []
    df_readers = pandas.DataFrame(readers, columns=['id'], dtype=str)

    for book in rated_books_of_readers:
        df_readers[book.title.lower()] = df_readers.apply(
            lambda row: float(get_rating_of_a_reader(str(book.isbn), float(row['id']))) if type(
                get_rating_of_a_reader(str(book.isbn), float(row['id']))) == float else 0.0, axis=1)
    print(df_readers)
    df_readers.set_index("id", inplace=True)

    for corr_book in rated_books_of_readers:
        df.append([corr_book.title, df_readers[book.title.lower()].corr(df_readers[corr_book.title.lower()]),
                   corr_book.avg_rating()])

    corr_fellowship = pandas.DataFrame(df, columns=['book', 'corr', 'avg_rating'])
    return corr_fellowship.sort_values('corr', ascending=False).head(top).to_dict(orient='records')
