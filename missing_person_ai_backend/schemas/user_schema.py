from pydantic import BaseModel, EmailStr

class UserRegisterSchema(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role_id: int
