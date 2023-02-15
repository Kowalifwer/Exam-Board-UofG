from django.contrib import admin
from general.models import Student, Course, Assessment, AssessmentResult, User, AcademicYear, StudentComment, CourseComment, LevelHead
from django.contrib.auth import admin as auth_admin
from django.db import connection, reset_queries
from django.utils.safestring import mark_safe

@admin.register(User)
class User_Admin(auth_admin.UserAdmin):
    change_password_form = auth_admin.AdminPasswordChangeForm

class CourseCommentInline(admin.TabularInline):
    model = CourseComment
    extra = 0

@admin.register(Course)
class Course_Admin(admin.ModelAdmin):
    list_display = ('code', 'name', 'credits', 'academic_year')
    list_filter = ('academic_year', 'credits')
    search_fields = ('code', 'academic_year')
    exclude = ('assessments',)
    readonly_fields = ('assessment_data',)
    inlines = [CourseCommentInline]

    def assessment_data(self, obj):
        return mark_safe('<br>'.join([str(assessment) for assessment in obj.assessments.all().order_by('weighting')]))

#create StudentComment inline
class CommentInline(admin.TabularInline):
    model = StudentComment
    extra = 0

@admin.register(Student)
class Student_Admin(admin.ModelAdmin):
    list_display = ('GUID', 'full_name', 'degree_title', 'current_academic_year', 'is_faster_route', 'is_masters', 'start_academic_year', 'end_academic_year')
    list_filter = ('degree_title', 'current_academic_year', 'start_academic_year', 'end_academic_year', 'is_faster_route', 'is_masters')
    search_fields = ('GUID', 'full_name', 'degree_title')
    readonly_fields = ('course_data',)
    exclude = ('courses',)
    inlines = [CommentInline]

    def course_data(self, obj):
        # return ""
        final_string = ""
        courses = obj.courses.all().order_by('academic_year').prefetch_related('assessments')
        total_credits = 0
        current_year = -1
        for course in courses:
            # results = course.results.all()
            if current_year != course.academic_year:
                current_year = course.academic_year
                final_string += f"<br>YEAR: {course.academic_year}<br><br>"
            total_credits += course.credits
            final_string += f"{course.code} - {course.name} ({course.academic_year}) - {course.credits}<br>"
            # final_string += f"Number of results: {len(results)}<br>"
        final_string += f"<br>Total credits: {total_credits}"
        return mark_safe(final_string)

# @admin.register(Assessment)
class Assessment_Admin(admin.ModelAdmin):
    list_display = ('name', 'weighting')
    list_filter = ('name',)
    search_fields = ('name', 'course')

@admin.register(AssessmentResult)
class AssessmentResult_Admin(admin.ModelAdmin):
    list_display = ('student', 'course', 'assessment', 'grade', 'preponderance')
    list_filter = ('assessment__type', 'course__academic_year', 'preponderance')
    search_fields = ('student__full_name', 'course__code', 'student__GUID')
    list_select_related = ('student', 'course', 'assessment')

#register default models with all fields
admin.site.register(AcademicYear)
admin.site.register(StudentComment)
admin.site.register(Assessment)
admin.site.register(LevelHead)