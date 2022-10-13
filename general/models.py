from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
class AcademicYearSettings(models.Model):
    level1_total_credits = models.IntegerField(default=120)
    level2_total_credits = models.IntegerField(default=120)
    level3_total_credits = models.IntegerField(default=120)
    level4_total_credits = models.IntegerField(default=120)
    level5_total_credits = models.IntegerField(default=120)


class AcademicYear(models.Model):
    year = models.IntegerField(unique=True)
    is_current = models.BooleanField(default=True)  # TODO: Ensure that only 1 year is current at a time
    settings = models.ForeignKey(AcademicYearSettings, null=True, blank=True, on_delete=models.SET_NULL)


class User(AbstractUser):
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


class Student(models.Model):
    GUID = models.CharField(max_length=8, unique=True)
    full_name = models.CharField(max_length=225)
    degree_title = models.CharField(max_length=100)

    level_choices = [
        (0, 'No levels'),
        (1, 'Level 1'),
        (2, 'Level 2'),
        (3, 'Level 3'),
        (4, 'Level 4'),
        (5, 'Level 5(M)'),
        (6, 'PhD'),
        (7, 'PostDoc'),
    ]

    degree_level = models.IntegerField(choices=level_choices, default=4)
    is_faster_route = models.BooleanField()
    start_academic_year = models.IntegerField()
    end_academic_year = models.IntegerField()
    current_academic_year = models.IntegerField(default=AcademicYear.objects.get(is_current=True).year)  # TODO: possibly make this a foreign key relationship.

    comment = models.TextField(max_length=1000, null=True, blank=True)

    @property
    def current_level_verbose(self):  # TODO Fix this, by taking current month into consideration (2022-2023 might still be first_year but calculation will return second_year). Also consider is_faster year.
        return self.level_choices[self.current_academic_year - self.start_academic_year + 1][1]

    @property
    def is_masters(self):
        return self.degree_level == 5

    @property
    def matriculation_number(self):
        return int(self.GUID[:-1]) if self.GUID[-1].isalpha() else int(self.GUID)

    def __str__(self):
        return self.matriculation_with_letter


class Course(models.Model):
    code = models.CharField(max_length=11)
    name = models.CharField(max_length=255, null=True)
    academic_year = models.PositiveIntegerField()
    # description = models.CharField(max_length=255, null=True, blank=True)

    lecturer = models.ForeignKey('User', on_delete=models.SET_NULL, blank=True, null=True)
    lecturer_comment = models.TextField(max_length=500, null=True, blank=True)

    credits = models.PositiveIntegerField()

    is_taught_now = models.BooleanField(default=True)
    enrolled_students = models.ManyToManyField(Student, blank=True, related_name="course_student_m2m")

    class Meta:
        db_table = 'course'
        constraints = [
            models.UniqueConstraint(fields=['code', 'academic_year'], name='code_year_unique')
        ]

    def __str__(self):
        return (self.code + " - " + str(self.academic_year))

    def fetch_assessments(self):
        return self.assessments.all()


class Assessment(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="assessments")

    moderation = models.DecimalField(default=1.0, decimal_places=2, max_digits=5)
    weighting = models.IntegerField()

    type_choices = [
        ('A', 'Assignment'),
        ('E', 'Exam'),
    ]
    type = models.CharField(choices=type_choices, max_length=1, default='A')

    def __str__(self):
        return self.course.name + '- ' + self.start_date


class AssessmentResult(models.Model):
    assessment = models.ForeignKey(Assessment, on_delete=models.SET_NULL, related_name="results", null=True, blank=True)
    student = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True, blank=True, related_name="results")

    grade_mark = models.IntegerField()
    preponderance_choices = [
        ('NA', 'None'),
        ('MV', 'Medical Void'),
        ('CW', 'Credit Witheld'),
        ('CR', 'Credit Refused'),
    ]
    preponderance = models.CharField(choices=preponderance_choices, default='NA', max_length=2)

    comment = models.TextField()

    start_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f'{self.assignment.course.name} - {self.start_date}'


class Comment(models.Model):
    subject = models.CharField(max_length=100)
    comment = models.TextField(blank=False, null=False)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)


class DegreeClassification(models.Model):
    classification_name = models.CharField(max_length=255)
    lower_GPA_standard = models.FloatField()
    lower_GPA_discretionary = models.FloatField()
    percentage_above_for_discretionary = models.IntegerField(default=50)
    char_band_for_discretionary = models.CharField(max_length=5)

    def __str__(self):
        return self.classification_name
