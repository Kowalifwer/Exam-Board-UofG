from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid
from django.shortcuts import reverse
from exam_board.tools import default_degree_classification_settings, default_level_progression_settings
import json
from math import ceil as math_ceil
from exam_board.tools import band_integer_to_band_letter_map, gpa_to_class_converter, gpa_to_progression_converter, update_cumulative_band_credit_totals
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.safestring import mark_safe

#Mixins
class CommentsForTableMixin():
    """Mixin for models that have Comment objects associated with them. Adds means to get comments for table and add comments to the model."""
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

def CommentMixin(related_name_user):
    """Returns a mixin that can be used to add comments to a model. The mixin will have a ForeignKey to the User model.
    :param related_name_user: The related name for the ForeignKey to the User model. (e.g. 'comments')
    """
    class Comment_Mixin(UUIDModelMixin):
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

class UUIDModelMixin(models.Model):
    """Abstract model that sets the table's id field to a UUID. This is to be used for all models that need an id/primary key."""
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)

    class Meta:
        abstract = True

class AcademicYear(UUIDModelMixin):
    """Model for an academic year. This is used to store the settings for the year, such as the degree classification settings and level progression settings.
    Currently, the default degree classification and level progression settings are stored in general/tools.py
    """
    year = models.IntegerField(unique=True)
    is_current = models.BooleanField(default=True)
    degree_classification_settings = models.JSONField(null=False, blank=False, default=default_degree_classification_settings)
    level_progression_settings = models.JSONField(null=False, blank=False, default=default_level_progression_settings)
    
    def save(self, *args, **kwargs): #on-save constraint that ensures that there can only be one is_current=true year at a time
        if self.is_current and AcademicYear.objects.filter(is_current=True).exists():
            raise Exception("There can only be one is_current=True academic year at a time.")
        super().save(*args, **kwargs)

    @property
    def degree_classification_settings_for_table(self):
        return json.dumps(self.degree_classification_settings)

    def level_progression_settings_for_table(self, level):
        return json.dumps(self.level_progression_settings[level])

    def __str__(self):
        return str(self.year)

class LevelHead(UUIDModelMixin):
    """Model for keeping track of level heads. A given academic year can be allocated up to 1 level head for each level."""
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='level_head')
    academic_year = models.ForeignKey('AcademicYear', on_delete=models.CASCADE, related_name='level_heads')

    level_choices = [
        (1, 'Level 1'),
        (2, 'Level 2'),
        (3, 'Level 3'),
        (4, 'Level 4'),
        (5, 'Level 5'),
    ]
    level = models.IntegerField(choices=level_choices, default=0)

    def __str__(self):
        return f"{self.user.get_name_verbose} - {self.academic_year.year}"

    def save(self, *args, **kwargs):
        if self.filter(level=self.level, academic_year=self.academic_year).exists():
            raise Exception("There can only be one level head for every level in a given academic year.")
        super().save(*args, **kwargs)

class User(AbstractUser, UUIDModelMixin):
    """Model for users. It extends the default user model to add a title field. More fields and functionality can be added here.
    """
    title = models.CharField(max_length=20, blank=True, null=True)
    
    @property
    def get_name_verbose(self):
        """Returns the full name of the user, with the title if it exists."""
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

