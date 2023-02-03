from django.urls import path
from general.views import home_view, test_queries_view, test_queries_2_view, test_queries_3_view, test_queries_4_view, login_view, logout_view, global_search_view, student_view, course_view, all_students_view, all_courses_view, degree_classification_view, grading_rules_view, api_view

courses_verbose = 'all_courses'
degree_classification_verbose = 'degree_classification'
grading_rules_verbose = 'grading_rules'

app_name = "general"
urlpatterns = [
    # general urls
    path('', home_view, name='home'),
    path('test_queries/', test_queries_view, name='test_queries'),
    path('test_queries_2/', test_queries_2_view, name='test_queries_2'),
    path('test_queries_3/', test_queries_3_view, name='test_queries_3'),
    path('test_queries_4/', test_queries_4_view, name='test_queries_4'),

    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('global_search/', global_search_view, name='global_search'),

    path('students/all/', all_students_view, name='all_students'),
    path('students/<str:GUID>/', student_view, name='student'),
    
    path('courses/all/', all_courses_view, name=courses_verbose),
    path('courses/all/<int:year>/', all_courses_view, name=courses_verbose+"_exact"),
    path('courses/<str:code>/<int:year>/', course_view, name='course'),

    path('degree_classification/', degree_classification_view, name=degree_classification_verbose),
    path('degree_classification/<int:year>/', degree_classification_view, name=degree_classification_verbose+"_exact"),

    path('grading_rules/', grading_rules_view, name=grading_rules_verbose),
    path('grading_rules/<int:year>/', grading_rules_view, name=grading_rules_verbose+"_exact"),

    path('api/', api_view, name='api'),


    #urls for incomplete views
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
]
