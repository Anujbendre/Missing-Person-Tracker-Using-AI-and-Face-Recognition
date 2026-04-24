from jose import jwt
from config import JWT_SECRET_KEY, JWT_ALGORITHM

def decode_token(token: str):
    return jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])