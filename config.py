import os

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

API_USAGE_FILE = "./data/api_usage.csv"

GOOGLE_CLIENT_ID = "729149519506-3qugjikben2j8ato3um5714rcjgknbrv.apps.googleusercontent.com"

REDIRECT_URI = "http://localhost/redirect"

HOST = "0.0.0.0"
PORT = 80
DEBUG = False