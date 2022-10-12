from django.shortcuts import HttpResponse, render

# Create your views here.
def home_view(request):

    return render(request, "general/home.html")