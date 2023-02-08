# all_assessments = self.assessments.all()
# all_results = self.results.all()
# all_students = self.students.all()
# student_grades = []
# for student in all_students:
#     student_totals_tracker = {
#         'coursework': [0, 0],
#         'exam': [0, 0],
#         'final': 0,
#     }
#     for assessment in all_assessments:
#         for result in all_results:
#             if result.assessment == assessment: ##we found a result for this assessment
#                 if result.student == student: ##we found a result for this student
#                     if result.assessment.type == 'E':
#                         student_totals_tracker['exam'][0] += result.grade * result.assessment.weighting
#                         student_totals_tracker['exam'][1] += result.assessment.weighting
#                     else:
#                         student_totals_tracker['coursework'][0] += result.grade * result.assessment.weighting
#                         student_totals_tracker['coursework'][1] += result.assessment.weighting

#                     student_totals_tracker['final'] += (result.grade * result.assessment.weighting) / 100
#                 else: ##we did not find a result for this student - means they get a 0 for this assessment
#                     pass

#     student_grades.append([
#         (student_totals_tracker['coursework'][0] / student_totals_tracker['coursework'][1]) if student_totals_tracker['coursework'][1] > 0 else 0,
#         (student_totals_tracker['exam'][0] / student_totals_tracker['exam'][1]) if student_totals_tracker['exam'][1] > 0 else 0,
#         student_totals_tracker['final'],
#     ])

# for student in student_grades:
#     extra_data['coursework_avg'] += student[0]
#     extra_data['exam_avg'] += student[1]
#     extra_data['final_grade'] += student[2]

# extra_data['coursework_avg'] = round(extra_data['coursework_avg'] / len(student_grades), 2)
# extra_data['exam_avg'] = round(extra_data['exam_avg'] / len(student_grades), 2)
# extra_data['final_grade'] = round(extra_data['final_grade'] / len(student_grades), 2)
# return extra_data

# function percent_to_integer_band(percent, round_up=true) {
#     //C3-B1, D1-E3, A5-A1, F1-H
#     if (bound_check(percent, 49.5, 69.5)) {
#         if (percent < 53.5)
#             return 12
#         else if (bound_check(percent, 53.5,56.5))
#             return 13
#         else if (bound_check(percent,56.5,59.5))
#             return 14
#         else if (bound_check(percent,59.5,63.5))
#             return 15
#         else if (bound_check(percent,63.5,66.5))
#             return 16
#         else if (bound_check(percent,66.5,69.5))
#             return 17
#     } else if (bound_check(percent, 29.5, 49.5)) {
#         if (percent < 33.5)
#             return 6
#         else if (bound_check(percent,33.5,36.5))
#             return 7
#         else if (bound_check(percent,36.5,39.5))
#             return 8
#         else if (bound_check(percent,39.5,43.5))
#             return 9
#         else if (bound_check(percent,43.5,46.5))
#             return 10
#         else if (bound_check(percent,46.5,49.5))
#             return 11
#     } else if (percent >= 69.5) {
#         if (percent < 73.5)
#             return 18
#         else if (bound_check(percent,73.5,78.5))
#             return 19
#         else if (bound_check(percent,78.5,84.5))
#             return 20
#         else if (bound_check(percent,84.5,91.5))
#             return 21
#         else if (percent >= 91.5)
#             return 22
#     } else if (percent < 29.5) {
#         if (percent < 9.5)
#             return 0
#         else if (bound_check(percent,9.5,14.5))
#             return 1
#         else if (bound_check(percent,14.5,19.5))
#             return 2
#         else if (bound_check(percent,19.5,23.5))
#             return 3
#         else if (bound_check(percent,23.5,26.5))
#             return 4
#         else if (bound_check(percent,26.5,29.5))
#             return 5
#     }
# }