class Student(UUIDModelMixin, CommentsForTableMixin):
    """Model for University of Glasgow students. It stores all the information about a student, such as their GUID, full_name, degree inforation, and more..."""

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
    def current_level_verbose(self):
        return self.level_choices.get(self.current_level, "N/A")

    @property
    def matriculation_number(self): #returns the number only part of the GUID
        return int(self.GUID[:-1]) if self.GUID[-1].isalpha() else int(self.GUID)

    def __str__(self):
        return f"{self.GUID} - {self.full_name}"
    
    @property
    def page_url(self):
        """Returns the url for the individual student view."""
        return reverse('general:student', args=[self.GUID])

    def graduation_difference_from_now(self, current_academic_year):
        """Returns the difference between the current academic year and the end academic year of the student."""
        return current_academic_year - self.end_academic_year
    
    def graduation_info(self):
        """Returns a string with information about the student's graduation status and a link to the cohort in which they have graduated."""
        current_academic_year = AcademicYear.objects.filter(is_current=True).first().year
        graduation_difference_from_now = self.graduation_difference_from_now(current_academic_year)
        link_to_relevant = reverse('general:degree_classification_exact', args=[5 if self.is_masters else 4, self.end_academic_year])
        if graduation_difference_from_now > 0:
            return mark_safe(f"Graduated {graduation_difference_from_now} years ago. <br><a href='{link_to_relevant}'>View graduation cohort</a>")
        elif graduation_difference_from_now == 0:
            return mark_safe(f"Due to graduate this academic year. <br><a href='{link_to_relevant}'>View graduation cohort</a>")
        else:
            link_to_relevant = reverse('general:level_progression_exact', args=[self.current_level, self.end_academic_year])
            return mark_safe(f"Due to graduate in {abs(graduation_difference_from_now)} years. <br><a href='{link_to_relevant}'>View graduation cohort</a>")
    
    def get_data_for_table(self, extra_data: dict=None):
        """Returns relevant data about the student object. Mostly used for tables.
        :param extra_data: An optional dictionary that can be used to fetch additional information about the model object, where necessary.
        :example use: obj.get_data_for_table(extra_data={"get_extra_data_FOO": [1, 2, 3]})
        :This will call the "get_extra_data_FOO" method with the arguments [1, 2, 3]
        :note that for this to work, the method MUST be defined within this model class.
        :return dict: A dictionary of data that can be used to populate a table.
        """
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
            for method, args in extra_data.items():
                ##This will call the method with the given arguments, and update the table_data dictionary with the new data.
                table_data.update(getattr(self, method)(*args))
        
        return table_data
    
    def get_data_for_table_json(self, extra_data=None):
        """Returns the data for the table in JSON format."""
        return json.dumps(self.get_data_for_table(extra_data))
    
    ###METHODS FOR EXTRA TABLE DATA FETCHING###
    def get_extra_data_level_progression(self, level_progression_rules, course_map):
        """Returns extra data for the level progression table.
        :param level_progression_rules: A dictionary of level progression rules. Structure can be found in the AcademicYear model, level_progression_settings field.
        :param course_map: A dictionary of courses and their assessment results. Has the following structure: {
            course: [(assessment, assessment_result), (assessment, assessment_result)...]
        }
        :return dict: A dictionary of extra data."""
        
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

        extra_data["progress_to_next_level"] = gpa_to_progression_converter(extra_data["final_gpa"], level_progression_rules)
        
        return extra_data
    
    def get_extra_data_degree_classification(self, degree_classification_settings, masters, lvl3_courses, lvl3_results, lvl4_courses, lvl4_results, lvl5_courses={}, lvl5_results={}):
        """Returns extra data for the degree classification table.
        :param degree_classification_settings: A dictionary of degree classification settings. Structure can be found in the AcademicYear model, degree_classification_settings field.
        :param masters: A boolean indicating whether this is a masters degree classification.
        :param lvl3_courses: A list of all level 3 courses, for the given student and academic year.
        :param lvl3_results: A list of all level 3 results, for the given student and academic year.
        :param lvl4_courses: A list of all level 4 courses, for the given student and academic year.
        :param lvl4_results: A list of all level 4 results, for the given student and academic year.
        :param lvl5_courses: A list of all level 5 courses, for the given student and academic year.
        :param lvl5_results: A list of all level 5 results, for the given student and academic year.
        :return dict: A dictionary of extra data."""

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
        classification_data = extra_data.copy() #used to calculate the class. key difference is it stores data across all levels, rather than just the final level.

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
            """Calculates the subset of data for a given level within the degree classification table and updates the state of extra_data dict, as well as the grade adder tuples.
            :param courses: A list of courses.
            :param results: A list of results.
            :param grade_adder_tuples: A tuple that keeps track of the total grade and total number of credits (float: total_grade, int: total_credits).
            :param update_greater_than: A boolean indicating whether to update the greater_than fields.
            :param upgrade_to_masters: A boolean indicating whether to upgrade the degree classification to masters."""

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
                
                update_cumulative_band_credit_totals(classification_data, credits, course_grade) ##classification data needs to account for all the honors levels
                if update_greater_than and not masters or upgrade_to_masters: ##table data only shows the greater_than fields for the final year of study
                    update_cumulative_band_credit_totals(extra_data, credits, course_grade)
                    extra_data["n_credits"] += credits
      
            return grade_adder_tuples
        
        final_l5_grade_adder_tuples = calculate_level_data(lvl5_courses, lvl5_results, final_l5_grade_adder_tuples, upgrade_to_masters=True)
        final_l4_grade_adder_tuples = calculate_level_data(lvl4_courses, lvl4_results, final_l4_grade_adder_tuples, update_greater_than=True)
        final_l3_grade_adder_tuples = calculate_level_data(lvl3_courses, lvl3_results, final_l3_grade_adder_tuples)
        final_gpa = 0

        if masters:
            if final_l5_grade_adder_tuples[1] == 0: ##no courses taken at level 5
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
            extra_data["project"] = round(extra_data["project"], 1)
        
        if extra_data["team"] == 0:
            extra_data["team"] = "N/A"
        else:
            extra_data["team"] = round(extra_data["team"], 1)
        
        if masters:
            if extra_data["project_masters"] == 0:
                extra_data["project_masters"] = "N/A"
            else:
                extra_data["project_masters"] = round(extra_data["project_masters"], 1)

        return extra_data

    def get_extra_data_course(self, assessments, course):
        """Provides additional data of the student, with regards to a given course, including the student's grade across all assessed work, preponderance, and credits.
        :param assessments: The assessments the student is taking
        :param course: The course the student is taking
        :return dict: The extra data
        """
        extra_data = {}
        results = AssessmentResult.objects.filter(assessment__in=assessments, course=course, student=self).select_related("assessment")
        totals = {
            "final": [0, 0]
        }
        ##the idea is that we store the total grade and the total weighting for each type/group of assessment
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


