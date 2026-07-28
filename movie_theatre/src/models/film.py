from pydantic import BaseModel, ConfigDict

from src.models.genre import Genre
from src.models.person import Person


class Film(BaseModel):
    uuid: str
    title: str
    imdb_rating: float
    description: str
    genre: list[Genre]
    actors: list[Person]
    writers: list[Person]
    directors: list[Person]
