from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from general.models import Student, Course, Assessment, AssessmentResult, User, AcademicYear, StudentComment, CourseComment
from django.db import connection, reset_queries
import time
from django.db.models import Prefetch
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
import json
from exam_board.tools import server_print, get_query_count, degree_progression_levels, degree_classification_levels
from django.db import transaction
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.http import Http404
from django.contrib import messages


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

def update_context_with_extra_header_data(context, reverse_name, title="View other years!", year=None, all_years=None, extra_level_iterator=None):
    if not all_years:
        all_years = AcademicYear.objects.all()
    
    url_course = context.get("current_course")
    url_level = context.get("current_level")

    context['all_years'] = context.get('all_years', [])
    for academic_year in all_years:
        if year and year == academic_year.year:
            context['selected_year'] = academic_year
        elif academic_year.is_current and 'selected_year' not in context:
            context['selected_year'] = academic_year
        
        args = [academic_year.year]
        if url_course:
            args.insert(0, url_course.code)
        if url_level:
            args.insert(0, url_level)
        context['all_years'].append({'obj':academic_year, 'url':reverse(reverse_name, args=args)})
    
    if extra_level_iterator:
        context['all_levels'] = []
        for level in extra_level_iterator:
            if level == url_level:
                context['selected_level'] = level
            args = [level, context['selected_year'].year]
            context['all_levels'].append({'title': extra_level_iterator[level], 'level':level, 'url':reverse(reverse_name, args=args)})     
    
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
        "page_info": json.dumps({
            "title": "Home",
            "points_list": [
                "This is the homepage/dashboard",
                "You can view all students and courses",
                "This page contains a table. A table has multiple useful features that may not be obvious at first glance. Please click the tables help button, to get detailed help for any given table!",
                "This page contains charts. Charts are interactive, and will summairise the data stored in the table."
                "Note that actions that cause the table state to change - will trigger the charts to update as well."
            ]
        })
    }

    if is_fetching_table_data(request):  
        all_data_json = {}
        if "students" in request.GET:   
            all_data_json = [student.get_data_for_table() for student in all_students]
        if "courses" in request.GET:
            all_data_json = [course.get_data_for_table() for course in all_courses]
            
        return JsonResponse(all_data_json, safe=False)

    AssessmentResult.objects.all()

    return render(request, "general/home.html", context)

def all_students_view(request):
    all_students = Student.objects.all()
    context = {
        "page_info" :json.dumps({
            "title": f"All students",
            "points_list": [
                "This page allows you to view and access all the Students across all academic years.",
                "Whilst this page can be useful for comparing the cohort averages, note that much more data is available on the individual course pages.",
                "<b>How to access a given course page?:</b> Right click on the course, and select 'View Course' from the dropdown menu.",
                "You have the option to moderate courses directly in this page, <b>however</b> it might be more clear to do so from the individual course page.",
                "An additional header is provided which allows you to navigate across different years, to view all the courses offered."
            ]
        })}
    if is_fetching_table_data(request):   
        all_students_json = [student.get_data_for_table() for student in all_students]
        # return JsonResponse({'data': all_students_json, 'last_page': paginator.num_pages})
        return JsonResponse(all_students_json, safe=False)

    return render(request, "general/all_students.html", context)

def all_courses_view(request, year=None):
    context = {}
    update_context_with_extra_header_data(context, 'general:all_courses_exact', "View courses from other years", year=year)
    context["page_info"] = json.dumps({
        "title": f"All Courses for {context['selected_year'].year}",
        "points_list": [
            "This page allows you to view and access all the offered courses for a given Academic year",
            "Whilst this page can be useful for comparing the cohort averages, note that much more data is available on the individual course pages.",
            "<b>How to access a given course page?:</b> Right click on the course, and select 'View Course' from the dropdown menu.",
            "You have the option to moderate courses directly in this page, <b>however</b> it might be more clear to do so from the individual course page.",
            "An additional header is provided which allows you to navigate across different years, to view all the courses offered."
        ]
    })

    all_courses = Course.objects.filter(academic_year=context['selected_year'].year)
    if is_fetching_table_data(request):
        assessment_data = fetch_assessment_data_if_relevant(request)
        if assessment_data:
            return assessment_data

        get_query_count("all_courses_view", True)
        all_courses_json = [course.get_data_for_table({
            "method": "get_extra_data_general",
            "args": []
        }) for course in all_courses.prefetch_related("assessments", "results", "results__assessment")]
        get_query_count("Time to search finish")
        # return JsonResponse({'data': all_students_json, 'last_page': paginator.num_pages})
        return JsonResponse(all_courses_json, safe=False)

    return render(request, "general/all_courses.html", context)