class Course(UUIDModelMixin, CommentsForTableMixin):
    """This is the model that represents a course table, and is used to store information about the course, such as the code, name, academic year, lecturer, credits, and any assessed content."""
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
        """Returns some information about the course object. Mostly used for tables.
        :param extra_data: An optional dictionary that can be used to fetch additional information about the model object, where necessary.
        :param kwargs: Any additional arguments that cause small changes to the data.
        :example use: obj.get_data_for_table(extra_data={"get_extra_data_FOO": [1, 2, 3]})
        :This will call the "get_extra_data_FOO" method with the arguments [1, 2, 3]
        :note that for this to work, the method MUST be defined within this model class.
        :return: A dictionary of data that can be used to populate a table.
        """
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

        if "assessments_prefetched" in kwargs: #if we prefetched the assessments for the whole queryset - we can figure out if the course is moderated without making a query for this obejct.
            table_data["is_moderated"] = self.is_moderated_optimized

        if extra_data: 
            for method, args in extra_data.items():
                ##This will call the method with the given arguments, and update the table_data dictionary with the new data.
                table_data.update(getattr(self, method)(*args))
        
        return table_data

    def get_data_for_table_json(self, extra_data=None):
        return json.dumps(self.get_data_for_table(extra_data))
    
    @property
    def page_url(self):
        """Returns the url for the individual course view."""
        return reverse('general:course', args=[self.code, self.academic_year])
    
    @property
    def is_moderated_optimized(self):
        """A faster way to check if a course is moderated. Requires that all the assessments for the course are prefetched"""
        for assessment in self.assessments.all():
            if assessment.moderation != 0:
                return True
        return False

    @property
    def is_moderated(self):
        return self.assessments.exclude(moderation=0).exists()

    ###Extra data methods###
    def get_extra_data_student(self, results):
        """Provides additional data for a given students performance, such as the student's grade across all assessed work, or any perponderances.
        :param assessments: The assessments the student is taking
        :param course: The course the student is taking
        :return dict: The extra data
        """

        extra_data = { #the value list tracks [total_grade, total_weighting, all_grades_are_preponderanced]
            'coursework_avg': [0, 0, True],
            'exam_avg': [0, 0, True],
            'final_grade': [0, 0, True],
            'is_moderated': False, #this is used to determine if the course is moderated, and if so, to display the moderation column.
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

    def get_extra_data_general(self):
        """Returns the average cohort perforamnce (grades), and tracks whether the course is moderated or not."""
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
    
class Assessment(UUIDModelMixin):
    """An Assessment is a single piece of coursework or exam. Assessments can be linked to the Course table, and have a weighting/100. 
    \nAssessments can also be moderated (between -6 and +6 bands)."""
    name = models.CharField(max_length=255, null=True, blank=True)
    weighting = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])

    type_choices = [
        ('C', 'Coursework'),
        ('I', 'Individual Project'),
        ('G', 'Group Project'),
        ('E', 'Exam'),
    ]
    type = models.CharField(choices=type_choices, max_length=1, default='C')

    moderation = models.IntegerField(default=0, validators=[MinValueValidator(-6), MaxValueValidator(6)])
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

class AssessmentResult(UUIDModelMixin):
    """An AssessmentResult is a single result for a student on a given assessment."""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="results")
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name="results")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="results")

    grade = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(22)]) #0 - 22 scale

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

class StudentComment(CommentMixin(related_name_user="student_comments")):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="comments")

class CourseComment(CommentMixin(related_name_user="course_comments")):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="comments")