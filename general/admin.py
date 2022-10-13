from django.contrib import admin
from general.models import Student, Course, Assessment, AssessmentResult, User
from django.contrib.auth import admin as auth_admin


@admin.register(User)
class User_Admin(auth_admin.UserAdmin):
    change_password_form = auth_admin.AdminPasswordChangeForm


admin.site.register(Student)
admin.site.register(Course)
admin.site.register(Assessment)
admin.site.register(AssessmentResult)
