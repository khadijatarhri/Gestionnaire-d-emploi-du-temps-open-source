from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from people.models import Tutor, Department,TrainingProgramme

from django.db import models


class Group(models.Model):
    name = models.CharField(max_length=50)
    train_prog = models.ForeignKey(TrainingProgramme, on_delete=models.CASCADE, null=True, blank=True)
    size = models.PositiveSmallIntegerField(null=True, blank=True)
    parent_groups = models.ManyToManyField('self', symmetrical=False, blank=True, related_name="children_groups")

    def __str__(self):
        return self.name

class Day(models.Model):
    day = models.CharField(max_length=2, choices=[('m', 'Monday'), ('tu', 'Tuesday'), ('w', 'Wednesday'), ('th', 'Thursday'), ('f', 'Friday'), ('sa', 'Saturday')], null=True, blank=True)

    def __str__(self):
        return self.day

class TimeSlot(models.Model):
    day = models.ForeignKey(Day, on_delete=models.CASCADE, null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.day} {self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')}"

class RoomType(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name

class Room(models.Model):
    name = models.CharField(max_length=20, null=True, blank=True)
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE, null=True, blank=True)
    capacity = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return self.name

class CourseType(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Module(models.Model):
    name = models.CharField(max_length=100)
    abbrev = models.CharField(max_length=10, verbose_name='Intitulé abbrégé')
    tutor_head=models.ForeignKey(Tutor, on_delete=models.CASCADE, null=True, blank=True) #added this also
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True)
    training_program = models.ForeignKey(TrainingProgramme, on_delete=models.CASCADE, null=True, blank=True)# i added this 

    def __str__(self):
        return self.name

class TutorModule(models.Model):
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE)
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    period = models.ForeignKey('Period', on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        unique_together = ('tutor', 'module', 'period')


# Preferences Models
class TutorAvailability(models.Model):
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE)
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    week = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(53)], null=True, blank=True)
    availability = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(1)], default=1)

    def __str__(self):
        return f"{self.tutor.username} - {self.time_slot} - {self.availability}"




class Course(models.Model):
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE, null=True, blank=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True)
    year = models.PositiveSmallIntegerField(null=True, blank=True)
    type = models.ForeignKey(CourseType, on_delete=models.CASCADE, null=True, blank=True)
    module = models.ForeignKey(Module, on_delete=models.CASCADE, null=True, blank=True)
    #i should add the training program : like gl 2a for exemple !don't need it here 

    def __str__(self):
        return f"{self.module} - {self.type} - {self.group}"

class Period(models.Model):
    name = models.CharField(max_length=20)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True)
    starting_week = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(53)], null=True, blank=True)
    ending_week = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(53)], null=True, blank=True)

    def __str__(self):
        return self.name

class Holiday(models.Model):
    day = models.ForeignKey('Day', on_delete=models.CASCADE)
    week = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(53)])
    year = models.PositiveSmallIntegerField()

class Schedule(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE, null=True, blank=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, null=True, blank=True)
    week = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(52)], blank=True, null=True)
    # adding the training program
    training_program = models.ForeignKey(TrainingProgramme, on_delete=models.CASCADE, null=True, blank=True, related_name='+')
    def __str__(self):
        return f"Week {self.week}: {self.course} in {self.room} at {self.time_slot}"

class Message(models.Model):
    sender = models.ForeignKey(Tutor, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(Tutor, related_name='received_messages', on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    body = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    related_course = models.ForeignKey(Schedule, null=True, blank=True, on_delete=models.SET_NULL)
    is_confirmation = models.BooleanField(default=False)
    confirmation_link = models.CharField(max_length=255, null=True, blank=True)
    decline_link = models.CharField(max_length=255, null=True, blank=True)
    
    def __str__(self):
        return self.subject

