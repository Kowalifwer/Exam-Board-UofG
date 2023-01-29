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