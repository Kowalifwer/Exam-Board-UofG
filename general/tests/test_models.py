from django.test import TestCase
from django.db import connection, reset_queries
from general.models import AcademicYear, User, Student
import json

# Create your tests here.
print("RUNNING DJANGO MODELS TESTS")

class AcademicYearTest(TestCase):
    def create_year(self):
        return AcademicYear.objects.create(year=2023, is_current=False)

    def test_degree_classification(self):
        w = self.create_year()
        self.assertTrue(isinstance(w.degree_classification_settings, list))
        self.assertTrue(isinstance(w.degree_classification_settings_for_table, str))
    
    def test_level_progression(self):
        w = self.create_year()
        self.assertTrue(isinstance(w.level_progression_settings, dict))
        self.assertTrue(isinstance(w.level_progression_settings["1"], list))

        self.assertTrue(isinstance(w.level_progression_settings_for_table("1"), str))
    
    def test_str(self):
        w = self.create_year()
        self.assertEqual(str(w), "2023")

class UserTest(TestCase):
    def create_user(self):
        return User.objects.create(username="test", email="test@gmail.com", password="test", first_name="test", last_name="test", title="dr")

    def test_get_name_verbose(self):
        w = self.create_user()
        self.assertEqual(w.get_name_verbose, "Dr. test test")
    
    def test_str(self):
        w = self.create_user()
        self.assertEqual(str(w), "test test")

#TODO -> Tests here that check linked stuff, eg. if a student is deleted, or a course etc..

