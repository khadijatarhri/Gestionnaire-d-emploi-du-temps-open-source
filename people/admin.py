from django.contrib import admin

# Register your models here.
from .models import Tutor, Department, TrainingProgramme

admin.site.register(Tutor)
admin.site.register(Department)
admin.site.register(TrainingProgramme)
