from base.models import Day, TimeSlot, RoomType, Room, CourseType, Group, Module, Tutor, TutorModule, Course, Period
from people.models import Department, TrainingProgramme, Tutor

# Create Days
days = ["m", "tu", "w", "th", "f", "sa"]
day_objects = {day: Day.objects.create(day=day) for day in days}

# Create TimeSlots
time_slots = [
    ("08:00", "10:00"),
    ("10:00", "12:00"),
    ("13:00", "15:00"),
    ("15:00", "17:00")
]
for day, day_obj in day_objects.items():
    for start_time, end_time in time_slots:
        TimeSlot.objects.create(day=day_obj, start_time=start_time, end_time=end_time)

# Create Room Types
lecture_room = RoomType.objects.create(name="Lecture Room")

# Create Rooms
Room.objects.create(name="Room 101", room_type=lecture_room, capacity=30)

# Create Course Types
cm_type = CourseType.objects.create(name="CM")
td_type = CourseType.objects.create(name="TD")
tp_type = CourseType.objects.create(name="TP")

# Create Departments
gl_department = Department.objects.create(name="Génie Logiciel", abbrev="GL")

# Create Training Programme
gl_programme = TrainingProgramme.objects.create(name="GL Programme", abbrev="GLP", department=gl_department)

# Create Group
group_a1 = Group.objects.create(name="A1", train_prog=gl_programme, size=25)

# Create Modules
math_module = Module.objects.create(name="Mathematics", abbrev="MATH", department=gl_department)
cs_module = Module.objects.create(name="Computer Science", abbrev="CS", department=gl_department)

# Create Tutors
tutor_john = Tutor.objects.create(username="john_doe", first_name="John", last_name="Doe", is_admin=True)
tutor_jane = Tutor.objects.create(username="jane_doe", first_name="Jane", last_name="Doe")

# Assign Modules to Tutors
TutorModule.objects.create(tutor=tutor_john, module=math_module)
TutorModule.objects.create(tutor=tutor_jane, module=cs_module)

# Create Courses
Course.objects.create(tutor=tutor_john, group=group_a1, year=2023, type=cm_type, module=math_module)
Course.objects.create(tutor=tutor_jane, group=group_a1, year=2023, type=td_type, module=cs_module)

# Create Period
fall_period = Period.objects.create(name="Fall 2023", department=gl_department, starting_week=1, ending_week=16)
