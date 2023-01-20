from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid
from django.shortcuts import reverse
from exam_board.tools import default_degree_classification_settings_dict
import json
from math import ceil as math_ceil
from exam_board.tools import band_integer_to_band_letter_map


# Create your models here.
class UUIDModel(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)

    class Meta:
        abstract = True

class AcademicYear(models.Model):
    year = models.IntegerField(unique=True)
    is_current = models.BooleanField(default=True)  # TODO: Ensure that only 1 year is current at a time
    degree_classification_settings = models.JSONField(null=False, blank=False, default=default_degree_classification_settings_dict)

    #create a getter for degree_classification_settings that returns the default settings in JSON
    @property
    def degree_classification_settings_for_table(self):
        try:
            return json.dumps(list(self.degree_classification_settings.values()))
        except:
            print("Error in degree_classification_settings_for_table")
            return json.dumps([])

    def __str__(self):
        return f"{self.year} - {'Currently active' if self.is_current else 'Not current year'}"

class User(AbstractUser, UUIDModel):
    level_choices = [
        (0, 'No levels'),
        (1, 'Level 1'),
        (2, 'Level 2'),
        (3, 'Level 3'),
        (4, 'Level 4'),
        (5, 'Level 5'),
        (10, 'All levels'),
    ]
    class_head_level = models.IntegerField(choices=level_choices, default=0)

    title = models.CharField(max_length=20, blank=True, null=True)

    @property
    def is_classhead(self):
        return self.level > 0
    
    @property
    def get_name_verbose(self):
        full_name_string = self.get_full_name()
        if self.title:
            full_name_string = f"{self.title}. {full_name_string}"
        
        if not full_name_string:
            if self.is_superuser:
                full_name_string = "SUPER-ADMIN"
            else:
                full_name_string = self.email
        
        return full_name_string

    def __str__(self):
        return f"{self.title + '.' if self.title else ''} {self.get_full_name()}"


