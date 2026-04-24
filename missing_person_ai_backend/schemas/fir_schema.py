from pydantic import BaseModel

class FIRCreateSchema(BaseModel):
    person_id: int
    priority: str = "HIGH"
