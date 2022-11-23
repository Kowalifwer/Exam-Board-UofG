from django.urls import path
from general.views import home_view, test_queries_view, test_queries_2_view, test_queries_3_view, test_queries_4_view

app_name = "general"
urlpatterns = [
    # general urls
    path('', home_view, name='home'),
    path('test_queries/', test_queries_view, name='test_queries'),
    path('test_queries_2/', test_queries_2_view, name='test_queries_2'),
    path('test_queries_3/', test_queries_3_view, name='test_queries_3'),
    path('test_queries_4/', test_queries_4_view, name='test_queries_4'),
]