def global_search_view(request):
    context = {}

    get_query_count("global_search_view")
    #TODO: refactor to do an ajax request for each table, not all at once (better lazy load)
    if request.method == "POST" and "global_search" in request.POST:
        search_term = request.POST["global_search"]
        context["search_term"] = search_term
        context["students"] = Student.objects.filter(Q(full_name__icontains=search_term) | Q(GUID__icontains=search_term)).exists()
        context["courses"] = Course.objects.filter(Q(code__icontains=search_term) | Q(name__icontains=search_term)).exists()
    
    context["page_info"] = json.dumps({
        "title": f"course/student search",
        "points_list": [
            f"This page will return all the students and courses that match the search term: <b>'{context['search_term'] if 'search_term' in context else 'no search term provided'}'</b>",
            "This page contains only basic information about the students and courses.",
            "It is recommended to use this page to find the relevant students and courses, and then access their individual pages to view more information about them.",
            "<b>How to access an individual course/student page?:</b> Right click on the student/course, and select 'View Student/Course' from the dropdown menu.",
        ]
    })
    
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
            data = [course.get_data_for_table(extra_data=None, fast_mod=True) for course in Course.objects.filter(
                Q(code__icontains=search_term) | Q(name__icontains=search_term)
            ).prefetch_related("assessments")]
        get_query_count("Time to search finish")
        return JsonResponse(data, safe=False)

    return render(request, "general/global_search.html", context)


def student_view(request, GUID):
    get_query_count("before student query")
    student = Student.objects.filter(GUID=GUID)
    if is_fetching_table_data(request):
        student_table = fetch_student_course_table_data_if_relevant(request)
        if student_table:
            return student_table
        assessment_data = fetch_assessment_data_if_relevant(request)
        if assessment_data:
            return assessment_data

        student = student.prefetch_related("results__assessment", "results__course").first()
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
    else:
        print("NOT FETCHING TABLE DATA")
    context = {"student": student.first()}
    context["page_info"] = json.dumps({
        "title": f"Individual student",
        "points_list": [
            f"This page provides information about the student: <b>'{context['student'].full_name}'</b>",
            "This page contains all the information about the student, including their results history, across all completed years.",
            "The chart shows the students Final, Coursework and Exam GPA's across all completed years. Chart elements can be toggled on/off by clicking on the legend.",
            "A detailed assessement breakdown is available by right-clicking on a course in the table and selecting 'Student grades and preponderance(popup)' from the dropdown menu.",
            "This popup also provides means to view and update the students preponderance history.",
            "You may also jump to any Course of interest, by right-clicking on the course row and selecting 'View Course page' from the dropdown menu.",
        ]
    })
    return render(request, "general/student.html", context)

def fetch_student_course_table_data_if_relevant(request):
    student_GUID = request.GET.get("student_GUID", "")
    course_id = request.GET.get("course_id", "")
    if student_GUID != "" and course_id != "":
        data_for_student_course_table = []
        all_course_assessments = Assessment.objects.filter(courses__id=course_id).order_by("weighting")
        for assessment in all_course_assessments:
            result = AssessmentResult.objects.filter(student__GUID=student_GUID, course__id=course_id, assessment=assessment).first()
            data_for_student_course_table.append({
                'type': assessment.get_type_display(),
                'name': assessment.name,
                'weighting': assessment.weighting,
                'moderation': assessment.moderation,
                'grade': min(result.grade + assessment.moderation, 22) if result else "Not completed",
                'preponderance': result.preponderance if result else "Not completed",
                'result_id': result.id if result else "Not completed",
            })
    else:
        return None
    
    return JsonResponse(data_for_student_course_table, safe=False)

def fetch_assessment_data_if_relevant(request):
    is_assessments = request.GET.get("assessments", None)
    course_id = request.GET.get("course_id", None)
    if course_id and is_assessments:
        course = Course.objects.filter(id=course_id).first()
        if course:
            data = [{
                "type": assessment.get_type_display(),
                "name": assessment.name,
                "weighting": assessment.weighting,
                "moderation": assessment.moderation,
                "moderation_user": assessment.moderated_by.get_name_verbose if assessment.moderated_by else "Not moderated",
                "moderation_date": assessment.moderation_datetime.strftime("%d/%m/%Y %H:%M") if assessment.moderation_datetime else "Not moderated",
                "id": str(assessment.id)
            }
                for assessment in course.assessments.all().order_by("weighting").select_related("moderated_by")
            ]
            return JsonResponse(data, safe=False)
    return None

