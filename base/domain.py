
# domain.py
from optapy import problem_fact, planning_entity, planning_id, planning_solution, planning_variable, value_range_provider, problem_fact_collection_property, planning_entity_collection_property, planning_score
from optapy.score import HardSoftScore

from optapy import planning_solution, planning_entity_collection_property, \
                   problem_fact_collection_property, \
                   value_range_provider, planning_score

from datetime import time

from .models import Course, TimeSlot, Room, TutorAvailability, Holiday

@problem_fact
class DomainRoom:
    def __init__(self, id, name, capacity):
        self.id = id
        self.name = name
        self.capacity = capacity

    @planning_id
    def get_id(self):
        return self.id

    def __str__(self):
        return f"Room(id={self.id}, name={self.name}, capacity={self.capacity})"

@problem_fact
class DomainTimeslot:
    def __init__(self, id, day, start_time, end_time):
        self.id = id
        self.day = day
        self.start_time = start_time
        self.end_time = end_time

    @planning_id
    def get_id(self):
        return self.id

    def __str__(self):
        return f"Timeslot(id={self.id}, day={self.day}, start_time={self.start_time}, end_time={self.end_time})"

@planning_entity
class Lesson:
    def __init__(self, id, subject, teacher, student_group, student_count, lesson_type, timeslot=None, room=None):
        self.id = id
        self.subject = subject
        self.teacher = teacher
        self.student_group = student_group
        self.student_count = student_count
        self.lesson_type = lesson_type
        self.timeslot = timeslot
        self.room = room

    @planning_id
    def get_id(self):
        return self.id

    @planning_variable(DomainTimeslot, ["domaintimeslotRange"])
    def get_timeslot(self):
        return self.timeslot

    def set_timeslot(self, new_timeslot):
        self.timeslot = new_timeslot

    @planning_variable(DomainRoom, ["domainroomRange"])
    def get_room(self):
        return self.room

    def set_room(self, new_room):
        self.room = new_room

    def __str__(self):
        return (
            f"Lesson("
            f"id={self.id}, "
            f"timeslot={self.timeslot}, "
            f"room={self.room}, "
            f"teacher={self.teacher}, "
            f"subject={self.subject}, "
            f"student_group={self.student_group}, "
            f"student_count={self.student_count}, "
            f"lesson_type={self.lesson_type}"
            f")"
        )

@problem_fact
class DomainTeacherAvailability:
    def __init__(self, teacher, week, available_timeslots, availability):
        self.teacher = teacher
        self.week = week
        self.available_timeslots = available_timeslots
        self.availability = availability
@problem_fact
class DomainHoliday:
    def __init__(self, day, week, year):
        self.day = day
        self.week = week
        self.year = year





@planning_solution
class TimeTable:
    def __init__(self, timeslot_list, room_list, lesson_list, teacher_availability_list, holiday_list, score=None):
        self.timeslot_list = timeslot_list
        self.room_list = room_list
        self.lesson_list = lesson_list
        self.teacher_availability_list = teacher_availability_list
        self.holiday_list = holiday_list
        self.score = score

    @problem_fact_collection_property(DomainTimeslot)
    @value_range_provider(range_id = "domaintimeslotRange")
    def get_timeslot_list(self):
        return self.timeslot_list

    @problem_fact_collection_property(DomainRoom)
    @value_range_provider(range_id = "domainroomRange")
    def get_room_list(self):
        return self.room_list

    @planning_entity_collection_property(Lesson)
    def get_lesson_list(self):
        return self.lesson_list

    @problem_fact_collection_property(DomainTeacherAvailability)
    def get_teacher_availability_list(self):
        return self.teacher_availability_list

    @problem_fact_collection_property(DomainHoliday)
    def get_holiday_list(self):
        return self.holiday_list

    @planning_score(HardSoftScore)
    def get_score(self):
        return self.score

    def set_score(self, score):
        self.score = score

    def __str__(self):
        return (
            f"TimeTable("
            f"timeslot_list={self.timeslot_list},\n"
            f"room_list={self.room_list},\n"
            f"lesson_list={self.lesson_list},\n"
            f"teacher_availability_list={self.teacher_availability_list},\n"
            f"holiday_list={self.holiday_list},\n"
            f"score={str(self.score.toString()) if self.score is not None else 'None'}"
            f")"
        )

def generate_problem(week):

        timeslot_list = [
            DomainTimeslot(
                timeslot.id,
                timeslot.day,
                timeslot.start_time,
                timeslot.end_time,
            )
            for timeslot in TimeSlot.objects.all()
        ]
    
        room_list = [
            DomainRoom(
                room.id,
                room.name,
                room.capacity
            )
            for room in Room.objects.all()
        ]
    
        lesson_list = [
            Lesson(
                course.id,
                course.module.name,
                course.tutor.last_name,
                course.group.name,
                course.group.size,
                course.type.name
            )
            for course in Course.objects.all()
        ]
    
        teacher_availability_list = [
            DomainTeacherAvailability(
                availability.tutor,
                week,
                [
                    DomainTimeslot(
                        ts.id,
                        ts.day.day,
                        ts.start_time,
                        ts.end_time,
                        week
                    )
                    for ts in TimeSlot.objects.filter(id=availability.time_slot.id)
                ],
                availability.availability
            )
            for availability in TutorAvailability.objects.filter(week=week)
        ]
    
        holiday_list = [
            DomainHoliday(
                holiday.day,
                holiday.week,
                holiday.year
            )
            for holiday in Holiday.objects.filter(week=week)
        ]

   
        return TimeTable(timeslot_list, room_list, lesson_list, teacher_availability_list, holiday_list)

