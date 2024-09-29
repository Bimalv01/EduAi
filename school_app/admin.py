from django.contrib import admin

from.models import *

# Register your models here.
admin.site.register(school_file),
admin.site.register(Student),
admin.site.register(Feedback)
admin.site.register(Teacher),
admin.site.register(TeacherFeedback)
admin.site.register(TeacherScore)
