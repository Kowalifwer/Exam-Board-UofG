from django.test import TestCase
from django.test import Client
from django.urls import reverse
from populate import unit_test as populate_for_tests
from general.models import Student, Course, User, AcademicYear
from django.contrib.messages import get_messages
import warnings
import json
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.alert import Alert
from time import sleep
from django.test import tag

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
            super().setUp()
            self.client = Client()
            #by default, our http client will be logged in.
            if "no_login" not in kwargs:
                self.client.force_login(User.objects.first())

        @classmethod
        def setUpTestData(cls):
            super().setUpTestData()
            populate_for_tests(**kwargs)
      
    return BaseTestCase

class MySeleniumTests(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        populate_for_tests()
        cls.selenium = WebDriver()
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        sleep(1)
        cls.selenium.quit()
        super().tearDownClass()
    
    @tag('selenium')
    def test_login(self):
        self.selenium.get('%s%s' % (self.live_server_url, reverse('general:home')))
        with self.subTest("login"):
            self.selenium.find_element(By.ID, 'login').click()
            self.assertEqual(self.selenium.current_url, self.live_server_url + reverse('general:home'))
            assert 'Logout' in self.selenium.page_source
        
        with self.subTest("student page"):
            sleep(1)
            self.selenium.get('%s%s' % (self.live_server_url, reverse('general:student', kwargs={'GUID': Student.objects.first().GUID})))
            #input area with id 'comment_input', type in a comment and submit button id 'add_comment_button'
            self.selenium.find_element(By.ID, 'comment_input').send_keys("This is a test comment.")
            self.selenium.find_element(By.ID, 'add_comment_button').click()
            sleep(2)
            #inside .tabulator-table, find the first .tabulator-row and click on it
            self.selenium.find_element(By.CSS_SELECTOR, '.tabulator-table .tabulator-row').click()
            sleep(2)
            #click id delete_comments_button
            self.selenium.find_element(By.ID, 'delete_comments_button').click()
            sleep(1)
            Alert(self.selenium).accept()
        
        with self.subTest("logout"):
            sleep(1)
            self.selenium.find_element(By.ID, 'logout').click()
            assert 'Login' in self.selenium.page_source
        

# Create your tests here.
class UnitTestHomeView(BaseViewTestCaseWithDBPopulate()):
    def test_home_view(self):
        # client = Client()
        response = self.client.get(reverse('general:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'general/home.html')

class IntegrationAllStudentsView(BaseViewTestCaseWithDBPopulate()):
    def test_integration_all_students(self):
        with self.subTest("Test all students view loads"):
            response = self.client.get(reverse('general:all_students'))
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, 'general/all_students.html')
        
        with self.subTest("Test all students view table loads"):
            response = self.client.get(reverse('general:all_students'), {'fetch_table_data': True})
            self.assertEqual(response.status_code, 200)
            #check response is json
            self.assertEqual(response['Content-Type'], 'application/json')

class IntegrationTestIndividualStudentView(BaseViewTestCaseWithDBPopulate()):
    def test_integration_student(self):
        random_student = Student.objects.order_by('?').first()
        if not random_student:
            raise Exception("No students in test database. Please ensure test populators generate sufficient data for testing views.")
        
        with self.subTest("Test student view with valid GUID"):
            url = reverse('general:student', kwargs={'GUID': random_student.GUID})
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, 'general/student.html')
        
        with self.subTest("Test student view with invalid GUID"):
            url = reverse('general:student', kwargs={'GUID': "anything"})
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertHasErrorMessage(response)
            self.assertTemplateUsed(response, 'general/student.html')
        
        ##student view TABLE -> all courses
        with self.subTest("Test student view table loads"):
            response = self.client.get(reverse('general:student', kwargs={'GUID': random_student.GUID}), {'fetch_table_data': True})
            self.assertEqual(response.status_code, 200)
            #check response is json
            self.assertEqual(response['Content-Type'], 'application/json')
        
        #TODO: API TESTS - test the api call, get the data, make sure it matches the database (at least the number of courses, the course codes)

class UnitTestIndividualStudentView(BaseViewTestCase):
    pass
    ## Test also for invalid GUID (student does not exist)

    ## Test also for no GUID param in URL

    ## API TESTS BELOW -> TODO: all courses table (ensure it loads correctly)
    ##api call the table, get the data, make sure it matches the database (at least the number of courses, the course codes)

class IntegrationTestAllCoursesView(BaseViewTestCaseWithDBPopulate(years=2)):
    #this test should pass, since if no year is provided, system should fallback to current year
    def test_integration_all_courses(self):

        with self.subTest("All courses view, with no year provided (should fallback to current year)"):
            response = self.client.get(reverse('general:all_courses'))
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, 'general/all_courses.html')

        with self.subTest("All courses view, with exact year provided"):
            response = self.client.get(reverse('general:all_courses_exact', kwargs={'year': 2021}))
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, 'general/all_courses.html')

        with self.subTest("Test all courses view table loads"):
            response = self.client.get(reverse('general:all_courses'), {'fetch_table_data': True})
            self.assertEqual(response.status_code, 200)
            #check response is json
            self.assertEqual(response['Content-Type'], 'application/json')

