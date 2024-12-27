from dotenv import load_dotenv 
import os 

load_dotenv(os.getcwd()+'/backend/.venv')
DB_NAME = os.environ.get("DB_NAME") 
DB_USER = os.environ.get("DB_USER") 
DB_PASSWORD = os.environ.get("DB_PASSWORD")