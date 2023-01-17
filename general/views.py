from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from general.models import Student, Course, Assessment, AssessmentResult, User, AcademicYear
from django.db import connection, reset_queries
import time
from django.db.models import Prefetch
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
import json
from exam_board.logging import server_print, get_query_count

def is_fetching_table_data(request):
    return request.method == 'GET' and request.GET.get('fetch_table_data')

# Create your views here.

def test_queries_view(request):
    context = {}
    all_students = Student.objects.all().prefetch_related("courses", "results")
    
    context["students"] = all_students
    # result = HttpResponse("Hello!")
    result = render(request, "general/test_queries.html", context)
    return result

def test_queries_2_view(request):
    context = {}
    # all_courses = Course.objects.all().prefetch_related(
    #     Prefetch(
    #         "results",
    #         queryset=AssessmentResult.objects.filter().select_related("student", "assessment")
    #     ),
    #     Prefetch("assessments"),
    # )
    all_courses = Course.objects.filter(academic_year=2020).prefetch_related("results", "results__student", "results__assessment", "assessments")

    context["courses"] = all_courses
    # result = HttpResponse("Hello!")
    result = render(request, "general/test_queries_2.html", context)
    return result

def test_queries_3_view(request):  # This view fetches all Assessment Results, and creates a python dictionary, of all students, and their results, for each course.
    context = {}
    # all_assessment_results = AssessmentResult.objects.all().filter().select_related("student", "course", "assessment")
    all_assessment_results = AssessmentResult.objects.filter(course__academic_year=2020)[:2000]
    big_dict = {}

    start_time = time.process_time()
    for result in all_assessment_results:
        student = result.student
        student_id = str(student.id)
        course = result.course
        course_id = str(course.id)
        assessment = result.assessment
        assessment_id = str(assessment.id)
        
        if student_id not in big_dict:
            big_dict[student_id] = {"student":{"GUID": student.GUID, "full_name": student.full_name, "degree_title": student.degree_title}, "courses": {}}

        if course_id not in big_dict[student_id]["courses"]:
            big_dict[student_id]["courses"][course_id] = {"course": {"code": course.code, "name":course.name, "academic_year": course.academic_year}, "assessments": {}}
        
        if assessment_id not in big_dict[student_id]["courses"][course_id]["assessments"]:
            big_dict[student_id]["courses"][course_id]["assessments"][assessment_id] = {"assessment": {"name": assessment.name, "weight": assessment.weighting}, "result": {"grade": result.grade, "preponderance": result.preponderance}}
    
    # context["student_data"] = big_dict
    # context["student_data_json"] = json.dumps(big_dict)
    print(f"Time taken to create full student data: {time.process_time() - start_time}")
    print("n queries executed", len(connection.queries))
    return HttpResponse('Greetings')
    result = render(request, "general/test_queries_3.html", context)
    return result

def test_queries_4_view(request):
    context = {}
    reset_queries()
    start = time.process_time()
    all_assessment_results = AssessmentResult.objects.filter().select_related("student", "course", "assessment")
        
    context["assessment_results"] = all_assessment_results
    result = render(request, "general/test_queries_4.html", context)
    print("n queries executed", len(connection.queries))
    print("Time taken to query and render template: ", time.process_time() - start)
    return result


def login_view(request):
    context = {}
    return render(request, "general/login.html", context)

def logout_view(request):
    context = {}
    return render(request, "general/logout.html", context)

def home_view(request):
    all_students = Student.objects.all()
    all_courses = Course.objects.all()

    context = {
        "students": all_students,
        "courses": all_courses,
    }

    if is_fetching_table_data(request):  
        all_data_json = {}
        if "students" in request.GET:   
            all_data_json = [student.get_data_for_table() for student in all_students]
        if "courses" in request.GET:
            all_data_json = [course.get_data_for_table() for course in all_courses]
            
        return JsonResponse(all_data_json, safe=False)

    return render(request, "general/home.html", context)

def all_students_view(request):
    print("time taken to render home page: ", time.process_time())
    all_students = Student.objects.all()
    # print(request.META['REMOTE_ADDR'])
    if is_fetching_table_data(request):
        # page = request.GET.get('page', 1)
        # size = request.GET.get('size', 200)
        # paginator = Paginator(all_students, size)
        
        # try:
        #     students = paginator.page(page)
        # except EmptyPage:
        #     students = []
        # except PageNotAnInteger:
        #     students = paginator.page(1)     
        all_students_json = [student.get_data_for_table() for student in all_students]
        # return JsonResponse({'data': all_students_json, 'last_page': paginator.num_pages})
        return JsonResponse(all_students_json, safe=False)

    return render(request, "general/all_students.html")

def all_courses_view(request):
    all_courses = Course.objects.all()
    if is_fetching_table_data(request):
        all_courses_json = [course.get_data_for_table() for course in all_courses]
        # return JsonResponse({'data': all_students_json, 'last_page': paginator.num_pages})
        return JsonResponse(all_courses_json, safe=False)

    return render(request, "general/all_courses.html")

