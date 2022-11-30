from django.conf import settings
from django.db import connection, reset_queries
import time
#DEBUG must be true for this to work. Be sure to set DEBUG = True at the bottom of settings.py to enable this
last_timestamp = time.time()

def reset_query_count():
    global last_timestamp
    reset_queries()
    last_timestamp = time.time()

def server_print(string):
    print(string)

def get_query_count(message, reset=True):
    global last_timestamp
    if settings.DEBUG:
        seconds_since_last = time.time() - last_timestamp
        string = str(round(seconds_since_last * 1000)) + "ms\t" + message + ": " + str(len(connection.queries)) + "\n"
        server_print(string)
        
        if reset:
            reset_queries()
            last_timestamp = time.time()