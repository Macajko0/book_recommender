from collections import defaultdict
import pandas as pd

from classes.book import Book


def data_reader(book_path, rating_path):
    books = pd.read_csv(book_path, encoding='cp1251', sep=';', on_bad_lines="skip", low_memory=False)

    books.drop(columns={"Image-URL-S", "Image-URL-M"}, inplace=True)

    # dataset = pd.merge(ratings, books, on=['ISBN'])
    # dataset_lowercase = dataset.apply(lambda x: x.str.lower() if (x.dtype == 'object') else x)

    books['ratings'] = books.apply(lambda x: {}, axis=1)
    books.columns = ["isbn", "title", "author", "publication", "publisher", "cover", "ratings"]
    books = books.fillna("")
    knihy = {str(kwargs.get('isbn')): Book(**kwargs) for kwargs in books.to_dict(orient="records")}

    ratings = pd.read_csv(rating_path, encoding='cp1251', sep=';')
    ratings = ratings[ratings['Book-Rating'] != 0]

    user_ratings = defaultdict(list)

    ratings.apply(lambda row: user_ratings[str(row['User-ID'])].append(str(row['ISBN'])), axis=1)

    ratings.apply(
        lambda row: knihy.get(row['ISBN']) is not None and
                    knihy.get(str(row['ISBN'])).add_rating(row['User-ID'], row['Book-Rating']), axis=1)

    return user_ratings, knihy