def course_view(request, code, year):
    get_query_count("before fetching course", False)
    course = Course.objects.filter(code=code, academic_year=year)
    if is_fetching_table_data(request):
        ##extra tables fetching
        student_course_table = fetch_student_course_table_data_if_relevant(request)
        if student_course_table:
            return student_course_table
        course_assessmets_table = fetch_assessment_data_if_relevant(request)
        if course_assessmets_table:
            return course_assessmets_table
        ##end of extra tables fetching

        course = course.prefetch_related("assessments").first()
        students = course.students.all().prefetch_related("results__course", "results__assessment", "courses")
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
                    value["columns"].append({"title": "Overall", "field": f"{key}_grade", "cssClass": "format_grade"})
                value.pop("weighting")

        extra_cols = list(extra_col_grps.values())
        extra_cols.append({"title": "Final grade(weighted)", "field": "final_grade", "cssClass": "format_grade"})

        get_query_count("after fetching course")
        return JsonResponse({"data": all_students_json, "extra_cols":extra_cols}, safe=False)
    
    context = {
        "current_course": course.first(),
    }
    update_context_with_extra_header_data(context, 'general:course', "View courses from other years", year=year)
    context["page_info"] = json.dumps({
        "title": f"Individual course",
        "points_list": [
            f"This page provides all the information about the course: <b>'{context['current_course']}'</b> offered in <b>'{year}'</b>.",
            "Each row details the results obtained by a student, across all the assessed content of the course.",
            "Each assessed piece of work is grouped by assessment type, which can vary from course to course (eg. some courses will have group projects, some will have individual projects, and most will have exams.).",
            "Assessment order is random, so it might be useful to rearrange the columns, before exporting/printing the table."
            "A students preponderance history can be viewed and modified by right clicking on the student row and selecting the relevant option from the dropdown menu.",
            "An additional header is provided which allows you to navigate across other years where this course has been offered."
            "You may also jump to any Student of interest, by right-clicking on the student row and selecting 'View Student page' from the dropdown menu.",
        ]
    })
    return render(request, "general/course.html", context)

def level_progression_view(request, level, year=None):
    if level not in degree_progression_levels.keys():
        raise Http404("Invalid level")
    context = {
        'current_level': level,
    }
    update_context_with_extra_header_data(context, 'general:level_progression_exact', "View level progression of other years", year=year, all_years=None, extra_level_iterator=degree_progression_levels)
    context["page_info"] = json.dumps({
        "title": f"Level progression",
        "points_list": [
            f"This page provides all the information about cohort <b>level {level}</b> in <b>'{context['selected_year'].year}'</b>.",
            "Each row details the students overall performance, across all the courses in the given level and year.",
            "The panel on the right offers charts that provide insights into the overall performance of the cohort, as well as the distribution of students who have a guaranteed pass, discretionary pass or fail to proceed into next level.",
            "The panel on the left provides some aggregate cohort statistics, such as number of students, and the average grade across all courses.",
            "An additional header is provided which allows you to navigate across different academic years and levels (1,2,3 or 4)"
            "You may also jump to any Student of interest, by right-clicking on the student row and selecting 'View Student page' from the dropdown menu.",
        ]
    })
    context["level_head"] = User.objects.filter(level_head__academic_year=context["selected_year"], level_head__level=level).first()
    get_query_count("before fetching level progression", True)
    if is_fetching_table_data(request):
        student_course_map = {}
        courses = Course.objects.filter(academic_year=context["selected_year"].year).prefetch_related("assessments", "students", "results", "results__assessment", "results__student")
        
        for course in courses:
            enrolled_students = [student for student in course.students.all() if (student.current_level - (student.current_academic_year - context["selected_year"].year)) == level]
            if not enrolled_students:
                continue

            expected_assessments = course.assessments.all()
            course_results = course.results.all()
            student_id_to_results_map = {}
            for result in course_results:
                if result.student.id not in student_id_to_results_map:
                    student_id_to_results_map[result.student.id] = {}
                if course.id not in student_id_to_results_map[result.student.id]:
                    student_id_to_results_map[result.student.id][course.id] = {}
                student_id_to_results_map[result.student.id][course.id][result.assessment.id] = result
            
            for student in enrolled_students:
                if student not in student_course_map:
                    student_course_map[student] = {}
                student_course_map[student][course] = []
                for assessment in expected_assessments:
                    student_course_map[student][course].append((assessment, student_id_to_results_map.get(student.id, {}).get(course.id, {}).get(assessment.id, None)))

        all_students_json = [
            student.get_data_for_table(
                {
                    "method": "get_extra_data_level_progression",
                    "args": [context["selected_year"].level_progression_settings[str(context["current_level"])] ,course_map]
                }
            ) for student, course_map in student_course_map.items()
        ]
        get_query_count("after fetching level progression")
        return JsonResponse(all_students_json, safe=False)

    return render(request, "general/level_progression.html", context)

