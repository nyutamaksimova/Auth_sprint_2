from pydantic import BaseModel, ConfigDict


class Person(BaseModel):
    uuid: str
    full_name: str


