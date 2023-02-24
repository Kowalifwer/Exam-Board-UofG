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

def default_degree_classification_settings():
    return [
        {
            "name": "First Class Honours",
            "short_name": "1st",
            "std_low_gpa": 17.5,
            "disc_low_gpa": 17.1,
            "char_band": "A",
            "percentage_above": 50,
        },
        {
            "name": "Upper Second Class Honours",
            "short_name": "2:1",
            "std_low_gpa": 14.5,
            "disc_low_gpa": 14.1,
            "char_band": "B",
            "percentage_above": 50,
        },
        {
            "name": "Lower Second Class Honours",
            "short_name": "2:2",
            "std_low_gpa": 11.5,
            "disc_low_gpa": 11.1,
            "char_band": "C",
            "percentage_above": 50,
        },
        {
            "name": "Third Class Honours",
            "short_name": "3rd",
            "std_low_gpa": 8.5,
            "disc_low_gpa": 8.1,
            "char_band": "D",
            "percentage_above": 50,
        }
    ]

def default_level_progression_settings():
    return {   
        #guaranteed with minimum 15 GPA across all lvl 1 computing science courses,
        #discretionary with minimum 12 GPA across all lvl 1 computing science courses
        "1": [
            {
                "name": "Guaranteed progression into level 2",
                "short_name": "yes",
                "above": 15.0, ##B3 is level 1 to level 2 pass
            },
            {
                "name": "Discretionary progression into level 2",
                "short_name": "discretionary",
                "above": 12.0, ##C3 is level 1 to level 2 discretionary
            },
        ],
        #grade point average of 12.0 over 60 credits of level 2 computing science courses, at first attempt
        "2": [
            {
                "name": "Guaranteed progression into level 3",
                "short_name": "yes",
                "above": 12.0, ##C3 is level 2 to level 3 pass
                "n_credits": 60,
            },
            {
                "name": "Discretionary progression into level 3",
                "short_name": "discretionary",
                "above": 9.0, ##D3 is level 2 to level 3 discretionary
                "n_credits": 60,
            }
        ],
        # GPA of 9.0 in level 3 for BSC and 12.0 for MSC. BSC below -> switch degree, MSC below -> switch to BSC.
        "3": [
            {
                "name": "Guaranteed progression into level 4",
                "short_name": "yes",
                "above": 12.0, ##D3 is level 3 to level 4 pass
            },
            {
                "name": "Discretionary progression into level 4",
                "short_name": "discretionary",
                "above": 9.0, ##E3 is level 3 to level 4 discretionary
            }
        ],
        #minimum E3 in every course, 9.0 GPA across all courses
        "4": [
            {
                "name": "Guaranteed progression into level 5",
                "short_name": "yes",
                "above": 12.0, ##D3 is level 4 to level 5 pass
            },
            {
                "name": "Discretionary progression into level 5",
                "short_name": "discretionary",
                "above": 9.0, ##E3 is level 4 to level 5 discretionary
            }
        ],
    }

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
    3: "Level 3 (Hons)",
    4: "Level 4 (Hons)",
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

    elif course_grade >= 3:
        dict_to_update["greater_than_f"] += credits
        dict_to_update["greater_than_g"] += credits
        dict_to_update["greater_than_h"] += credits
    
    elif course_grade >= 1:
        dict_to_update["greater_than_g"] += credits
        dict_to_update["greater_than_h"] += credits
    
    elif course_grade >= 0:
        dict_to_update["greater_than_h"] += credits


def gpa_to_class_converter(grade_data, degree_classification_settings):  
    for description in degree_classification_settings:#ignore the fail case
        if grade_data["final_gpa"] >= description["std_low_gpa"]:
            return description["short_name"]
        if grade_data["final_gpa"] >= description["disc_low_gpa"]:
            if round((grade_data[f"greater_than_{description['char_band'].lower()}"] / grade_data["n_credits"]) * 100, 0) >= description["percentage_above"]:
                return description["short_name"]
        
    return "Fail"

def gpa_to_progression_converter(final_gpa, degree_progression_settings):
    for description in degree_progression_settings:
        if final_gpa >= description["above"]:
            return description["short_name"]
        
    return "no"