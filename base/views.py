from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404

from django.template.response import TemplateResponse
from django.core.mail import send_mail
from people.models import Tutor, TrainingProgramme, Department 
from django.core.exceptions import ObjectDoesNotExist
from base.forms import ContactForm

from django.contrib.auth.decorators import login_required


import logging

# Create a logger
logger = logging.getLogger(__name__)


#imports for optapy
from .models import TutorModule, TimeSlot, Room, Schedule, TutorAvailability, Holiday, Group, Course, Day, Module
from .domain import DomainRoom, DomainTimeslot, Lesson, TimeTable, DomainTeacherAvailability, DomainHoliday, generate_problem

from people.models import TrainingProgramme
from people.forms import AddTutorForm

import optapy



#solver idea import first 

from .constraints import define_constraints  
from optapy import solver_factory_create
import optapy.config
from optapy.types import Duration



# Create your views here.

def home(request):
    return render(request, 'home.html')

def save_department(request):
    if request.method == 'POST':
        department = request.POST.get('department')
        request.session['selected_department'] = department
        return redirect('login')
    else:
        return HttpResponse("Method not allowed")

def aide(request):
    return render(request, 'aide.html')





def contact(req):
    ack = ''
    if req.method == 'POST':
        form = ContactForm(req.POST)
        if form.is_valid():
            dat = form.cleaned_data
            recip_send = [Tutor.objects.get(username=
                                            dat.get("recipient")).email,
                          dat.get("sender")]
            try:
                send_mail(
                    '[EdT ENSIAS] ' + dat.get("subject"),
                    "(Cet e-mail vous a été envoyé depuis le site des emplois"
                    " du temps de l'ENSIAS)\n\n"
                    + dat.get("message"),
                    dat.get("sender"),
                    recip_send,
                )
                ack='email sent'
            except:
                ack = 'Envoi du mail impossible !'
                return TemplateResponse(req, 'contact.html',
                              {'form': form,
                               'ack': ack
                              })

            return render(req,'contact.html',{'ack' :ack})
    else:
        init_mail = ''
        if req.user.is_authenticated:
            init_mail = req.user.email
        form = ContactForm(initial={
            'sender': init_mail})
    return TemplateResponse(req, 'contact.html',
                  {'form': form,
                   'ack': ack
                  })


def add_tutor(request):
    if request.method == 'POST':
        form = AddTutorForm(request.POST)
        if form.is_valid():
            # If the form is valid, save the new tutor instance
            form.save()
            # Redirect to a success page, or any other desired action
            return redirect('success_page')
    else:
        # If the request method is GET, initialize an empty form
        form = AddTutorForm()
    
    # Render the template with the form
    return render(request, 'add_tutor.html', {'form': form})

def success_page(request):
    return render(request, 'success_page.html')


#start the work with octapy 

# teacher availability

def is_available(tutor, timeslot, week):
    try:
        availability_record = TutorAvailability.objects.get(tutor=tutor, time_slot=timeslot, week=week)
        return availability_record.availability
    except TutorAvailability.DoesNotExist:
        return 1.0  # Default to fully available if not specified


def solve_and_save_schedule(week, training_program):
    try:
        solver_config = optapy.config.solver.SolverConfig() \
            .withEntityClasses(Lesson) \
            .withSolutionClass(TimeTable) \
            .withConstraintProviderClass(define_constraints) \
            .withTerminationSpentLimit(Duration.ofSeconds(30))

        problem = generate_problem(week, training_program) # add the parameter in the definition of the function
        problem.__str__()
        if problem is None:
            raise ValueError("Problem generation failed")

        solution = solver_factory_create(solver_config) \
        .buildSolver() \
        .solve(generate_problem(week=1))

        if solution is None:
            raise ValueError("Solver returned None")

        Schedule.objects.filter(week=week).delete()
        for lesson in solution.get_lesson_list():
            schedule = Schedule(
                course=Course.objects.get(pk=lesson.id),
                time_slot=TimeSlot.objects.get(pk=lesson.timeslot.id),
                room=Room.objects.get(pk=lesson.room.id),
                week=week
            )
            schedule.save()

        return solution
    except Exception as e:
        # Handle exceptions gracefully (e.g., log the error and return None)
        print(f"Error solving and saving schedule: {e}")
        return None

