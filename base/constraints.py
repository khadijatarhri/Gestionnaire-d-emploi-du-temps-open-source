from .domain import Lesson, DomainRoom, DomainTeacherAvailability, DomainHoliday
from optapy import constraint_provider
from optapy.constraint import Joiners, ConstraintFactory
from optapy.score import HardSoftScore
from datetime import time

@constraint_provider
def define_constraints(constraint_factory: ConstraintFactory):
    return [
        # Hard constraints
        room_conflict(constraint_factory),
        teacher_conflict(constraint_factory),
        student_group_conflict(constraint_factory),
        group_subgroup_conflict(constraint_factory),
        room_capacity_constraint(constraint_factory),
        teacher_availability_constraint(constraint_factory),
        holiday_constraint(constraint_factory),
        # Soft constraints
        wednesday_afternoon_constraint(constraint_factory),
        saturday_morning_constraint(constraint_factory),
        cm_morning_constraint(constraint_factory),
        idle_time_minimization(constraint_factory),
    ]

def room_conflict(constraint_factory: ConstraintFactory):
    return constraint_factory.for_each(Lesson) \
            .join(Lesson,
                  Joiners.equal(lambda lesson: lesson.timeslot),
                  Joiners.equal(lambda lesson: lesson.room),
                  Joiners.less_than(lambda lesson: lesson.id)
             ) \
            .penalize("Room conflict", HardSoftScore.ONE_HARD)

def teacher_conflict(constraint_factory: ConstraintFactory):
    return constraint_factory.for_each(Lesson) \
                .join(Lesson,
                      Joiners.equal(lambda lesson: lesson.timeslot),
                      Joiners.equal(lambda lesson: lesson.teacher),
                      Joiners.less_than(lambda lesson: lesson.id)
                ) \
                .penalize("Teacher conflict", HardSoftScore.ONE_HARD)

def student_group_conflict(constraint_factory: ConstraintFactory):
    return constraint_factory.for_each(Lesson) \
            .join(Lesson,
                  Joiners.equal(lambda lesson: lesson.timeslot),
                  Joiners.equal(lambda lesson: lesson.student_group),
                  Joiners.less_than(lambda lesson: lesson.id)
            ) \
            .penalize("Student group conflict", HardSoftScore.ONE_HARD)

def group_subgroup_conflict(constraint_factory: ConstraintFactory):
    return constraint_factory.for_each(Lesson) \
            .join(Lesson,
                  Joiners.equal(lambda lesson: lesson.timeslot),
                  Joiners.equal(lambda lesson: lesson.student_group.split()[0]),  # Assuming group names have a structure like "Group Subgroup"
                  Joiners.less_than(lambda lesson: lesson.id)
            ) \
            .penalize("Group and subgroup conflict", HardSoftScore.ONE_HARD)

def room_capacity_constraint(constraint_factory: ConstraintFactory):
    return constraint_factory.for_each(Lesson) \
            .join(DomainRoom, 
                  Joiners.equal(lambda lesson: lesson.room),
                  Joiners.filtering(lambda lesson, room: lesson.student_count > room.capacity)
            ) \
            .penalize("Room capacity", HardSoftScore.ONE_HARD)

def teacher_availability_constraint(constraint_factory: ConstraintFactory):
    return constraint_factory.for_each(Lesson) \
            .join(DomainTeacherAvailability,
                  Joiners.equal(lambda lesson: lesson.teacher),
                  Joiners.equal(lambda lesson: lesson.timeslot.week),
                  Joiners.filtering(lambda lesson, availability: lesson.timeslot not in availability.available_timeslots)
            ) \
            .penalize("Teacher not available", HardSoftScore.ONE_HARD) \
            .join(DomainTeacherAvailability,
                  Joiners.equal(lambda lesson: lesson.teacher),
                  Joiners.equal(lambda lesson: lesson.timeslot.week),
                  Joiners.filtering(lambda lesson, availability: lesson.timeslot in availability.available_timeslots and availability.availability == 0.5)
            ) \
            .penalize("Teacher not preferable", HardSoftScore.ONE_SOFT) 


def holiday_constraint(constraint_factory: ConstraintFactory):
    return constraint_factory.for_each(Lesson) \
            .join(DomainHoliday,
                  Joiners.equal(lambda lesson: lesson.timeslot.day),
                  Joiners.equal(lambda lesson: lesson.timeslot.week),
                  Joiners.filtering(lambda lesson, holiday: lesson.timeslot.day in holiday.date.strftime("%A"))
            ) \
            .penalize("Holiday", HardSoftScore.ONE_HARD)

def wednesday_afternoon_constraint(constraint_factory: ConstraintFactory):
    return constraint_factory.for_each(Lesson) \
            .filter(lambda lesson: lesson.timeslot.day == "w" and lesson.timeslot.start_time >= time(hour=12)) \
            .penalize("Wednesday afternoon", HardSoftScore.ONE_SOFT)

def saturday_morning_constraint(constraint_factory: ConstraintFactory):
    return constraint_factory.for_each(Lesson) \
            .filter(lambda lesson: lesson.timeslot.day == "sa" and lesson.timeslot.start_time < time(hour=12)) \
            .penalize("Saturday morning", HardSoftScore.ONE_SOFT)

def cm_morning_constraint(constraint_factory: ConstraintFactory):
    return constraint_factory.for_each(Lesson) \
            .filter(lambda lesson: lesson.lesson_type == "CM" and lesson.timeslot.start_time >= time(hour=12)) \
            .penalize("CM in the afternoon", HardSoftScore.ONE_SOFT)

def idle_time_minimization(constraint_factory: ConstraintFactory):
    return constraint_factory.for_each(Lesson) \
            .join(Lesson,
                  Joiners.equal(lambda lesson: lesson.teacher),
                  Joiners.greater_than(lambda lesson: lesson.timeslot),
                  Joiners.less_than(lambda lesson: lesson.id)
            ) \
            .filter(lambda lesson, previous_lesson: (lesson.timeslot.day == previous_lesson.timeslot.day and (lesson.timeslot.start_time - previous_lesson.timeslot.end_time).seconds / 3600.0 > 1)) \
            .penalize("Idle time", HardSoftScore.ONE_SOFT)
