from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid
from django.shortcuts import reverse
from exam_board.tools import default_degree_classification_settings_dict
import json
from math import ceil as math_ceil
from exam_board.tools import band_integer_to_band_letter_map, gpa_to_class_converter, update_cumulative_band_credit_totals
from django.core.validators import MaxValueValidator, MinValueValidator

class CommentsForTableMixin():
    @property
    def comments_for_table(self):
        return json.dumps([{
            "comment": comment.comment.replace("\n", ""),
            "added_by": comment.added_by.get_name_verbose,
            "timestamp": comment.timestamp.strftime("%d/%m/%Y %H:%M"),
            "id": str(comment.id),
        } for comment in self.comments.all().select_related('added_by')])

    def add_comment(self, comment, added_by):
        self.comments.create(comment=comment, added_by=added_by)

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
        return json.dumps(list(self.degree_classification_settings.values()))

    def __str__(self):
        return f"{self.year}{'(Active)' if self.is_current else '(Inactive)'}"

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
        return self.get_full_name()


class Student(UUIDModel, CommentsForTableMixin):
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
    }

    @property
    def current_level(self):
        return self.current_academic_year - self.start_academic_year + (1 if not self.is_faster_route else 2)

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
    
    def graduation_info(self):
        current_academic_year = AcademicYear.objects.filter(is_current=True).first().year
        grad_diff = current_academic_year - self.end_academic_year
        if grad_diff > 0:
            return f"Graduated {grad_diff} years ago"
        elif grad_diff == 0:
            return "Due to graduate this academic year."
        else:
            return f"Due to graduate in {abs(grad_diff)} years"
    
    def get_data_for_table(self, extra_data=None):
        table_data = {
            "GUID": self.GUID,
            "name": self.full_name,
            "degree_name": self.degree_name,
            "degree_title": self.degree_title,
            "is_masters": self.is_masters,
            "is_faster_route": self.is_faster_route,
            "current_year": self.current_level_verbose,
            "start_year": self.start_academic_year,
            "end_year": self.end_academic_year,
            "level": self.current_level,

            #extra hidden data
            "page_url": self.page_url,
            "count": 1
        }
        if extra_data:
            extra_data = getattr(self, extra_data["method"])(*extra_data["args"])
            table_data.update(extra_data)
        
        return table_data
    
    def get_data_for_table_json(self, extra_data=None):
        return json.dumps(self.get_data_for_table(extra_data))
    
    def get_extra_data_level_progression(self, course_map):
        extra_data = {
            "progress_to_next_level": "no", #yes, discretionary, no
            "final_band": 0,
            "final_gpa": 0,
            "greater_than_a": 0,
            "greater_than_b": 0,
            "greater_than_c": 0,
            "greater_than_d": 0,
            "greater_than_e": 0,
            "greater_than_f": 0,
            "greater_than_g": 0,
            "greater_than_h": 0,
            "n_credits": 0,
        }

        grade_adder_tuples = [0, 0]
        for course, assessment_results in course_map.items():
            credits = course.credits
            extra_data["n_credits"] += credits
            course_grade = 0
            for expected_assessment_result_tuples in assessment_results:
                assessment, result = expected_assessment_result_tuples
                grade = 0
                if result:
                    grade = min(result.grade + assessment.moderation, 22) #grade capped at 22, with moderation
                else:
                    no_res_counter += 1
                course_grade += round(grade * assessment.weighting / 100, 0) #round to nearest integer, since course grades are integers

            update_cumulative_band_credit_totals(extra_data, credits, course_grade)

            grade_adder_tuples[0] += course_grade * credits
            grade_adder_tuples[1] += credits
        if grade_adder_tuples[1] == 0: ##no courses taken at level 4
            extra_data["final_gpa"] = "N/A"
            extra_data["final_band"] = "N/A"
        else:
            final_gpa = grade_adder_tuples[0] / grade_adder_tuples[1]
            extra_data["final_gpa"] = round(final_gpa, 1)
            extra_data["final_band"] = band_integer_to_band_letter_map[int(round(extra_data["final_gpa"], 0))]

        if final_gpa >= 12:
            extra_data["progress_to_next_level"] = "yes"
        elif final_gpa >= 9:
            extra_data["progress_to_next_level"] = "discretionary"
        
        return extra_data
    
    def get_extra_data_degree_classification(self, degree_classification_settings, masters, lvl3_courses, lvl3_results, lvl4_courses, lvl4_results, lvl5_courses={}, lvl5_results={}):
        extra_data = {
            "class": "N/A",
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
            "n_credits": 0,
        }
        classification_data = extra_data.copy()

        if masters:
            extra_data.update({
                "l5_band": 0,
                "l5_gpa": 0,
                "project_masters": 0,
            })
        

        final_l5_grade_adder_tuples = [0,0]
        final_l4_grade_adder_tuples = [0,0]
        final_l3_grade_adder_tuples = [0,0]
        
        def calculate_level_data(courses, results, grade_adder_tuples, update_greater_than=False, upgrade_to_masters=False):
            for course in courses:
                credits = course.credits
                classification_data["n_credits"] += credits

                expected_assessments = course.assessments.all()
                course_grade = 0
                for assessment in expected_assessments:
                    result = [result for result in results if result.assessment == assessment]
                    grade = 0
                    if result:
                        grade = min(result[0].grade + assessment.moderation, 22) #grade capped at 22, with moderation
                    course_grade += grade * assessment.weighting / 100
                
                if credits == 60:
                    extra_data["project_masters"] = course_grade
                elif credits == 40:
                    if update_greater_than: #if is lvl 4 - means we have a solo project
                        extra_data["project"] = course_grade
                    else:
                        extra_data["team"] = course_grade

                grade_adder_tuples[0] += round(course_grade * credits, 0) #course grades are rounded to 0 decimal places.
                grade_adder_tuples[1] += credits
                
                update_cumulative_band_credit_totals(classification_data, credits, course_grade)
                if update_greater_than and not masters or upgrade_to_masters:
                    update_cumulative_band_credit_totals(extra_data, credits, course_grade)
                    extra_data["n_credits"] += credits
      
            return grade_adder_tuples
        
        final_l5_grade_adder_tuples = calculate_level_data(lvl5_courses, lvl5_results, final_l5_grade_adder_tuples, upgrade_to_masters=True)
        final_l4_grade_adder_tuples = calculate_level_data(lvl4_courses, lvl4_results, final_l4_grade_adder_tuples, update_greater_than=True)
        final_l3_grade_adder_tuples = calculate_level_data(lvl3_courses, lvl3_results, final_l3_grade_adder_tuples)
        final_gpa = 0

        if masters:
            if final_l5_grade_adder_tuples[1] == 0: ##no courses taken at level 4
                extra_data["l5_gpa"] = "N/A"
                extra_data["l5_band"] = "N/A"
            else:
                final_l5_grade = final_l5_grade_adder_tuples[0] / final_l5_grade_adder_tuples[1]
                extra_data["l5_gpa"] = round(final_l5_grade, 1) #round to 1 decimal place since we calculate gpa to 1 decimal place
                extra_data["l5_band"] = band_integer_to_band_letter_map[int(round(final_l5_grade, 0))]
                final_gpa += final_l5_grade * 0.4 ##level 5 is worth 40% of the final gpa for masters students

        if final_l4_grade_adder_tuples[1] == 0: ##no courses taken at level 4
            extra_data["l4_gpa"] = "N/A"
            extra_data["l4_band"] = "N/A"
        else:
            final_l4_grade = final_l4_grade_adder_tuples[0] / final_l4_grade_adder_tuples[1]
            extra_data["l4_gpa"] = round(final_l4_grade, 1) #round to 1 decimal place since we calculate gpa to 1 decimal place
            extra_data["l4_band"] = band_integer_to_band_letter_map[int(round(final_l4_grade, 0))]
            final_gpa += final_l4_grade * (0.6 if not masters else 0.36) #level 4 is worth 60% of the final gpa for undergraduates and 36% for masters students
        
        if final_l3_grade_adder_tuples[1] == 0: ##no courses taken at level 3
            extra_data["l3_gpa"] = "N/A"
            extra_data["l3_band"] = "N/A"
        else:
            final_l3_grade = final_l3_grade_adder_tuples[0] / final_l3_grade_adder_tuples[1]
            extra_data["l3_gpa"] = round(final_l3_grade, 1) #round to 1 decimal place since we calculate gpa to 1 decimal place
            extra_data["l3_band"] = band_integer_to_band_letter_map[int(round(final_l3_grade, 0))]
            final_gpa += final_l3_grade * (0.4 if not masters else 0.24) #level 3 is worth 40% of the final gpa for undergraduates and 24% for masters students
        
        ##calculate final band and final gpa: level3 is worth 40% and level 4 is worth 60%
        if final_gpa == 0:
            extra_data["final_gpa"] = "N/A"
            extra_data["final_band"] = "N/A"
        else:
            classification_data["final_gpa"] = final_gpa
            extra_data["final_gpa"] = round(final_gpa, 1) #round to 1 decimal place since we calculate gpa to 1 decimal place
            extra_data["final_band"] = band_integer_to_band_letter_map[int(round(final_gpa, 0))]
            
            extra_data["class"] = gpa_to_class_converter(classification_data, degree_classification_settings)

        if extra_data["project"] == 0:
            extra_data["project"] = "N/A"
        else:
            extra_data["project"] = band_integer_to_band_letter_map[int(round(extra_data["project"], 0))]
        
        if extra_data["team"] == 0:
            extra_data["team"] = "N/A"
        else:
            extra_data["team"] = band_integer_to_band_letter_map[int(round(extra_data["team"], 0))]
        
        if masters:
            if extra_data["project_masters"] == 0:
                extra_data["project_masters"] = "N/A"
            else:
                extra_data["project_masters"] = band_integer_to_band_letter_map[int(round(extra_data["project_masters"], 0))]

        return extra_data

    def get_extra_data_course(self, assessments, course):
        extra_data = {}
        results = AssessmentResult.objects.filter(assessment__in=assessments, course=course, student=self).select_related("assessment")
        totals = {
            "final": [0, 0]
        }
        for result in results:
            result_assessment = result.assessment
            type = result_assessment.type
            weighting = result_assessment.weighting
            grade = min(result.grade + result_assessment.moderation, 22) #grade capped at 22, with moderation
            if type not in totals:
                totals[type] = [0, 0]

            if result.preponderance == "NA":
                extra_data[str(result_assessment.id)] = grade
            else:
                extra_data[str(result_assessment.id)] = result.preponderance
                if result.preponderance == "MV": #if medical void - do not count, by setting the weighting to 0
                    weighting = 0
                else: #if CR/CW -> credit witheld or refused - count as 0
                    grade = 0
            
            totals[type][0] += grade * weighting
            totals[type][1] += weighting

        all_mv = True
        for key, total_counters in totals.items():
            if total_counters[1] > 0: ##if weighting across a group is > 0 AKA if any of the assessments are NOT medical void.
                extra_data[f"{key}_grade"] = f"{total_counters[0] / total_counters[1]:.2f}"
                totals["final"][0] += total_counters[0]
                totals["final"][1] += total_counters[1]
                all_mv = False
            else:
                extra_data[f"{key}_grade"] = "MV"

        extra_data["final_grade"] = f'{round(totals["final"][0]/totals["final"][1], 2)}' if not all_mv else "MV"
        
        return extra_data
    
    class Meta:
        ordering = ['current_academic_year']