def degree_classification_view(request, level, year=None):
    if level not in degree_classification_levels.keys():
        raise Http404("Invalid level")
    context = {
        'current_level': level,
    }
    update_context_with_extra_header_data(context, 'general:degree_classification_exact', "View degree classifications of other years", year=year, all_years=None, extra_level_iterator=degree_classification_levels)
    context["page_info"] = json.dumps({
        "title": f"Degree classification",
        "points_list": [
            f"This page provides all the information about students who graduate at <b>level {level}</b> in <b>'{context['selected_year'].year}'</b>.",
            "Each row details the students overall performance, across all the courses in the given level and year.",
            "The panel on the right offers charts that provide insights into the overall performance of the graduation cohort, as well as the distribution of students across their recieved final award.",
            "The panel on the left provides some aggregate cohort statistics, such as number of students, and the average grades across all levels.",
            "An additional header is provided which allows you to navigate across different academic years and degree classifications (Bsc/Beng or Msc/Meng)"
            "You may also jump to any Student of interest, by right-clicking on the student row and selecting 'View Student page' from the dropdown menu.",
        ]
    })
    get_query_count("before fetching degree classification", False)
    if is_fetching_table_data(request):
        masters = level == 5
        students = set(Student.objects.filter(end_academic_year=context['selected_year'].year, current_academic_year=context['selected_year'].year, is_masters=False if not masters else True).prefetch_related("results__course", "results__assessment", "courses", "courses__assessments"))
        student_course_map_lvl5 = {}
        student_results_map_lvl5 = {}
        student_course_map_lvl4 = {}
        student_results_map_lvl4 = {}
        student_course_map_lvl3 = {}
        student_results_map_lvl3 = {}
        no_course_students = set()
        base_year = context['selected_year'].year - 1 if not masters else context['selected_year'].year - 2
        for student in students:
            if student.current_level != level:
                no_course_students.add(student)
                continue

            if masters:
                lvl5_courses = [course for course in student.courses.all() if course.academic_year == base_year + 2]
                if not lvl5_courses:
                    no_course_students.add(student)
                    continue

            lvl4_courses = [course for course in student.courses.all() if course.academic_year == base_year + 1]
            if not lvl4_courses:
                no_course_students.add(student)
                continue
    
            lvl3_courses = [course for course in student.courses.all() if course.academic_year == base_year]
            if not lvl3_courses:
                no_course_students.add(student)
                continue

            if masters:
                student_course_map_lvl5[student] = lvl5_courses
                student_results_map_lvl5[student] = [result for result in student.results.all() if result.course.academic_year == base_year + 2]

            student_course_map_lvl4[student] = lvl4_courses
            student_results_map_lvl4[student] = [result for result in student.results.all() if result.course.academic_year == base_year + 1]

            student_course_map_lvl3[student] = lvl3_courses
            student_results_map_lvl3[student] = [result for result in student.results.all() if result.course.academic_year == base_year]

        final_students = students.difference(no_course_students)
        
        if not final_students:
            return JsonResponse([], safe=False)
        
        all_students_json = [
            student.get_data_for_table(
                {
                    "method": "get_extra_data_degree_classification",
                    "args": [context["selected_year"].degree_classification_settings, masters, student_course_map_lvl3[student], student_results_map_lvl3[student], student_course_map_lvl4[student], student_results_map_lvl4[student], student_course_map_lvl5[student] if masters else {}, student_results_map_lvl5[student] if masters else {}]
                }
            ) for student in final_students
        ]

        get_query_count("after fetching degree classification")
        response = JsonResponse(all_students_json, safe=False)

        return response

    return render(request, "general/degree_classification.html", context)

