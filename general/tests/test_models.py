from django.test import TestCase
from django.db import connection, reset_queries
from general.models import AcademicYear
from exam_board.tools import default_degree_classification_settings_dict
import json

# Create your tests here.
class BaseTestCase(TestCase):
    def setUp(self):
        super().setUp()

    def test_placeholder(self):
        x = 2
        y = 3
        self.assertEqual(x + y, 5)
    

class AcademicYearTest(TestCase):

    def create_year(self):
        return AcademicYear.objects.create(year=2023, is_current=False)

    def test_whatever_creation(self):
        w = self.create_year()
        #assert that degree_classification_settings_for_table() is a valid json
        self.assertTrue(isinstance(w.degree_classification_settings, dict))
        self.assertTrue(isinstance(w.degree_classification_settings_for_table, str))
        self.assertEqual(list(w.degree_classification_settings.values()), json.loads(w.degree_classification_settings_for_table))
    
    def test_str(self):
        w = self.create_year()
        