class Student(UUIDModel):
    GUID = models.CharField(max_length=8, unique=True)
    full_name = models.CharField(max_length=225)
    degree_name = models.CharField(max_length=225)
    degree_title = models.CharField(max_length=100)

    is_faster_route = models.BooleanField(default=False)
    is_masters = models.BooleanField(default=False)
    start_academic_year = models.IntegerField()
    end_academic_year = models.IntegerField()
    current_academic_year = models.IntegerField()

    courses = models.ManyToManyField("Course", related_name="students")

    level_choices = {
        0: 'No levels',
        1: 'Level 1',
        2: 'Level 2',
        3: 'Level 3',
        4: 'Level 4',
        5: 'Level 5(M)',

        6: 'PhD', #6 onwards is phd
    }

    @property
    def current_level(self):
        return self.current_academic_year - self.start_academic_year + 1

    @property
    def current_level_verbose(self):  # TODO Fix this, by taking current month into consideration (2022-2023 might still be first_year but calculation will return second_year). Also consider is_faster year.
        if self.current_level >= 6:
            return "PhD"
        return self.level_choices.get(self.current_level, "N/A")

    @property
    def matriculation_number(self):
        return int(self.GUID[:-1]) if self.GUID[-1].isalpha() else int(self.GUID)

    def __str__(self):
        return f"{self.GUID} - {self.full_name}"
    
    @property
    def page_url(self):
        return reverse('general:student', args=[self.GUID])
    
    @property
    def student_comments_for_table(self):
        return json.dumps([{
            "comment": comment.comment,
            "added_by": comment.added_by.get_name_verbose,
            "timestamp": comment.timestamp.strftime("%d/%m/%Y %H:%M"),
            "id": str(comment.id),
        } for comment in self.comments.all().select_related('added_by')])
    
    def get_data_for_table(self, extra_data=None):
        table_data = {
            "GUID": self.GUID,
            "name": self.full_name,
            "degree_name": self.degree_name,
            "degree_title": self.degree_title,
            "is_masters": self.is_masters,
            "current_year": self.current_level_verbose,
            "start_year": self.start_academic_year,
            "end_year": self.end_academic_year,
            "page_url": self.page_url,
        }
        if extra_data:
            extra_data = getattr(self, extra_data["method"])(*extra_data["args"])
            table_data.update(extra_data)
        
        return table_data
    
    def get_extra_data_degree_classification(self, lvl4_courses, lvl4_results, lvl3_courses, lvl3_results):
        extra_data = {
            "final_band": 0,
            "final_gpa": 0,
            "l4_band": 0,
            "l4_gpa": 0,
            "l3_band": 0,
            "l3_gpa": 0,
            "greater_than_a": 0,
            "greater_than_b": 0,
            "greater_than_c": 0,
            "greater_than_d": 0,
            "greater_than_e": 0,
            "greater_than_f": 0,
            "greater_than_g": 0,
            "greater_than_h": 0,
            "project": 0,
            "team": 0,
        }
        
        #student -> courses -> expected_assessments -> assessment_result
        # for course in courses:
        #     expected_assessments = course...
        #     for assessment in expected_assessments:

        #if its a project, we need to sum the grades

        final_l4_grade_adder_tuples = [0,0]
        final_l3_grade_adder_tuples = [0,0]
        
        def calculate_level_data(courses, results, grade_adder_tuples, update_greater_than=False):
            for course in courses:
                credits = course.credits
                expected_assessments = course.assessments.all()
                course_grade = 0
                for assessment in expected_assessments:
                    result = [result for result in results if result.assessment == assessment]
                    grade = 0
                    if result:
                        grade = result[0].grade
                    course_grade += grade * assessment.weighting / 100

                grade_adder_tuples[0] += course_grade * credits
                grade_adder_tuples[1] += credits
                
                if update_greater_than:
                    if course_grade >= 70:
                        extra_data["greater_than_a"] += credits
                        extra_data["greater_than_b"] += credits
                        extra_data["greater_than_c"] += credits
                        extra_data["greater_than_d"] += credits
                        extra_data["greater_than_e"] += credits
                        extra_data["greater_than_f"] += credits
                        extra_data["greater_than_g"] += credits
                        extra_data["greater_than_h"] += credits
                    
                    elif course_grade >= 60:
                        extra_data["greater_than_b"] += credits
                        extra_data["greater_than_c"] += credits
                        extra_data["greater_than_d"] += credits
                        extra_data["greater_than_e"] += credits
                        extra_data["greater_than_f"] += credits
                        extra_data["greater_than_g"] += credits
                        extra_data["greater_than_h"] += credits
                    
                    elif course_grade >= 50:
                        extra_data["greater_than_c"] += credits
                        extra_data["greater_than_d"] += credits
                        extra_data["greater_than_e"] += credits
                        extra_data["greater_than_f"] += credits
                        extra_data["greater_than_g"] += credits
                        extra_data["greater_than_h"] += credits
                    
                    elif course_grade >= 40:
                        extra_data["greater_than_d"] += credits
                        extra_data["greater_than_e"] += credits
                        extra_data["greater_than_f"] += credits
                        extra_data["greater_than_g"] += credits
                        extra_data["greater_than_h"] += credits
                    
                    elif course_grade >= 30:
                        extra_data["greater_than_e"] += credits
                        extra_data["greater_than_f"] += credits
                        extra_data["greater_than_g"] += credits
                        extra_data["greater_than_h"] += credits
                    
                    elif course_grade >= 20:
                        extra_data["greater_than_f"] += credits
                        extra_data["greater_than_g"] += credits
                        extra_data["greater_than_h"] += credits
                    
                    elif course_grade >= 10:
                        extra_data["greater_than_g"] += credits
                        extra_data["greater_than_h"] += credits
                    
                    elif course_grade >= 0:
                        extra_data["greater_than_h"] += credits
                
            return grade_adder_tuples
        
        final_l4_grade_adder_tuples = calculate_level_data(lvl4_courses, lvl4_results, final_l4_grade_adder_tuples, update_greater_than=True)
        final_l3_grade_adder_tuples = calculate_level_data(lvl3_courses, lvl3_results, final_l3_grade_adder_tuples)
        final_gpa = 0

        if final_l4_grade_adder_tuples[1] == 0: ##no courses taken at level 4
            extra_data["l4_gpa"] = "N/A"
            extra_data["l4_band"] = "N/A"
        else:
            final_l4_grade = final_l4_grade_adder_tuples[0] / final_l4_grade_adder_tuples[1]
            extra_data["l4_gpa"] = math_ceil(final_l4_grade / (100/22))
            extra_data["l4_band"] = band_integer_to_band_letter_map[extra_data["l4_gpa"]]
            final_gpa += final_l4_grade * 0.6
        
        if final_l3_grade_adder_tuples[1] == 0: ##no courses taken at level 3
            extra_data["l3_gpa"] = "N/A"
            extra_data["l3_band"] = "N/A"
        else:
            final_l3_grade = final_l3_grade_adder_tuples[0] / final_l3_grade_adder_tuples[1]
            extra_data["l3_gpa"] = math_ceil(final_l3_grade / (100/22))
            extra_data["l3_band"] = band_integer_to_band_letter_map[extra_data["l3_gpa"]]
            final_gpa += final_l3_grade * 0.4
        
        ##calculate final band and final gpa: level3 is worth 40% and level 4 is worth 60%
        extra_data["final_gpa"] = math_ceil(final_gpa / (100/22))
        extra_data["final_band"] = band_integer_to_band_letter_map[extra_data["final_gpa"]]

        return extra_data

    def get_extra_data_course(self, assessments, course):
        extra_data = {}
        results = AssessmentResult.objects.filter(assessment__in=assessments, course=course, student=self).select_related("assessment")
        final_grade = 0
        totals = {}
        for result in results:
            result_assessment = result.assessment
            type = result_assessment.type
            weighting = result_assessment.weighting
            grade = result.grade
            if type not in totals:
                totals[type] = [0, 0]

            if result.preponderance == "NA":
                extra_data[str(result_assessment.id)] = f"{grade}"
            else:
                extra_data[str(result_assessment.id)] = f"{result.preponderance}"
                if result.preponderance == "MV": #if medical void - do not count
                    weighting = 0
                else: #if credit witheld or refused - count as 0
                    grade = 0
            
            totals[type][0] += grade * weighting
            totals[type][1] += weighting

            final_grade += result.grade * result_assessment.weighting / 100
        
        for key, totals in totals.items():
            if totals[1] > 0:
                extra_data[f"{key}_grade"] = f"{totals[0] / totals[1]:.2f}"
            else:
                extra_data[f"{key}_grade"] = "N/A"
        extra_data["final_grade"] = f"{round(final_grade, 2)}"
        
        return extra_data
    
    class Meta:
        ordering = ['current_academic_year']


