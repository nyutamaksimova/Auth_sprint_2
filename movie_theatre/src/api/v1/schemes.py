from pydantic import BaseModel, ConfigDict

from src.models.genre import Genre
from src.models.person import Person


class Film(BaseModel):
    """Фильм"""
    uuid: str
    title: str
    imdb_rating: float
    description: str
    genre: list[Genre]
    actors: list[Person]
    writers: list[Person]
    directors: list[Person]

    model_config = ConfigDict(from_attributes=True)


class FilmShort(BaseModel):
    """Краткий формат информации о фильме"""
    uuid: str
    title: str
    imdb_rating: float

    model_config = ConfigDict(from_attributes=True)