class Course(UUIDModel, CommentsForTableMixin):
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
    
    def get_data_for_table(self, extra_data={}, **kwargs):
        table_data = {
            'code': self.code,
            'name': self.name,
            'academic_year': self.academic_year,
            'lecturer_comment': self.lecturer_comment,
            'credits': self.credits,
            'is_taught_now': self.is_taught_now,
            'course_id': str(self.id),
            
            #Extra properties
            'page_url': self.page_url,
        }

        if "fast_mod" in kwargs:
            table_data["is_moderated"] = self.is_moderated_optimized

        if extra_data:
            extra_data = getattr(self, extra_data["method"])(*extra_data["args"])
            table_data.update(extra_data)
        
        return table_data

    def get_data_for_table_json(self, extra_data=None):
        return json.dumps(self.get_data_for_table(extra_data))
    
    @property
    def page_url(self):
        return reverse('general:course', args=[self.code, self.academic_year])
    
    @property #use this function IF we prefetched the assessments for the whole queryset.
    def is_moderated_optimized(self):
        for assessment in self.assessments.all():
            if assessment.moderation != 0:
                return True
        return False

    @property
    def is_moderated(self):
        return self.assessments.exclude(moderation=0).exists()

    def get_extra_data_student(self, results): #this will return the students personal averages for the course
        ##MV if all stuff are MV
        extra_data = {
            'coursework_avg': [0, 0, True],
            'exam_avg': [0, 0, True],
            'final_grade': [0, 0, True],
            'is_moderated': False,
        }

        for result in results: ##tally up the averages and the final grade here
            if result.assessment.moderation != 0:
                extra_data['is_moderated'] = True

            grade = min(result.grade + result.assessment.moderation, 22) #grade capped at 22, with moderation
            weighting = result.assessment.weighting
            if result.preponderance == "NA":
                extra_data['exam_avg'][2] = False
                extra_data['coursework_avg'][2] = False
                extra_data['final_grade'][2] = False
            else:
                if result.preponderance == "MV":
                    weighting = 0
                else: ##if CR/CW -> credit witheld or refused - count as 0
                    grade = 0

            weighted_grade = grade * weighting

            if result.assessment.type == 'E':
                extra_data['exam_avg'][0] += weighted_grade
                extra_data['exam_avg'][1] += weighting
            else:
                extra_data['coursework_avg'][0] += weighted_grade
                extra_data['coursework_avg'][1] += weighting
            
            extra_data['final_grade'][0] += weighted_grade
            extra_data['final_grade'][1] += weighting

        ##get the averages, and round everything up.
        if extra_data['exam_avg'][2]:
            extra_data['exam_avg'] = "MV"
        else:
            extra_data['exam_avg'] = round(extra_data['exam_avg'][0] / extra_data['exam_avg'][1], 2) if extra_data["exam_avg"][1] > 0 else "N/A"
        if extra_data['coursework_avg'][2]:
            extra_data['coursework_avg'] = "MV"
        else:
            extra_data['coursework_avg'] = round(extra_data['coursework_avg'][0] / extra_data['coursework_avg'][1], 2) if extra_data["coursework_avg"][1] > 0 else "N/A"
        if extra_data['final_grade'][2]:
            extra_data['final_grade'] = "MV"
        else:
            extra_data['final_grade'] = round(extra_data['final_grade'][0] / extra_data['final_grade'][1], 2) if extra_data["final_grade"][1] > 0 else "N/A"
        return extra_data

    def get_extra_data_general(self): ##this will return the cohort averages for the course
        extra_data = {
            'coursework_avg': [0, 0],
            'exam_avg': [0, 0],
            'final_grade': [0, 0],
            'is_moderated': False,
        }

        ##go over every assessment, group by cw and exam
        all_assessments = self.assessments.all()
        all_results = self.results.all()
        for assessment in all_assessments:
            if assessment.moderation != 0:
                extra_data['is_moderated'] = True
            for result in all_results:
                if result.assessment == assessment:
                    grade = min(result.grade + assessment.moderation, 22) #grade capped at 22, with moderation
                    weighting = assessment.weighting
                    if result.preponderance != "NA": ##if the grade has a preponderance - account for that
                        if result.preponderance == "MV":
                            weighting = 0
                        else: ##if CR/CW -> credit witheld or refused - count as 0
                            grade = 0

                    if assessment.type == 'E':
                        extra_data['exam_avg'][0] += grade * weighting
                        extra_data['exam_avg'][1] += weighting
                    else:
                        extra_data['coursework_avg'][0] += grade * weighting
                        extra_data['coursework_avg'][1] += weighting

                    extra_data['final_grade'][0] += grade * weighting
                    extra_data['final_grade'][1] += weighting
        
        ##get the averages, and round everything up.
        extra_data['exam_avg'] = round(extra_data['exam_avg'][0] / extra_data['exam_avg'][1], 2) if extra_data["exam_avg"][1] > 0 else "N/A"
        extra_data['coursework_avg'] = round(extra_data['coursework_avg'][0] / extra_data['coursework_avg'][1], 2) if extra_data["coursework_avg"][1] > 0 else "N/A"
        extra_data['final_grade'] = round(extra_data['final_grade'][0] / extra_data['final_grade'][1], 2) if extra_data["final_grade"][1] > 0 else "N/A"
        return extra_data
    