class Course(UUIDModel):
    code = models.CharField(max_length=11)
    name = models.CharField(max_length=255, null=True)
    academic_year = models.PositiveIntegerField()

    lecturer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="courses_taught")
    lecturer_comment = models.TextField(max_length=500, null=True, blank=True)

    credits = models.PositiveIntegerField()

    assessments = models.ManyToManyField("Assessment", related_name="courses")

    is_taught_now = models.BooleanField(default=True)

    class Meta:
        db_table = 'course'
        constraints = [
            models.UniqueConstraint(fields=['code', 'academic_year'], name='code_year_unique')
        ]
        ordering = ['academic_year']

    def fetch_assessments(self):
        return self.assessments.all()
    
    def __str__(self):
        return (f"{self.name} - {self.academic_year}")
    
    @property
    def verbose_name(self):
        return f"{self.name} - {self.academic_year} ({'currently active' if self.is_taught_now else 'not active'})"
    
    @property
    def level_integer(self):
        return int(self.code[-4])
    
    def get_data_for_table(self, extra_data={}):
        table_data = {
            'code': self.code,
            'name': self.name,
            'academic_year': self.academic_year,
            'lecturer_comment': self.lecturer_comment,
            'credits': self.credits,
            'is_taught_now': self.is_taught_now,
            
            #Extra properties
            # 'average_coursework_data': self.average_coursework_data,
            'page_url': self.page_url,
        }

        if extra_data:
            extra_data = getattr(self, extra_data["method"])(*extra_data["args"])
            table_data.update(extra_data)
        
        return table_data
    
    @property
    def page_url(self):
        return reverse('general:course', args=[self.code, self.academic_year])

    def get_extra_data_student(self, results):
        extra_data = {
            'coursework_avg': [0, 0],
            'exam_avg': [0, 0],
            'final_grade': 0,
        }

        for result in results: ##tally up the averages and the final grade here
            if result.assessment.type == 'E':
                extra_data['exam_avg'][0] += result.grade * result.assessment.weighting
                extra_data['exam_avg'][1] += result.assessment.weighting
            else:
                extra_data['coursework_avg'][0] += result.grade * result.assessment.weighting
                extra_data['coursework_avg'][1] += result.assessment.weighting
            extra_data['final_grade'] += result.grade * result.assessment.weighting / 100

        ##get the averages, and round everything up.
        extra_data['exam_avg'] = round(extra_data['exam_avg'][0] / extra_data['exam_avg'][1], 2) if extra_data["exam_avg"][1] > 0 else "N/A"
        extra_data['coursework_avg'] = round(extra_data['coursework_avg'][0] / extra_data['coursework_avg'][1], 2) if extra_data["coursework_avg"][1] > 0 else "N/A"
        extra_data['final_grade'] = round(extra_data['final_grade'], 2)
        return extra_data

    def get_extra_data_general(self):
        extra_data = {
            'coursework_avg': [0, 0],
            'exam_avg': [0, 0],
            'final_grade': 0,
        }

        assessment_groups = {
            'exam': [],
            'coursework': [],
        }

        assessments = self.assessments.all()
        results = self.results.all()
        for assessment in assessments:
            pass
        len(assessments)
        len(results)

        # for result in results:
        #     pass
        return extra_data
    
