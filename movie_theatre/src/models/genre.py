from pydantic import BaseModel, ConfigDict


class Genre(BaseModel):
    uuid: str
    name: str