class Assessment(UUIDModel):
    name = models.CharField(max_length=255, null=True, blank=True)
    weighting = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])

    type_choices = [
        ('C', 'Coursework'),
        ('I', 'Individual Project'),
        ('G', 'Group Project'),
        ('E', 'Exam'),
    ]
    type = models.CharField(choices=type_choices, max_length=1, default='C')

    moderation = models.IntegerField(default=0)
    moderated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    moderation_datetime = models.DateTimeField(null=True, blank=True)

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

    grade = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(22)]) # 0 - 22

    preponderance_choices = [
        ('NA', 'None'),
        ('MV', 'Medical Void'),
        ('CW', 'Credit Witheld'),
        ('CR', 'Credit Refused'),
    ]
    preponderance = models.CharField(choices=preponderance_choices, default='NA', max_length=2)
    date_submitted = models.DateField(auto_now_add=True)
    date_updated = models.DateField(auto_now=True)

    def __str__(self):
        return f'{self.student.full_name} - {self.assessment.name} - {self.grade}/22'

def CommentMixin(related_name_user):
    class Comment_Mixin(UUIDModel):
        added_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name=related_name_user)

        comment = models.TextField(blank=False, null=False)
        timestamp = models.DateTimeField(auto_now=True)

        class Meta:
            indexes = [
                models.Index(fields=['timestamp']),
            ]
            ordering = ['-timestamp']
            abstract = True
        
        def __str__(self):
            return f"{self.added_by} - {self.timestamp} - {self.comment}"
    
    return Comment_Mixin

class StudentComment(CommentMixin(related_name_user="student_comments")):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="comments")

class CourseComment(CommentMixin(related_name_user="course_comments")):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="comments")