from dataclasses import dataclass
from typing import Dict

url = str


@dataclass
class Book:
    isbn: str
    title: str
    author: str
    publication: int
    publisher: str
    cover: url
    ratings: Dict[str, float]

    def add_rating(self, user_id: str, rating: float) -> None:
        self.ratings[user_id] = rating

    def avg_rating(self) -> float:
        if not self.ratings:
            return -1
        avg = "{:.2f}".format(sum(self.ratings.values()) / len(self.ratings))
        return float(avg)

    def num_of_ratings(self):
        return len(self.ratings)