class IntegrationTestIndividualCourseView(BaseViewTestCaseWithDBPopulate(years=2)):
    def test_integration_course(self):
        random_course = Course.objects.order_by('?').first()
        if not random_course:
            raise Exception("No courses in test database. Please ensure test populators generate sufficient data for testing views.")
        
        with self.subTest("Test course view table loads"):
            response = self.client.get(reverse('general:course', kwargs={'code': random_course.code, 'year': random_course.academic_year}), {'fetch_table_data': True})
            self.assertEqual(response.status_code, 200)
            #check response is json
            self.assertEqual(response['Content-Type'], 'application/json')
        
        #TODO-> shoot apis to other urls ?

class UnitTestIndividualCourseView(BaseViewTestCase):
    def setUp(self):
        Course.objects.create(code="TEST", academic_year=2022, credits=3)
        Course.objects.create(code="TEST", academic_year=2021, credits=3)

    def test_valid_course_view(self):
        url = reverse('general:course', kwargs={'code': "TEST", 'year': 2022})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'general/course.html')
        
    def test_valid_course_view_previous_year(self):
        url = reverse('general:course', kwargs={'code': "TEST", 'year': 2021})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'general/course.html')

    def test_individual_course_view_invalid_year_provided(self):
        url = reverse('general:course', kwargs={'code': "anything", 'year': 2022})
        response = self.client.get(url)
        self.assertHasErrorMessage(response)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'general/course.html')

    def test_individual_course_view_invalid_course_code_provided(self):
        url = reverse('general:course', kwargs={'code': "anything", 'year': 2021})
        response = self.client.get(url)
        self.assertHasErrorMessage(response)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'general/course.html')

