from django.contrib import admin

# Register your models here.
from .models import Group, Day, TimeSlot, Room, TutorModule, TutorAvailability, Course, RoomType, CourseType, Module, Period, Holiday, Schedule
from django.db import models
class TimeSlotAdmin(admin.ModelAdmin):
    # Customize the time format for a specific field
    # For example, if you want to display and input time in 12-hour format
    # you can use '%I:%M %p' where %I is hour in 12-hour format, %M is minute, and %p is AM or PM
    formfield_overrides = {
        models.TimeField: {'input_formats': ['%H:%M']},
    }

admin.site.register(TimeSlot, TimeSlotAdmin)

admin.site.register(Group)
admin.site.register(Day)
admin.site.register(Room)
admin.site.register(TutorModule)
admin.site.register(TutorAvailability)
admin.site.register(Course)
admin.site.register(CourseType)
admin.site.register(RoomType)
admin.site.register(Module)
admin.site.register(Holiday)
admin.site.register(Schedule)
admin.site.register(Period)