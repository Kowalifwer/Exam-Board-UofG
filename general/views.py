from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from general.models import Student, Course, Assessment, AssessmentResult, User, AcademicYear, Comment
from django.db import connection, reset_queries
import time
from django.db.models import Prefetch
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
import json
from exam_board.tools import server_print, get_query_count
from django.db import transaction
from django.utils import timezone


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
        assessment_data = fetch_assessment_data_if_relevant(request)
        if assessment_data:
            return assessment_data

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
    get_query_count("before student query")
    if is_fetching_table_data(request):
        student_table = fetch_student_course_table_data_if_relevant(request)
        if student_table:
            return student_table
        assessment_data = fetch_assessment_data_if_relevant(request)
        if assessment_data:
            return assessment_data

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
    else:
        print("NOT FETCHING TABLE DATA")
    context = {"student": Student.objects.filter(GUID=GUID).first()}
    return render(request, "general/student.html", context)

def course_student_view(request):
    pass

def fetch_student_course_table_data_if_relevant(request):
    student_GUID = request.GET.get("student_GUID", "")
    course_id = request.GET.get("course_id", "")
    if student_GUID != "" and course_id != "":
        data_for_student_course_table = []
        all_course_assessments = Assessment.objects.filter(courses__id=course_id)
        for assessment in all_course_assessments:
            result = AssessmentResult.objects.filter(student__GUID=student_GUID, course__id=course_id, assessment=assessment).first()
            data_for_student_course_table.append({
                'type': assessment.get_type_display(),
                'name': assessment.name,
                'weighting': assessment.weighting,
                'grade': result.grade if result else "Not completed",
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
            data = [
                {"type": assessment.get_type_display(),
                "name": assessment.name,
                "weighting": assessment.weighting,
                "moderation": f"{'' if assessment.moderation <= 0 else '+'}{assessment.moderation} bands.",
                "moderation_user": assessment.moderated_by.get_name_verbose if assessment.moderated_by else "Not moderated",
                "moderation_date": assessment.moderation_datetime.strftime("%d/%m/%Y %H:%M") if assessment.moderation_datetime else "Not moderated",
                "id": str(assessment.id)}
            for assessment in course.assessments.all().order_by("weighting").select_related("moderated_by")]
            return JsonResponse(data, safe=False)
    return None


def course_view(request, code, year):
    get_query_count("before fetching course", False)
    if is_fetching_table_data(request):
        ##extra tables fetching
        student_course_table = fetch_student_course_table_data_if_relevant(request)
        if student_course_table:
            return student_course_table
        course_assessmets_table = fetch_assessment_data_if_relevant(request)
        if course_assessmets_table:
            return course_assessmets_table
        ##end of extra tables fetching

        course = Course.objects.filter(code=code, academic_year=year).prefetch_related("assessments").first()
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
                    value["columns"].append({"title": "Total", "field": f"{key}_grade", "cssClass": "format_grade"})
                value.pop("weighting")

        extra_cols = list(extra_col_grps.values())
        extra_cols.append({"title": "Final grade(weighted)", "field": "final_grade", "cssClass": "format_grade"})

        get_query_count("after fetching course")
        return JsonResponse({"data": all_students_json, "extra_cols":extra_cols}, safe=False)
    
    context = {
        'course_other_years': []
    }
    
    for course in Course.objects.filter(code=code).select_related("lecturer"):
        if course.academic_year == year:
            context['current_course'] = course
        else:
            context['course_other_years'].append(course)

    return render(request, "general/course.html", context)

def degree_classification_view(request, year=None):
    context = {'other_years': []}
    all_years = AcademicYear.objects.all()
    for academic_year in all_years:
        if year and year == academic_year.year:
            context['current_year'] = academic_year
        elif academic_year.is_current and 'current_year' not in context:
            context['current_year'] = academic_year
        else:
            context['other_years'].append(academic_year)

    get_query_count("before fetching degree classification", False)
    if is_fetching_table_data(request):
        level = request.GET.get("level")
        if level not in ("4", "5"):
            return JsonResponse([], safe=False)
        
        masters = level == "5"
        students = set(Student.objects.filter(end_academic_year=context['current_year'].year, current_academic_year=context['current_year'].year, is_masters=False if not masters else True).prefetch_related("results__course", "results__assessment", "courses", "courses__assessments"))
        student_course_map_lvl5 = {}
        student_results_map_lvl5 = {}
        student_course_map_lvl4 = {}
        student_results_map_lvl4 = {}
        student_course_map_lvl3 = {}
        student_results_map_lvl3 = {}
        no_course_students = set()
        base_year = context['current_year'].year - 1 if not masters else context['current_year'].year - 2
        for student in students:
            if student.current_level != int(level):
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
            
        all_students_json = [
            student.get_data_for_table(
                {
                    "method": "get_extra_data_degree_classification",
                    "args": [masters, student_course_map_lvl3[student], student_results_map_lvl3[student], student_course_map_lvl4[student], student_results_map_lvl4[student], student_course_map_lvl5[student] if masters else {}, student_results_map_lvl5[student] if masters else {}]
                }
            ) for student in students.difference(no_course_students)
        ]

        get_query_count("after fetching degree classification")
        response = JsonResponse(all_students_json, safe=False)

        return response

    return render(request, "general/degree_classification.html", context)

def grading_rules_view(request, year=None):
    context = {'other_years': []}
    all_years = AcademicYear.objects.all()
    for academic_year in all_years:
        if year and year == academic_year.year:
            context['current_year'] = academic_year
        elif academic_year.is_current and 'current_year' not in context:
            context['current_year'] = academic_year
        else:
            context['other_years'].append(academic_year)
    print(context)
    return render(request, "general/grading_rules.html", context)

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
                print("value", value)
                ass_result_to_update_map = {}
                course = Course.objects.filter(id=course_id).first()
                print("course", course, course_id)

                def value_converseion_based_on_mode(value, existing_value=0):
                    if mode == "increase":
                        return value + existing_value
                    elif mode == "decrease":
                        return value*-1 + existing_value
                    elif mode == "remove":
                        return 0

                    assert True == False, "Invalid mode. Should be increase, decrease or remove."
    
                ##think about REPLACEMENT edge case. we can only delete if assessment is not used in any other course.
                for assessment_db in assessments_db:
                    instance = Assessment.objects.filter(name=assessment_db.name, weighting=assessment_db.weighting, type=assessment_db.type, moderation=value_converseion_based_on_mode(value, assessment_db.moderation)).first()
                    if not instance:
                        instance = Assessment(name=assessment_db.name, weighting=assessment_db.weighting, type=assessment_db.type, moderation=value_converseion_based_on_mode(value))
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
                    print(key, value)
                    value.update(assessment=key)
                Assessment.objects.filter(courses=None).exclude(moderation=0).delete()
                
                return JsonResponse({"status": "Moderation successful.", "data": True}, safe=False)

            #GRADING RULES
            if action == "save_grading_rules":
                year_id = request.POST.get("year_id", None)
                if year_id:
                    year = AcademicYear.objects.filter(id=year_id).first()
                    if year:
                        if year.degree_classification_settings != data:
                            year.degree_classification_settings = data
                            year.save()
                            response["status"] = "Degree classification updated succesfully!"
                        else:
                            response["status"] = "No changes detected."
                    else:
                        response["status"] = "Server error. Academic year not found."
            
            #PREPONDERANCE
            if action == "update_preponderance":
                print(data)
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
            if action in ["add_student_comment", "delete_student_comment"]:
                student_id = request.POST.get("student_id", None)
                if student_id:
                    student = Student.objects.filter(id=student_id).first()
                    if student:
                        if action == "add_student_comment":
                            comment = data
                            if comment != "" and type(comment) == str and len(comment) <= 200:
                                comment_instance = Comment.objects.create(student=student, comment=comment, added_by=request.user)
                                student.comments.add(comment_instance)

                                response["status"] = "Comment added succesfully!"
                                response["data"] = student.student_comments_for_table
                            else:
                                response["status"] = "Invalid comment."
                        elif action == "delete_student_comment":
                            comment_id = data
                            if comment_id:
                                comment = Comment.objects.filter(id=comment_id).select_related("added_by").first()
                                if comment:
                                    if comment.added_by != request.user:
                                        response["status"] = "You are not allowed to delete this comment."
                                    else:
                                        comment.delete()
                                        response["status"] = "Comment deleted succesfully!"
                                        response["data"] = student.student_comments_for_table
                                else:
                                    response["status"] = "Comment not found."
                            else:
                                response["status"] = "No comment id provided."
                    else:
                        response["status"] = "Student not found."
                else:
                    response["status"] = "No student id provided."
        else:
            response["status"] = "No action provided."
    
    return JsonResponse(response)