def generate_timetable_html(solution):
    if solution is None:
        logger.error("No solution provided to generate_timetable_html")
        return {}

    timetable = {}
    for lesson in solution.get_lesson_list():
        time_range = f"{lesson.timeslot.start_time.strftime('%H:%M')} - {lesson.timeslot.end_time.strftime('%H:%M')}"
        day_code = lesson.timeslot.day[:2].lower()
        if time_range not in timetable:
            timetable[time_range] = {'m': [], 'tu': [], 'w': [], 'th': [], 'f': [], 'sa': []}
        timetable[time_range][day_code].append(f"{lesson.subject} ({lesson.teacher}) in {lesson.room.name}")

    return timetable

def timetable_view(request, week, trainingProgram_id):
    # get the trainingProgram object 
    training_program = get_object_or_404(TrainingProgramme, pk=trainingProgram_id)
    #week = request.GET.get('week', 1)
    # i have to fix the selection of the trainingprogram : la filiere (generation d edt pour une filiere et promo donnée)
    solution = solve_and_save_schedule(week,training_program)
    timetable_items = solution.items() # if the problem persists try to implement the items method or something similar
    context = {'timetable_items': timetable_items}
    return render(request, 'schedule.html', context)

# apply function 
def apply_schedule_to_weeks(request, training_program_id, schedule_week, starting_week, ending_week):
    # Get the schedule for the specified week
    schedule_entries = Schedule.objects.filter(week=schedule_week, training_program=training_program_id)
    
    for week in range(starting_week, ending_week+1):
        # Clear existing schedules for the target week
        Schedule.objects.filter(week=week, training_program=training_program_id).delete()
        
        for entry in schedule_entries:
            # Create a new schedule entry for the target week
            Schedule.objects.create(
                course=entry.course,
                time_slot=entry.time_slot,
                room=entry.room,
                week=week,
                training_program=training_program_id
            )


# filter view 

@login_required
def filter_display(request):
    week = request.GET.get('week')
    group = request.GET.get('group')
    training_program = request.GET.get('training_program')
    tutor = request.GET.get('tutor')
    room = request.GET.get('room')
    module = request.GET.get('module')
    
    # Base queryset for schedules
    schedules = Schedule.objects.all()

    # Apply filters if parameters are provided
    if week:
        schedules = schedules.filter(week=week)
    if group:
        schedules = schedules.filter(course__group=group)
    if training_program:
        schedules = schedules.filter(course__training_program=training_program)
    if tutor:
        schedules = schedules.filter(course__tutor=tutor)
    if room:
        schedules = schedules.filter(room=room)
    if module:
        schedules = schedules.filter(course__module=module)
    
    # Fetch all unique timeslots and days
    timeslots = TimeSlot.objects.all().order_by('start_time')
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    # Organize schedule entries into a dictionary keyed by day and timeslot
    timetable = {day: {timeslot: None for timeslot in timeslots} for day in days}
    for entry in schedules:
        day = entry.time_slot.day
        timeslot = entry.time_slot
        timetable[day][timeslot] = entry

    context = {
        'timetable': timetable,
        'timeslots': timeslots,
        'days': days,
        'week': week,
        'groups': Group.objects.all(),
        'training_programs': TrainingProgramme.objects.all(),
        'tutors': Tutor.objects.all(),
        'rooms': Room.objects.all(),
        'modules': Module.objects.all(),
    }

    return render(request, 'filtered_display.html', context)

def ajouter(request):
    return render(request, 'ajouter.html')