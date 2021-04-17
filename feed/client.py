import requests
from .constants import TORRE_OPPORTUNITIES_SEARCH_URL

def makeRequestFor(data):
    return requests.post(TORRE_OPPORTUNITIES_SEARCH_URL, data = {'key':'value'})