from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid
from django.shortcuts import reverse
from exam_board.tools import default_degree_classification_settings_dict
import json

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

    @property
    def is_classhead(self):
        return self.level > 0

    def __str__(self):
        return self.username


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

    def get_extra_data_course(self, assessments, course):
        extra_data = {}
        results = AssessmentResult.objects.filter(assessment__in=assessments, course=course, student=self).select_related("assessment")
        final_grade = 0
        totals = {}
        for result in results:
            result_assessment = result.assessment
            if result_assessment.type not in totals:
                totals[result_assessment.type] = [0, 0]
            totals[result_assessment.type][0] += result.grade * result_assessment.weighting
            totals[result_assessment.type][1] += result_assessment.weighting
            extra_data[str(result_assessment.id)] = f"{result.grade}" 
            final_grade += result.grade * result_assessment.weighting / 100
        
        for key, totals in totals.items():
            if totals[1] > 0:
                extra_data[f"{key}_grade"] = f"{totals[0] / totals[1]:.2f}"
        extra_data["final_grade"] = f"{round(final_grade, 2)}"
        
        return extra_data
    
    class Meta:
        ordering = ['current_academic_year']


class Course(UUIDModel):
    code = models.CharField(max_length=11)
    name = models.CharField(max_length=255, null=True)
    academic_year = models.PositiveIntegerField()

    lecturer_comments = models.TextField(max_length=500, null=True, blank=True)

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
    
    def get_data_for_table(self, extra_data={}):
        table_data = {
            'code': self.code,
            'name': self.name,
            'academic_year': self.academic_year,
            'lecturer_comments': self.lecturer_comments,
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
    comment = models.TextField(null=True, blank=True)
    date_submitted = models.DateField(auto_now_add=True)
    date_updated = models.DateField(auto_now=True)

    def __str__(self):
        return f'{self.student.full_name} - {self.assessment.name} - {self.grade}%'

class Comment(UUIDModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="comments")
    comment = models.TextField(blank=False, null=False)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
