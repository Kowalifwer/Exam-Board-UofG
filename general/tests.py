from django.test import TestCase

# Create your tests here.
class BaseTestCase(TestCase):
    def setUp(self):
        print("do something in the base...")
        super().setUp()
    
    def test_placeholder(self):
        x = 2
        y = 3
        self.assertEqual(x + y, 5)