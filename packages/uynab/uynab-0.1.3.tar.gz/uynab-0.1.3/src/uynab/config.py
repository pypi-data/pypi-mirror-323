import os


class Config:
    BASE_URL = "https://api.ynab.com/v1"
    API_TOKEN = os.getenv("YNAB_API_TOKEN")
    VERBOSE = False