class LevelProgressionViewTests(BaseViewTestCaseWithDBPopulate()):
    def test_level_progression_view(self):
        response = self.client.get(reverse('general:level_progression', kwargs={'level': 4}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'general/level_progression.html')

class LevelProgressionIntegrationTests(BaseViewTestCaseWithDBPopulate(levels=[1, 2, 3, 4], students=50, credits=60)):
    def test_integration_level_progression_tables(self):
        with self.subTest("Test level 1 table"):
            response = self.client.get(reverse('general:level_progression', kwargs={'level': 1}), {'fetch_table_data': True})
            self.assertEqual(response.status_code, 200)
            #check response is json
            self.assertEqual(response['Content-Type'], 'application/json')
        with self.subTest("Test level 2 table"): #
            response = self.client.get(reverse('general:level_progression', kwargs={'level': 2}), {'fetch_table_data': True})
            self.assertEqual(response.status_code, 200)
            #check response is json
            self.assertEqual(response['Content-Type'], 'application/json')
        with self.subTest("Test level 3 table"): #
            response = self.client.get(reverse('general:level_progression', kwargs={'level': 3}), {'fetch_table_data': True})
            self.assertEqual(response.status_code, 200)
            #check response is json
            self.assertEqual(response['Content-Type'], 'application/json')
        with self.subTest("Test level 4 table"): #
            response = self.client.get(reverse('general:level_progression', kwargs={'level': 4}), {'fetch_table_data': True})
            self.assertEqual(response.status_code, 200)
            #check response is json
            self.assertEqual(response['Content-Type'], 'application/json')
        

class DegreeClassificationUnitTests(BaseViewTestCase):
    def setUp(self):
        academic_year = AcademicYear.objects.filter(is_current=True).first()
        if not academic_year:
            academic_year = AcademicYear.objects.create(year=2022, is_current=True)

    def test_degree_classification_bachelors(self):
        response = self.client.get(reverse('general:degree_classification', kwargs={'level': 4}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'general/degree_classification.html')
    
    def test_degree_classification_masters(self):
        response = self.client.get(reverse('general:degree_classification', kwargs={'level': 5}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'general/degree_classification.html')

class DegreeClassificationIntegrationTests(BaseViewTestCaseWithDBPopulate(levels=[3,4,5], years=3, students=250, credits=80)):
    def test_integration_degree_classification_tables(self):
        ##TODO: check the table data
        with self.subTest("Test degree classification table Bachelors"): #
            response = self.client.get(reverse('general:degree_classification', kwargs={'level': 4}), {'fetch_table_data': True})
            self.assertEqual(response.status_code, 200)
            if response.content == b'[]':
                warnings.warn("No students fetched for degree classification bachelors cohort table -> meaning this view is not recieving full coverage. Please tweak the population data parameters to ensure this view is covered and tested.")
                
            #check response is json
            self.assertEqual(response['Content-Type'], 'application/json')
        with self.subTest("Test degree classification table Masters"):
            response = self.client.get(reverse('general:degree_classification', kwargs={'level': 5}), {'fetch_table_data': True})
            #check if response content is empty list
            if response.content == b'[]':
                warnings.warn("No students fetched for degree classification masters cohort table -> meaning this view is not recieving full coverage. Please tweak the population data parameters to ensure this view is covered and tested.")
                
            self.assertEqual(response.status_code, 200)
            #check response is json
            self.assertEqual(response['Content-Type'], 'application/json')

class GlobalSearchViewIntegrationTests(BaseViewTestCaseWithDBPopulate(students=10)):
    def test_integration(self):
        random_student = Student.objects.order_by('?').first()
        random_course = Course.objects.order_by('?').first()
        if not random_student or not random_course:
            raise Exception("No students or courses found in test database. Please populate the database with students and courses before running this test.")

        with self.subTest("Global search with search term -> expected to contain search term"):
            response = self.client.post(reverse('general:global_search'), {'global_search': 'test'})
            self.assertIn('search_term', response.context)
            self.assertEqual(response.context['search_term'], 'test')
        
        with self.subTest("Global search with search term -> expected to return no results"):
            response = self.client.post(reverse('general:global_search'), {'global_search': 'aw0d9u1n3c092u3n9203ur029cru3n'})
            self.assertIsNone(response.context['course_data'])
            self.assertIsNone(response.context['student_data'])

        with self.subTest("Global search with search term -> expected to return student table"):
            response = self.client.post(reverse('general:global_search'), {'global_search': random_student.full_name})
            #check response search term is correct
            self.assertEqual(response.context['search_term'], random_student.full_name)
            #check response has 'student_data'
            self.assertIn('student_data', response.context)
            self.assertGreater(len(json.loads(response.context['student_data'])), 0)
        
        with self.subTest("Global search with search term -> expected to return course table"):
            response = self.client.post(reverse('general:global_search'), {'global_search': random_course.code})
            #check response search term is correct
            self.assertEqual(response.context['search_term'], random_course.code)
            #check response has 'course_data'
            self.assertIn('course_data', response.context)
            self.assertGreater(len(json.loads(response.context['course_data'])), 0)

        with self.subTest("Global search with no search term"): #
            response = self.client.get(reverse('general:global_search'))
            self.assertEqual(response.status_code, 200)
            self.assertNotIn('search_term', response.context)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'general/global_search.html')
    
    #API TEST -> get a random course, search for it (table api), check the response is json, check the response contains the course code
    #do the same for random student

class LevelProgressionRulesViewTests(BaseViewTestCaseWithDBPopulate()):
    def test_level_progression_rules_view(self):
        response = self.client.get(reverse('general:level_progression_rules', kwargs={'level': 4}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'general/level_progression_rules.html')

class DegreeClassificationRulesViewTests(BaseViewTestCaseWithDBPopulate()):
    def test_degree_classification_rules_view(self):
        response = self.client.get(reverse('general:degree_classification_rules'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'general/degree_classification_rules.html')


class TableApiIntegrationTests(BaseViewTestCaseWithDBPopulate()):
    
    def test_table_api(self):
        random_course = Course.objects.order_by('?').first()
        random_student = Student.objects.order_by('?').first()
        if not random_course or not random_student:
            raise Exception("No students or courses found in test database. Please populate the database with students and courses before running this test.")

        with self.subTest("Test table api -> assessment moderation table"):
            response = self.client.get(reverse('general:api_table', kwargs={'table_name': 'assessment_moderation'}), {'assessments': True, 'course_id': random_course.id})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response['Content-Type'], 'application/json')
        
        with self.subTest("Test table api -> student-course-assessments table"):
            response = self.client.get(reverse('general:api_table', kwargs={'table_name': 'course_assessments'}), {'course_id': random_course.id, 'student_GUID': random_student.GUID})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response['Content-Type'], 'application/json')

class GeneralApiIntegrationTests(BaseViewTestCaseWithDBPopulate(years=2, students=50, levels=[1,2,3], credits=60)):
    #TODO: consider testing this with Selenium!!
    def test_api(self):
        random_course = Course.objects.order_by('?').first()
        random_student = Student.objects.order_by('?').first()
        current_year = AcademicYear.objects.get(is_current=True)
        if not random_course or not random_student:
            raise Exception("No students or courses found in test database. Please populate the database with students and courses before running this test.")

        #---- POST REQUESTS ----
        with self.subTest("Test general api -> Moderation -> increase 1 bands"):
            response = self.client.post(reverse('general:api', kwargs={'action': 'moderation'}), {'student_GUID': random_student.GUID, 'data': json.dumps({
                'mode': 'increase',
                'value': 1,
                'course_id': str(random_course.id),
                'assessment_ids': [str(id) for id in list(random_course.assessments.all().values_list('id', flat=True))]
            })})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response['Content-Type'], 'application/json')
        
        with self.subTest("Test general api -> Moderation -> decrease 2 bands"):
            response = self.client.post(reverse('general:api', kwargs={'action': 'moderation'}), {'student_GUID': random_student.GUID, 'data': json.dumps({
                'mode': 'decrease',
                'value': 2,
                'course_id': str(random_course.id),
                'assessment_ids': [str(id) for id in list(random_course.assessments.all().values_list('id', flat=True))]
            })})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response['Content-Type'], 'application/json')
        
        with self.subTest("Test general api -> Moderation -> remove"):
            response = self.client.post(reverse('general:api', kwargs={'action': 'moderation'}), {'student_GUID': random_student.GUID, 'data': json.dumps({
                'mode': 'remove',
                'value': 1,
                'course_id': str(random_course.id),
                'assessment_ids': [str(id) for id in list(random_course.assessments.all().values_list('id', flat=True))]
            })})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response['Content-Type'], 'application/json')
        
        with self.subTest("Test general api -> Moderation -> invalid mode"):
            response = self.client.post(reverse('general:api', kwargs={'action': 'moderation'}), {'student_GUID': random_student.GUID, 'data': json.dumps({
                'mode': 'improve',
                'value': 1,
                'course_id': str(random_course.id),
                'assessment_ids': [str(id) for id in list(random_course.assessments.all().values_list('id', flat=True))]
            })})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response['Content-Type'], 'application/json')
        
        with self.subTest("Test general api -> Moderation -> missing parameters"):
            response = self.client.post(reverse('general:api', kwargs={'action': 'moderation'}), {'student_GUID': random_student.GUID, 'data': json.dumps({
                'mode': 'increase',
                'value': 1,
                # 'course_id': str(random_course.id), missing
                'assessment_ids': [str(id) for id in list(random_course.assessments.all().values_list('id', flat=True))]
            })})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response['Content-Type'], 'application/json')
        
        with self.subTest("Test general api -> save_grading_rules -> degree rules"):
            response = self.client.post(reverse('general:api', kwargs={'action': 'save_grading_rules'}),
                {'course_id': str(random_course.id),
                 'year_id': str(current_year.id)
                 })
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response['Content-Type'], 'application/json')
        
        with self.subTest("Test general api -> save_grading_rules -> level rules"):
            response = self.client.post(reverse('general:api', kwargs={'action': 'save_grading_rules'}),
                {'course_id': str(random_course.id),
                 'level': 4,
                 'year_id': str(current_year.id)
                 })
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response['Content-Type'], 'application/json')
        
        with self.subTest("Test general api -> update_preponderance"):
            response = self.client.post(reverse('general:api', kwargs={'action': 'update_preponderance'}), {'course_id': str(random_course.id), "data": json.dumps([
                {'result_id': str(result.id), 'preponderance': 'MV'} for result in random_course.results.all()
            ])})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response['Content-Type'], 'application/json')
        
        with self.subTest("Test general api -> add_comment -> student"):
            response = self.client.post(reverse('general:api', kwargs={'action': "add_comment"}), {'student_id': str(random_student.id), "data": json.dumps("Hello there!")})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response['Content-Type'], 'application/json')
        
        with self.subTest("Test general api -> add_comment -> course"):
            response = self.client.post(reverse('general:api', kwargs={'action': "add_comment"}), {'course_id': str(random_course.id), "data": json.dumps("Hello there!")})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response['Content-Type'], 'application/json')
        
        with self.subTest("Test general api -> delete_comment -> student"):
            response = self.client.post(reverse('general:api', kwargs={'action': "delete_comments"}), {'course_id': random_course.id, "data" : json.dumps([
                str(comment.id) for comment in random_student.comments.all()
            ])})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response['Content-Type'], 'application/json')
        
        with self.subTest("Test general api -> delete_comment -> course"):
            response = self.client.post(reverse('general:api', kwargs={'action': "delete_comments"}), {'student_id': random_student.id, "data" : json.dumps([
                str(comment.id) for comment in random_course.comments.all()
            ])})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response['Content-Type'], 'application/json')
        
        #----GET REQUESTS----
        with self.subTest("Test general api -> get request"):
            response = self.client.get(reverse('general:api', kwargs={'action': "test_get"}), {'student_id': random_student.id})
            self.assertEqual(response['Content-Type'], 'application/json')
        
        #---OTHER REQUESTS---
        with self.subTest("Test general api -> delete_comment -> course"):
            response = self.client.put(reverse('general:api', kwargs={'action': "test_put"}), {})
            #check that "Invalid request method" is inside response.status
            self.assertEqual(response.json()['status'], "Invalid request method")
            self.assertEqual(response['Content-Type'], 'application/json')

#TODO: consider selenium tests, to test the actual functionality of the website (e.g. clicking on a course code in the all courses table should take you to the course page)

#https://stackoverflow.com/questions/90002/what-is-a-reasonable-code-coverage-for-unit-tests-and-why
#https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Testing -> types of testing

#Goal of testing -> to rigorously test all the functionality ]

# Code Coverage is a misleading metric if 100% coverage is your goal (instead of 100% testing of all features).

# You could get a 100% by hitting all the lines once. However you could still miss out testing a particular sequence (logical path) in which those lines are hit.
# You could not get a 100% but still have tested all your 80%/freq used code-paths. Having tests that test every 'throw ExceptionTypeX' or similar defensive programming guard you've put in is a 'nice to have' not a 'must have'

#Basically, say that I aimed to rigorously test every feature of the website, so the logic was to test some of the models, all of the views etc..
#This naturally also brought the code coverage to over 90%

# I write my tests to exercise all the functionality and edge cases I can think of (usually working from the documentation).
# I run the code coverage tools
# I examine any lines or paths not covered and any that I consider not important or unreachable (due to defensive programming) I mark as not counting
# I write new tests to cover the missing lines and improve the documentation if those edge cases are not mentioned.