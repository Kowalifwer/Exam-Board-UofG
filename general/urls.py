from django.urls import path
from general.views import home_view

app_name = "general"
urlpatterns = [
    # general urls
    path('', home_view, name='home'),
]
