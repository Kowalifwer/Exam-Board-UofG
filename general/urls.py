from django.urls import path
from general.views import home_view, test_queries_view, test_queries_2_view, test_queries_3_view, test_queries_4_view, login_view, logout_view, global_search_view, student_view, course_view, all_students_view, all_courses_view, degree_classification_view

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
    
    path('courses/all/', all_courses_view, name='all_courses'),
    path('courses/<str:code>/<int:year>/', course_view, name='course'),

    path('degree_classification/<int:year>/', degree_classification_view, name='degree_classification')
]
