from django.shortcuts import render
from general.models import Student, Course, Assessment, AssessmentResult, User, AcademicYear
from django.db import connection, reset_queries

# Create your views here.
def home_view(request):
    reset_queries()
    all_students = Student.objects.all()
    all_courses = Course.objects.all().prefetch_related('enrolled_students')
    print(all_students)
    for course in all_courses:
        print(f"Course: {course.name}, has {course.enrolled_students.count()} students")

    print(len(connection.queries))
    return render(request, "general/home.html")

def test_queries_view(request):
    

    return render(request, "general/test_queries.html")
