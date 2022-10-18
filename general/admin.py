from django.contrib import admin
from general.models import Student, Course, Assessment, AssessmentResult, User, AcademicYear
from django.contrib.auth import admin as auth_admin

@admin.register(User)
class User_Admin(auth_admin.UserAdmin):
    change_password_form = auth_admin.AdminPasswordChangeForm

@admin.register(Course)
class Course_Admin(admin.ModelAdmin):
    list_display = ('code', 'name', 'credits', 'academic_year')
    list_filter = ('code', 'academic_year', 'credits')
    search_fields = ('code', 'academic_year')

@admin.register(Student)
class Student_Admin(admin.ModelAdmin):
    list_display = ('GUID', 'full_name', 'degree_title', 'current_academic_year', 'is_faster_route', 'is_masters', 'start_academic_year', 'end_academic_year')
    list_filter = ('degree_title', 'current_academic_year', 'start_academic_year', 'end_academic_year', 'is_faster_route', 'is_masters')
    search_fields = ('GUID', 'full_name', 'degree_title')

@admin.register(Assessment)
class Assessment_Admin(admin.ModelAdmin):
    list_display = ('name', 'weighting')
    list_filter = ('name',)
    search_fields = ('name', 'course')

@admin.register(AssessmentResult)
class AssessmentResult_Admin(admin.ModelAdmin):
    list_display = ('student', 'course', 'assessment', 'grade', 'preponderance')
    list_filter = ('assessment__type', 'course__academic_year', 'assessment', 'preponderance')
    search_fields = ('student__full_name', 'course__code')

#register default models with all fields
admin.site.register(AcademicYear)
