from pydantic import BaseModel
from fastapi import Form
from datetime import date


class MissingPersonCase:
    def __init__(
        self,
        full_name: str = Form(...),
        age: int = Form(...),
        gender: str = Form(...),
        last_seen_location: str = Form(...),
        last_seen_date: date = Form(...)
    ):
        self.full_name = full_name
        self.age = age
        self.gender = gender
        self.last_seen_location = last_seen_location
        self.last_seen_date = last_seen_date
