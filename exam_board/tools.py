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

class default_degree_classification_settings_dict(dict):
    def __init__(self):
        super().__init__({ ## provide the default values for the degree classification settings here.
            1: {
                "name": "First Class Honours",
                "std_low_gpa": 19.0,
                "disc_low_gpa": 18.1,
                "char_band": "A",
                "percentage_above": 50,
            },
            2: {
                "name": "Upper Second Class Honours",
                "std_low_gpa": 15.0,
                "disc_low_gpa": 14.1,
                "char_band": "B",
                "percentage_above": 50,
            },
            3: {
                "name": "Lower Second Class Honours",
                "std_low_gpa": 12.0,
                "disc_low_gpa": 11.1,
                "char_band": "C",
                "percentage_above": 50,
            },
            4: {
                "name": "Third Class Honours",
                "std_low_gpa": 9.0,
                "disc_low_gpa": 8.1,
                "char_band": "D",
                "percentage_above": 50,
            },
            5: {
                "name": "Fail",
                "std_low_gpa": 0.0,
                "disc_low_gpa": 0.0,
                "char_band": "F",
                "percentage_above": 0,
            },
        })