def global_search_view(request):
    context = {}

    get_query_count("global_search_view")
    #TODO: refactor to do an ajax request for each table, not all at once (better lazy load)
    if request.method == "POST" and "global_search" in request.POST:
        search_term = request.POST["global_search"]
        context["search_term"] = search_term
        context["students"] = Student.objects.filter(Q(full_name__icontains=search_term) | Q(GUID__icontains=search_term)).exists()
        context["courses"] = Course.objects.filter(Q(code__icontains=search_term) | Q(name__icontains=search_term)).exists()
    
    if is_fetching_table_data(request):
        search_term = request.GET["search_term"]
        if "students" in request.GET:
            data = [student.get_data_for_table() for student in Student.objects.filter(Q(full_name__icontains=search_term) | Q(GUID__icontains=search_term))]
        elif "courses" in request.GET:
            # data = [
            #     course.get_data_for_table({
            #         "method": "get_extra_data_general",
            #         "args": []
            #     }) for course in Course.objects.filter(
            #         Q(code__icontains=search_term) | Q(name__icontains=search_term)
            #     )
            #     # .prefetch_related("assessments", "results")
            # ]
            #context[extra'cols ...]
            data = [course.get_data_for_table() for course in Course.objects.filter(
                Q(code__icontains=search_term) | Q(name__icontains=search_term)
            )]
        get_query_count("Time to search finish")
        return JsonResponse(data, safe=False)

    return render(request, "general/global_search.html", context)

def student_view(request, GUID):
    context = {"student": Student.objects.filter(GUID=GUID).first()}
    get_query_count("before student query")
    if is_fetching_table_data(request):
        student = Student.objects.filter(GUID=GUID).prefetch_related("results__assessment", "results__course").first()
        courses = student.courses.all()
        results = student.results.all()

        ##note that this is heavily optimized for less executed queries.
        def filter_results(course):
            return [result for result in results if result.course == course]

        all_courses_json = [
            course.get_data_for_table({
                "method": "get_extra_data_student",
                "args": [filter_results(course)]
            }) for course in courses
        ]
        get_query_count("after student query")
        return JsonResponse(all_courses_json, safe=False)

    return render(request, "general/student.html", context)

def course_view(request, code, year):
    context = {
        'course_other_years': []
    }
    get_query_count("before fetching course", False)
    for course in Course.objects.filter(code=code):
        if course.academic_year == year:
            context['current_course'] = course
        else:
            context['course_other_years'].append(course)

    if is_fetching_table_data(request):
        course = Course.objects.filter(code=code, academic_year=year).prefetch_related("assessments").first()
        students = course.students.all().prefetch_related("results__course", "results__assessment", "courses")[:50]
        course_assessments = course.assessments.all()

        all_students_json = [
            student.get_data_for_table(
                {
                    "method": "get_extra_data_course",
                    "args": [course_assessments, course]
                }
            ) for student in students
        ]
        extra_col_grps = {}

        for assessment in course_assessments:
            if assessment.type not in extra_col_grps:
                extra_col_grps[assessment.type] = {
                    "title": f"{assessment.get_type_display()} breakdown",
                    "columns": [],
                    "weighting": 0,
                    "headerHozAlign": "center",
                }
            extra_col_grps[assessment.type]["columns"].append({"title": str(assessment), "field": str(assessment.id), "cssClass": "format_grade"})
            extra_col_grps[assessment.type]["weighting"] += assessment.weighting
        
        for key, value in extra_col_grps.items():
            if value["columns"]:
                value["title"] += f"({value['weighting']}%)"
                if len(value["columns"]) > 1:
                    value["columns"].append({"title": "Total", "field": f"{key}_grade", "cssClass": "format_grade"})
                value.pop("weighting")

        extra_cols = list(extra_col_grps.values())
        extra_cols.append({"title": "Final grade(weighted)", "field": "final_grade", "cssClass": "format_grade"})

        get_query_count("after fetching course")
        response = JsonResponse({"data": all_students_json, "extra_cols":extra_cols}, safe=False)
        return response

    return render(request, "general/course.html", context)

def degree_classification_view(request, year=None):
    context = {'other_years': []}
    all_years = AcademicYear.objects.all()
    for academic_year in all_years:
        if academic_year.year == year:
            context['current_year'] = academic_year
        else:
            context['other_years'].append(academic_year)

    get_query_count("before fetching degree classification", False)
    if is_fetching_table_data(request):
        students = Student.objects.filter(current_academic_year=context['current_year'].year).prefetch_related("results__course", "results__assessment", "courses")
        all_students_json = [
            student.get_data_for_table(
                {
                    "method": "get_extra_data_degree_classification",
                    "args": []
                }
            ) for student in students
        ]
        get_query_count("after fetching degree classification")
        response = JsonResponse({"data": all_students_json}, safe=False)
        return response

    return render(request, "general/degree_classification.html", context)

#GUID, FULL_NAME, FINAL BAND, FINAL GPA, L4 BAND, L4 GPA, L3 BAND, L3 GPA, >A, >B, >C, >D, ... Project, Team ...

# def api_view(request):
#     context = {}
#     return render(request, "general/api.html", context)
