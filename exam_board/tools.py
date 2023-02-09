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
                "short_name": "1st",
                "std_low_gpa": 17.5,
                "disc_low_gpa": 17.1,
                "char_band": "A",
                "percentage_above": 50,
            },
            2: {
                "name": "Upper Second Class Honours",
                "short_name": "2:1",
                "std_low_gpa": 14.5,
                "disc_low_gpa": 14.1,
                "char_band": "B",
                "percentage_above": 50,
            },
            3: {
                "name": "Lower Second Class Honours",
                "short_name": "2:2",
                "std_low_gpa": 11.5,
                "disc_low_gpa": 11.1,
                "char_band": "C",
                "percentage_above": 50,
            },
            4: {
                "name": "Third Class Honours",
                "short_name": "3rd",
                "std_low_gpa": 8.5,
                "disc_low_gpa": 8.1,
                "char_band": "D",
                "percentage_above": 50,
            },
            5: {
                "name": "Fail",
                "short_name": "Fail",
                "std_low_gpa": 8.0,
                "disc_low_gpa": 0.0,
                "char_band": "F",
                "percentage_above": 0,
            },
        })

band_integer_to_band_letter_map = {
        0: "H",

        1: "G2",
        2: "G1",

        3: "F3",
        4: "F2",
        5: "F1",

        6: "E3",
        7: "E2",
        8: "E1",

        9: "D3",
        10: "D2",
        11: "D1",

        12: "C3",
        13: "C2",
        14: "C1",
        
        15: "B3",
        16: "B2",
        17: "B1",
 
        18: "A5",
        19: "A4",
        20: "A3",
        21: "A2",
        22: "A1",
    }

degree_progression_levels = {
    1: "Level 1",
    2: "Level 2",
    3: "Level 3 (Honours)",
    4: "Level 4 (Honours)",
    # 5: "Level 5 (Masters)",
}

degree_classification_levels = {
    4: "BsC/BEng (Hons)",
    5: "MSc/MEng (Hons)",
}

def update_cumulative_band_credit_totals(dict_to_update, credits, course_grade):
    if course_grade >= 18:
        dict_to_update["greater_than_a"] += credits
        dict_to_update["greater_than_b"] += credits
        dict_to_update["greater_than_c"] += credits
        dict_to_update["greater_than_d"] += credits
        dict_to_update["greater_than_e"] += credits
        dict_to_update["greater_than_f"] += credits
        dict_to_update["greater_than_g"] += credits
        dict_to_update["greater_than_h"] += credits
    
    elif course_grade >= 15:
        dict_to_update["greater_than_b"] += credits
        dict_to_update["greater_than_c"] += credits
        dict_to_update["greater_than_d"] += credits
        dict_to_update["greater_than_e"] += credits
        dict_to_update["greater_than_f"] += credits
        dict_to_update["greater_than_g"] += credits
        dict_to_update["greater_than_h"] += credits
    
    elif course_grade >= 12:
        dict_to_update["greater_than_c"] += credits
        dict_to_update["greater_than_d"] += credits
        dict_to_update["greater_than_e"] += credits
        dict_to_update["greater_than_f"] += credits
        dict_to_update["greater_than_g"] += credits
        dict_to_update["greater_than_h"] += credits
    
    elif course_grade >= 9:
        dict_to_update["greater_than_d"] += credits
        dict_to_update["greater_than_e"] += credits
        dict_to_update["greater_than_f"] += credits
        dict_to_update["greater_than_g"] += credits
        dict_to_update["greater_than_h"] += credits
    
    elif course_grade >= 6:
        dict_to_update["greater_than_e"] += credits
        dict_to_update["greater_than_f"] += credits
        dict_to_update["greater_than_g"] += credits
        dict_to_update["greater_than_h"] += credits

    if course_grade >= 3:
        dict_to_update["greater_than_f"] += credits
        dict_to_update["greater_than_g"] += credits
        dict_to_update["greater_than_h"] += credits
    
    elif course_grade >= 1:
        dict_to_update["greater_than_g"] += credits
        dict_to_update["greater_than_h"] += credits
    
    elif course_grade >= 0:
        dict_to_update["greater_than_h"] += credits


def gpa_to_class_converter(grade_data, degree_classification_settings):  
    for description in degree_classification_settings.values():#ignore the fail case
        if grade_data["final_gpa"] >= description["std_low_gpa"]:
            return description["short_name"]
        if grade_data["final_gpa"] >= description["disc_low_gpa"]:
            if round((grade_data[f"greater_than_{description['char_band'].lower()}"] / grade_data["n_credits"]) * 100, 0) >= description["percentage_above"]:
                return description["short_name"]
        
    return "Fail"