class Assessment(UUIDModel):
    name = models.CharField(max_length=255, null=True, blank=True)
    moderation = models.DecimalField(default=1.0, decimal_places=2, max_digits=5)
    weighting = models.IntegerField()

    type_choices = [
        ('C', 'Coursework'),
        ('I', 'Individual Project'),
        ('G', 'Group Project'),
        ('E', 'Exam'),
    ]
    type = models.CharField(choices=type_choices, max_length=1, default='C')

    @property
    def possible_choices(self):
        return [i[0] for i in self.type_choices]

    def __str__(self):
        return f"{self.name}({self.weighting}%)"


#possible lvl 1,2 subjects = [STATS, MATHS, PHYS, PSYCH, CHEM, GEOG, ECON, BIO, CSC, ENG, HIST, POLS]
#when populating courses for a given student: check which years they should have courses in.
#steps - generate some lvl 1 courses, then generate lvl 2 courses, then lvl 3, then lvl 4, then lvl 5
#lvl 1 courses should be 

#steps to moderate a course/assessment.
##lvl 1 - 12 courses, across 3 subjects
##lvl 2 - 12 courses, across 2 or 3 subjects (40,40,40) or (60,60)
##lvl 3 - 8 courses, 1 group project (10x8,40)
##lvl 4 - 8 courses, 1 individual project (10x8, 40)
##lvl 5 - 8 courses, 1 group project (10x8, 60)
##8 courses 1 project
##12 courses
##course_assessments_json = {
#    "CSC101": {
# }



class AssessmentResult(UUIDModel):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="results")
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name="results")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="results")

    grade = models.IntegerField() # 0 - 100

    @property
    def grade_with_weighting(self):
        return round(self.grade * self.assessment.weighting / 100, 2)

    preponderance_choices = [
        ('NA', 'None'),
        ('MV', 'Medical Void'),
        ('CW', 'Credit Witheld'),
        ('CR', 'Credit Refused'),
    ]
    preponderance = models.CharField(choices=preponderance_choices, default='NA', max_length=2)
    # comment = models.TextField(null=True, blank=True)
    date_submitted = models.DateField(auto_now_add=True)
    date_updated = models.DateField(auto_now=True)

    def __str__(self):
        return f'{self.student.full_name} - {self.assessment.name} - {self.grade}%'

class Comment(UUIDModel):
    added_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="comments")

    comment = models.TextField(blank=False, null=False)
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['timestamp']),
        ]
        ordering = ['timestamp']