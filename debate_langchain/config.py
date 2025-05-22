from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")

# DB 및 리미터 초기화용 전역 객체
db = SQLAlchemy()
limiter = Limiter(key_func=get_remote_address)

def init_extensions(app):
    CORS(app)
    db.init_app(app)
    limiter.init_app(app)
