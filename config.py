import os
from dotenv import load_dotenv

load_dotenv()

IMAP = os.getenv('IMAP')
LOGIN = os.getenv('LOGIN')
PASSWORD = os.getenv('PASSWORD')