def degree_classification_grading_rules_view(request, year=None):
    context = {}
    update_context_with_extra_header_data(context, 'general:degree_grading_rules_exact', "View grading rules of other years", year=year)
    context["page_info"] = json.dumps({
        "title": f"Degree classification grading rules",
        "points_list": [
            f"This page showcases the rules used to calculate the degree classifications, for a given year. Currently: <b>'{context['selected_year'].year}'</b>.",
            "Clicking the 'Edit degree classification rules' button will allow you view and modify the degree classication rules for the selected year.",
            "An additional header is provided which allows you to navigate across different academic years"
        ]
    })
    return render(request, "general/degree_grading_rules.html", context)

def level_progression_rules_view(request, level, year=None):
    if level not in [1, 2, 3, 4]:
        raise Http404("Invalid level")
    context = {
        'current_level': level,
    }
    update_context_with_extra_header_data(context, 'general:level_progression_rules_exact', "View level progression rules of other years", year=year, all_years=None, extra_level_iterator=degree_progression_levels)
    context["page_info"] = json.dumps({
        "title": f"Level progression determining rules",
        "points_list": [
            f"This page showcases the rules used to determine the requirements for progression into the next level, for a given year and level. Currently: <b>'{context['selected_year'].year}'</b> and <b>'Level {level}'</b>.",
            "Clicking the 'Edit level progression rules' button will allow you view and modify the level progression rules for the selected level and year.",
            "An additional header is provided which allows you to navigate across different academic years and levels"
        ]
    })
    context['table_settings'] = context['selected_year'].level_progression_settings_for_table(str(level))
    return render(request, "general/level_progression_rules.html", context)
#GUID, FULL_NAME, FINAL BAND, FINAL GPA, L4 BAND, L4 GPA, L3 BAND, L3 GPA, >A, >B, >C, >D, ... Project, Team ...

