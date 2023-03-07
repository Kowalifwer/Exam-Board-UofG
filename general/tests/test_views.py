from django.test import TestCase, TransactionTestCase
from django.db import connection, reset_queries
from django.test import Client
from django.urls import reverse
from populate import unit_test as populate_for_tests
from general.models import Student, Course, User
from django.contrib.messages import get_messages

print("RUNNING DJANGO VIEW TESTS")

class BaseViewTestCase(TestCase):

    def assertHasErrorMessage(self, response):
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(len(messages) > 0)
        has_error = False
        for message in messages:
            if message.tags == "error":
                has_error = True
                break
        if not has_error:
            self.fail("No error messages found in response.")

def BaseViewTestCaseWithDBPopulate(**kwargs):
    kwargs["students"] = kwargs.get("students", 5)
    class BaseTestCase(BaseViewTestCase):
        def setUp(self):
            super().setUp() #wipes the db, sets to empty.
            populate_for_tests(**kwargs)
      
    return BaseTestCase

# Create your tests here.
class TestHomeView(BaseViewTestCaseWithDBPopulate()):
    def test_home_view(self):
        #setup is ran here. ALWAYS. (wipes db, allows u to populate.)
        client = Client()
        response = client.get(reverse('general:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'general/home.html')

class TestAllStudentsView(BaseViewTestCaseWithDBPopulate()):
    def test_all_students_view(self):
        client = Client()
        response = client.get(reverse('general:all_students'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'general/all_students.html')

class TestIndividualStudentView(BaseViewTestCaseWithDBPopulate()):
    def test_individual_student_view(self):
        random_student = Student.objects.order_by('?').first()
        if not random_student:
            raise Exception("No students in test database. Please ensure test populators generate sufficient data for testing views.")
        
        client = Client()
        url_to_test = reverse('general:student', kwargs={'GUID': random_student.GUID})

        response = client.get(url_to_test)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'general/student.html')
    
    ## Test also for invalid GUID (student does not exist)

    ## Test also for no GUID param in URL

    ## API TESTS BELOW -> TODO: all courses table (ensure it loads correctly)
    ##api call the table, get the data, make sure it matches the database (at least the number of courses, the course codes)

class TestAllCoursesView(BaseViewTestCaseWithDBPopulate(years=2)):
    #this test should pass, since if no year is provided, system should fallback to current year
    def test_all_courses_view_no_year_provided(self):
        client = Client()
        response = client.get(reverse('general:all_courses'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'general/all_courses.html')
    
    def test_all_courses_view_exact_year_provided(self):
        client = Client()
        response = client.get(reverse('general:all_courses_exact', kwargs={'year': 2021}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'general/all_courses.html')

class IntegrationTestIndividualCourseView(BaseViewTestCaseWithDBPopulate(years=2)):
    def test_integration_course(self):
        client = Client()
        with self.subTest("Test course view with valid year and course code"):
            random_course = Course.objects.order_by('?').first()
            if not random_course:
                raise Exception("No courses in test database. Please ensure test populators generate sufficient data for testing views.")

            url = reverse('general:course', kwargs={'code': random_course.code, 'year': random_course.academic_year})
            response = client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, 'general/course.html')
        
        with self.subTest("Test course view with previous year and course code"):
            previous_year_course = Course.objects.filter(code=random_course.code, academic_year=random_course.academic_year - 1).first()
            if not previous_year_course:
                previous_year_course = Course.objects.create(code=random_course.code, academic_year=random_course.academic_year - 1, credits=random_course.credits)

            url = reverse('general:course', kwargs={'code': previous_year_course.code, 'year': previous_year_course.academic_year})
            response = client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, 'general/course.html')

class UnitTestIndividualCourseViewInvalid(BaseViewTestCase):
    def setUp(self):
        Course.objects.create(code="TEST", academic_year=2022, credits=20)

    def test_individual_course_view_invalid_year_provided(self):
        client = Client()
        url = reverse('general:course', kwargs={'code': "anything", 'year': 2022})
        response = client.get(url)
        self.assertHasErrorMessage(response)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'general/course.html')

    def test_individual_course_view_invalid_course_code_provided(self):
        client = Client()
        url = reverse('general:course', kwargs={'code': "anything", 'year': 2021})
        response = client.get(url)
        self.assertHasErrorMessage(response)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'general/course.html')

class IntegrationTestIndividualStudentView(BaseViewTestCaseWithDBPopulate()):
    def test_integration_student(self):
        client = Client()
        with self.subTest("Test student view with valid GUID"):
            random_student = Student.objects.order_by('?').first()
            if not random_student:
                raise Exception("No students in test database. Please ensure test populators generate sufficient data for testing views.")

            url = reverse('general:student', kwargs={'GUID': random_student.GUID})
            response = client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, 'general/student.html')
        
        with self.subTest("Test student view with invalid GUID"):
            url = reverse('general:student', kwargs={'GUID': "anything"})
            response = client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertHasErrorMessage(response)
            self.assertTemplateUsed(response, 'general/student.html')
        
        #TODO: API TESTS - test the api call, get the data, make sure it matches the database (at least the number of courses, the course codes)

class LevelProgressionViewTests(BaseViewTestCaseWithDBPopulate()):
    def test_level_progression_view(self):
        client = Client()
        response = client.get(reverse('general:level_progression', kwargs={'level': 4}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'general/level_progression.html')

class DegreeClassificationViewTests(BaseViewTestCaseWithDBPopulate()):
    def test_degree_classification_view(self):
        client = Client()
        response = client.get(reverse('general:degree_classification', kwargs={'level': 4}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'general/degree_classification.html')

class GlobalSearchViewTests(BaseViewTestCaseWithDBPopulate()):
    def test_global_search_view(self):
        #going to the URL as a get request should return empty context
        client = Client()
        response = client.get(reverse('general:global_search'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'general/global_search.html')
        self.assertNotIn('search_term', response.context)
    
    def test_global_search_view_with_search_term(self):
        #going to the URL as a get request should return empty context
        client = Client()
        response = client.post(reverse('general:global_search'), {'global_search': 'test'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'general/global_search.html')
        self.assertIn('search_term', response.context)
        self.assertEqual(response.context['search_term'], 'test')
    
    #API TEST -> if student table has correct n of rows, then the api call should return the same n of rows

class LevelProgressionRulesViewTests(BaseViewTestCaseWithDBPopulate()):
    def test_level_progression_rules_view(self):
        client = Client()
        response = client.get(reverse('general:level_progression_rules'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'general/level_progression_rules.html')

class DegreeClassificationRulesViewTests(BaseViewTestCaseWithDBPopulate()):
    def test_degree_classification_rules_view(self):
        client = Client()
        response = client.get(reverse('general:degree_classification_rules'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'general/degree_classification_rules.html')


#TODO: consider selenium tests, to test the actual functionality of the website (e.g. clicking on a course code in the all courses table should take you to the course page)
