from django.test import TestCase
from general.models import AcademicYear, User, Student

# Create your tests here.
print("RUNNING DJANGO MODELS TESTS")
class BaseModelTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        AcademicYear.objects.create(year=2022, is_current=True)

class AcademicYearTest(BaseModelTestCase):
    current_year = AcademicYear.objects.get(is_current=True)
    def test_degree_classification(self):
        self.assertTrue(isinstance(self.current_year.degree_classification_settings, list))
        self.assertTrue(isinstance(self.current_year.degree_classification_settings_for_table, str))
    
    def test_level_progression(self):
        self.assertTrue(isinstance(self.current_year.level_progression_settings, dict))
        self.assertTrue(isinstance(self.current_year.level_progression_settings["1"], list))

        self.assertTrue(isinstance(self.current_year.level_progression_settings_for_table("1"), str))
    
    def test_str(self):
        self.assertEqual(str(self.current_year), "2022")

class UserTest(BaseModelTestCase):
    def create_user(self):
        return User.objects.create(username="test", email="test@gmail.com", password="test", first_name="test", last_name="test", title="dr")

    def test_get_name_verbose(self):
        w = self.create_user()
        self.assertEqual(w.get_name_verbose, "Dr. test test")
    
    def test_str(self):
        w = self.create_user()
        self.assertEqual(str(w), "test test")

class StudentTest(BaseModelTestCase):
    def test_graduation_info_graduated(self):
        student = Student.objects.create(GUID="2312329h", full_name="Test testovich", start_academic_year=2020, end_academic_year=2021, current_level=2)
        self.assertTrue(isinstance(student.graduation_info, str))

    def test_graduation_info_graduating_now(self):
        student = Student.objects.create(GUID="2312339B", full_name="Test testovich", start_academic_year=2020, end_academic_year=2022, current_level=2)
        self.assertTrue(isinstance(student.graduation_info, str))

    def test_graduation_info_graduating_later(self):
        student = Student.objects.create(GUID="2312329K", full_name="Test testovich", start_academic_year=2020, end_academic_year=2024, current_level=2)
        self.assertTrue(isinstance(student.graduation_info, str))


#TODO -> Tests here that check linked stuff, eg. if a student is deleted, or a course etc..