def api_view(request):
    response = {"status": "Uknown error occurred.", "data": None}
    student_id = request.POST.get("student_id", None)
    course_id = request.POST.get("course_id", None)

    if request.method == "POST":
        action = request.POST.get("action", None)
        if action:
            data = json.loads(request.POST.get("data", "{}"))

            #MODERATION
            if action == "moderation":
                mode = data.get("mode", None)
                value = data.get("value", 0)
                assessment_ids = data.get("assessment_ids", None)
                course_id = data.get("course_id", None)
                ##need to create new assessments, and update course_assessment_map, and all the grade results
                assessments_db = Assessment.objects.filter(id__in=assessment_ids)
                new_assessment_refs = []
                new_to_create = []

                if not value or not mode or not assessment_ids or not assessments_db or not course_id:
                    return JsonResponse({"status": "Server error. Invalid data recieved.", "data": None}, safe=False)
                
                value = int(value)
                ass_result_to_update_map = {}
                course = Course.objects.filter(id=course_id).first()

                def value_conversion_based_on_mode(value, existing_value=0):
                    if mode == "increase":
                        return value + existing_value
                    elif mode == "decrease":
                        return value*-1 + existing_value
                    elif mode == "remove":
                        return 0

                    assert True == False, "Invalid mode. Should be increase, decrease or remove."
    
                ##think about REPLACEMENT edge case. we can only delete if assessment is not used in any other course.
                for assessment_db in assessments_db:
                    instance = Assessment.objects.filter(name=assessment_db.name, weighting=assessment_db.weighting, type=assessment_db.type, moderation=value_conversion_based_on_mode(value, assessment_db.moderation)).first()
                    if not instance:
                        instance = Assessment(name=assessment_db.name, weighting=assessment_db.weighting, type=assessment_db.type, moderation=value_conversion_based_on_mode(value))
                        new_to_create.append(instance)

                    if instance.moderation != 0:
                        instance.moderated_by = request.user
                        instance.moderation_datetime = timezone.now()
                    else:
                        instance.moderated_by = None
                        instance.moderation_datetime = None
                    new_assessment_refs.append(instance)

                    ass_results = AssessmentResult.objects.filter(assessment=assessment_db, course=course)
                    ass_result_to_update_map[instance] = ass_results
                

                course.assessments.remove(*assessments_db)
                Assessment.objects.bulk_create(new_to_create)
                course.assessments.add(*new_assessment_refs)
                for key, value in ass_result_to_update_map.items():
                    value.update(assessment=key)
                Assessment.objects.filter(courses=None).exclude(moderation=0).delete()
                
                return JsonResponse({"status": "Moderation successful.", "data": True}, safe=False)

            #GRADING RULES
            if action == "save_grading_rules":
                year_id = request.POST.get("year_id", None)
                level = request.POST.get("level", None)
                if year_id:
                    year = AcademicYear.objects.filter(id=year_id).first()
                    if year:
                        attribute = "level_progression_settings" if level else "degree_classification_settings"
                        existing_state = getattr(year, attribute)
                        if (existing_state if not level else existing_state[level]) != data:
                            if level:
                                existing_state[level] = data
                            else:
                                existing_state = data
                            setattr(year, attribute, existing_state)
                            year.save()
                            response["status"] = "Rules updated succesfully!"
                        else:
                            response["status"] = "No rule changes detected."
                    else:
                        response["status"] = "Server error. Academic year not found."
            
            #PREPONDERANCE
            if action == "update_preponderance":
                results_to_save = [] ##make sure we save at the very end, to make sure all data is valid
                for row in data:
                    result_id = row.get("result_id", "")
                    if not result_id:
                        return JsonResponse({"status": "Server error. Result id not found.", "data": None}, safe=False)
                    result = AssessmentResult.objects.filter(id=result_id).first()
                    if not result:
                        return JsonResponse({"status": "Server error. Result not found.", "data": None}, safe=False)
                    preponderance = row.get("preponderance", "")
                    if preponderance not in [tuple[0] for tuple in AssessmentResult.preponderance_choices]:
                        return JsonResponse({"status": "Server error. Invalid preponderance.", "data": None}, safe=False)
                    
                    if result.preponderance != preponderance:
                        result.preponderance = preponderance
                        results_to_save.append(result)
                
                if results_to_save:
                    AssessmentResult.objects.bulk_update(results_to_save, ["preponderance"])
                    response["status"] = "Preponderance(s) updated succesfully!"
                    response["data"] = True
                else:
                    response["status"] = "No changes detected."

            #STUDENT COMMENTS
            if action in ["add_comment", "delete_comments"]:
                obj_for_comments = None
                if student_id:
                    obj_for_comments = Student.objects.filter(id=student_id).first()
                    comment_object = StudentComment
                elif course_id:
                    obj_for_comments = Course.objects.filter(id=course_id).first()
                    comment_object = CourseComment

                if obj_for_comments:
                    if action == "add_comment":
                        comment = data
                        if comment != "" and type(comment) == str and len(comment) <= 250:
                            obj_for_comments.add_comment(comment=comment, added_by=request.user)
                            response["status"] = "Comment added succesfully!"
                            response["data"] = obj_for_comments.comments_for_table
                        else:
                            response["status"] = "Comment too short/long or invalid format. Please try again."
                    
                    elif action == "delete_comments":
                        comment_id_list = data
                        if comment_id_list:
                            comments = comment_object.objects.filter(id__in=comment_id_list).select_related("added_by")
                            status_string = "Deletion cancelled. Please address the following issues, and try again:\n"
                            n_comments = 0
                            for comment in comments:
                                n_comments += 1
                                if comment.added_by != request.user:
                                    status_string += f"Comment {n_comments} not deleted. You are not the author of this comment.\n"
                            
                            if n_comments == len(comment_id_list):
                                comments.delete()
                                response["status"] = f"{n_comments} selected comment{'s' if n_comments>1 else ''} deleted succesfully!"
                                response["data"] = obj_for_comments.comments_for_table
                            else:
                                response["status"] = "Recieved comments do not match the comments to be deleted. Please refresh the page and try again."
                            
                            response["data"] = obj_for_comments.comments_for_table
                        else:
                            response["status"] = "No comment id's provided, for deletion."
                else:
                    response["status"] = "Server error. Student or course not found."
        else:
            response["status"] = "No action provided."
    
    return JsonResponse(response)

##Incomplete functionality views - DO NOT USE IN PRODUCTION
def login_view(request, prev_path):
    if request.user.is_authenticated:
        return redirect("general:home")
    else:
        ##get a random user from the User model, and log this anonymous user in.
        #this is a test view, that allows anyone to login with a click of a button
        #this is not a production view, and should not be used in production
        user = User.objects.order_by("?").first()
        login(request, user)
        messages.info(request, f"Logged in as {user.get_name_verbose}!")
        return redirect(prev_path)

def logout_view(request, prev_path):
    logout(request)
    messages.info(request, "Logged out succesfully!")
    return redirect(prev_path)
