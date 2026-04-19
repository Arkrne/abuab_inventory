import os
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from dotenv import load_dotenv


load_dotenv()

# Configuration
SECRET_KEY = os.getenv("ABUAB_SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("ABUAB_SECRET_KEY is not set. Configure it before starting the app.")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ABUAB_ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

# We use Argon2 to avoid the 72-byte Bcrypt bug on Windows
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password.strip())

def verify_password(plain_password, hashed_password):
    try:
        return pwd_context.verify(plain_password.strip(), hashed_password)
    except Exception:
        return False

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)