##TEST VIEWS
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