from django.urls import path
from .views import *
from django.contrib.auth.views import *
from .views import *
##CHANGE IT UP - IMPORTANT TO HAVE REFERENCES FOR URLS.

app_name = "general"
urlpatterns = [
    #general urls
    path('', home_view, name='home'),
]