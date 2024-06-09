from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404

from django.template.response import TemplateResponse
from django.core.mail import send_mail
from people.models import Tutor, TrainingProgramme, Department
from django.core.exceptions import ObjectDoesNotExist
from base.forms import ContactForm
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Message
from django.utils.dateparse import parse_time
import json

from django.http import JsonResponse, HttpResponseNotAllowed


from datetime import time

import logging, json
# Create a logger
logger = logging.getLogger(__name__)


#imports for optapy
from .models import TutorModule, TimeSlot, Room, Schedule, TutorAvailability, Holiday, Group, Course, Day, Module,Message
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
            schedule = Schedule.objects.create()
            schedule.course.module = entry.course.module
            schedule.course.tutor = entry.course.tutor
            schedule.time_slot = entry.time_slot
            schedule.room = entry.room
            schedule.training_program = entry.training_program
            schedule.week = entry.week
            schedule.save()
    message= 'EDT appliqué au semaine données'
    return render(request, 'options.html', {'message1': message})

# filter view 

@login_required
def filter_display(request):
    training_program = TrainingProgramme.objects.all()
    tutors = Tutor.objects.all()
    groups = Group.objects.all()
    modules = Module.objects.all()
    rooms = Room.objects.all()
    weeks = [i for i in range (1,53)]
    schedules = Schedule.objects.all()

    week = request.GET.get('week')
    group = request.GET.getlist('group')
    training_program = request.GET.getlist('training_program')
    tutor = request.GET.getlist('tutor')
    room = request.GET.getlist('room')
    module = request.GET.getlist('module')
    
    # Base queryset for schedules
        

    # Apply filters if parameters are provided
    if week:
        schedules = schedules.filter(week=week)
    if group :
        schedules = schedules.filter(course__group__in=group)
    if training_program :
        schedules = schedules.filter(course__group__training_program__in=training_program)
    if tutor:
        schedules = schedules.filter(course__tutor__in=tutor)
    if room:
        schedules = schedules.filter(room__in=room)
    if module:
        schedules = schedules.filter(course__module__in=module)

        
    schedules_9_m = schedules.filter( time_slot__day__day='m', time_slot__start_time=time(9,0))
    schedules_11_m = schedules.filter( time_slot__day__day='m', time_slot__start_time=time(11,0))
    schedules_14_m = schedules.filter( time_slot__day__day='m', time_slot__start_time=time(14,0))
    schedules_16_m = schedules.filter( time_slot__day__day='m', time_slot__start_time=time(16,0))
    schedules_9_tu = schedules.filter( time_slot__day__day='tu', time_slot__start_time=time(9,0))
    schedules_11_tu = schedules.filter( time_slot__day__day='tu', time_slot__start_time=time(11,0))
    schedules_14_tu = schedules.filter( time_slot__day__day='tu', time_slot__start_time=time(14,0))
    schedules_16_tu = schedules.filter( time_slot__day__day='tu', time_slot__start_time=time(16,0))
    schedules_9_w = schedules.filter( time_slot__day__day='w', time_slot__start_time=time(9,0))
    schedules_11_w = schedules.filter( time_slot__day__day='w', time_slot__start_time=time(11,0))
    schedules_14_w = schedules.filter( time_slot__day__day='w', time_slot__start_time=time(14,0))
    schedules_16_w = schedules.filter( time_slot__day__day='w', time_slot__start_time=time(16,0))
    schedules_9_th = schedules.filter( time_slot__day__day='th', time_slot__start_time=time(9,0))
    schedules_11_th = schedules.filter( time_slot__day__day='th', time_slot__start_time=time(11,0))
    schedules_14_th = schedules.filter( time_slot__day__day='th', time_slot__start_time=time(14,0))
    schedules_16_th = schedules.filter( time_slot__day__day='th', time_slot__start_time=time(16,0))
    schedules_9_f = schedules.filter( time_slot__day__day='f', time_slot__start_time=time(9,0))
    schedules_11_f = schedules.filter( time_slot__day__day='f', time_slot__start_time=time(11,0))
    schedules_14_f = schedules.filter( time_slot__day__day='f', time_slot__start_time=time(14,0))
    schedules_16_f = schedules.filter( time_slot__day__day='f', time_slot__start_time=time(16,0))
    context= {'schedules_9_m': schedules_9_m,'schedules_11_m': schedules_11_m, 'schedules_14_m': schedules_14_m,'schedules_16_m': schedules_16_m,
                                            'schedules_9_tu': schedules_9_tu,'schedules_11_tu': schedules_11_tu, 'schedules_14_tu': schedules_14_tu,'schedules_16_tu': schedules_16_tu,
                                            'schedules_9_w': schedules_9_w,'schedules_11_w': schedules_11_w, 'schedules_14_w': schedules_14_w,'schedules_16_w': schedules_16_w,
                                            'schedules_9_th': schedules_9_th,'schedules_11_th': schedules_11_th, 'schedules_14_th': schedules_14_th,'schedules_16_th': schedules_16_th,
                                            'schedules_9_f': schedules_9_f,'schedules_11_f': schedules_11_f, 'schedules_14_f': schedules_14_f,'schedules_16_f': schedules_16_f,'training_program':training_program, 'tutors': tutors, 'groups':groups, 'modules':modules,'weeks':weeks, 'rooms':rooms}
    return render(request, 'filtered_display.html', context)



@csrf_exempt
def ajouter(request):
    semaine= Tutor.objects.get(is_admin=True, department= request.user.department).semaine_type
    if request.method == 'POST':
        data = json.loads(request.body)
        tutor = request.user.tutor  # Assumes the user is authenticated and linked to a Tutor instance.
        week = 1  # Replace with the actual week if it's dynamic.

        for entry in data:
            day = entry['day']
            start_time = parse_time(entry['time'].split(' - ')[0])
            end_time = parse_time(entry['time'].split(' - ')[1])
            time_slot = TimeSlot.objects.get(day__day=day, start_time=start_time, end_time=end_time)
            
            TutorAvailability.objects.update_or_create(
                tutor=tutor,
                time_slot=time_slot,
                week=week,
                defaults={'availability': float(entry['status'])}
            )
        
        return JsonResponse({'message': 'Availability updated successfully!'})

    return render(request, 'ajouter.html', {'semaine': semaine})

#modifier dyal bse7 had lmera
@login_required
def unseen_messages(request):
    messages = Message.objects.filter(receiver=request.user, is_read=False)
    message_list = [
        {
            'id': message.id,
            'sender': message.sender.username,
            'subject': message.subject,
            'body': message.body,
            'requires_response': message.requires_response,
        }
        for message in messages
    ]
    return JsonResponse({'messages': message_list})

@login_required
def update_message_status(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        message_id = data.get('message_id')
        action = data.get('action')  # 'confirm' or 'decline' or 'seen'

        message = get_object_or_404(Message, id=message_id, receiver=request.user)

        if action == 'seen':
            message.is_seen = True
            message.save()
            return JsonResponse({'success': True, 'message': 'Message marked as seen.'})
        elif action in ['confirm', 'decline'] and message.requires_response:
            # Handle confirm or decline
            message.is_seen = True
            message.save()
            # Add custom logic if needed for confirmation or decline
            return JsonResponse({'success': True, 'message': f'Message {action}ed successfully.'})

    return JsonResponse({'success': False, 'message': 'Invalid request method or action.'})


#consulter html = modifier
def send_message(request):
    week = request.GET.get('week', 2)
    timeslots = TimeSlot.objects.all()
    courses = Schedule.objects.filter(week = week, course__tutor = request.user)
    schedules = Schedule.objects.filter(week = week)
    schedules_9_m = schedules.filter( time_slot__day__day='m', time_slot__start_time=time(9,0))
    schedules_11_m = schedules.filter( time_slot__day__day='m', time_slot__start_time=time(11,0))
    schedules_14_m = schedules.filter( time_slot__day__day='m', time_slot__start_time=time(14,0))
    schedules_16_m = schedules.filter( time_slot__day__day='m', time_slot__start_time=time(16,0))
    schedules_9_tu = schedules.filter( time_slot__day__day='tu', time_slot__start_time=time(9,0))
    schedules_11_tu = schedules.filter( time_slot__day__day='tu', time_slot__start_time=time(11,0))
    schedules_14_tu = schedules.filter( time_slot__day__day='tu', time_slot__start_time=time(14,0))
    schedules_16_tu = schedules.filter( time_slot__day__day='tu', time_slot__start_time=time(16,0))
    schedules_9_w = schedules.filter( time_slot__day__day='w', time_slot__start_time=time(9,0))
    schedules_11_w = schedules.filter( time_slot__day__day='w', time_slot__start_time=time(11,0))
    schedules_14_w = schedules.filter( time_slot__day__day='w', time_slot__start_time=time(14,0))
    schedules_16_w = schedules.filter( time_slot__day__day='w', time_slot__start_time=time(16,0))
    schedules_9_th = schedules.filter( time_slot__day__day='th', time_slot__start_time=time(9,0))
    schedules_11_th = schedules.filter( time_slot__day__day='th', time_slot__start_time=time(11,0))
    schedules_14_th = schedules.filter( time_slot__day__day='th', time_slot__start_time=time(14,0))
    schedules_16_th = schedules.filter( time_slot__day__day='th', time_slot__start_time=time(16,0))
    schedules_9_f = schedules.filter( time_slot__day__day='f', time_slot__start_time=time(9,0))
    schedules_11_f = schedules.filter( time_slot__day__day='f', time_slot__start_time=time(11,0))
    schedules_14_f = schedules.filter( time_slot__day__day='f', time_slot__start_time=time(14,0))
    schedules_16_f = schedules.filter( time_slot__day__day='f', time_slot__start_time=time(16,0))
    context= {'schedules_9_m': schedules_9_m,'schedules_11_m': schedules_11_m, 'schedules_14_m': schedules_14_m,'schedules_16_m': schedules_16_m,
                                            'schedules_9_tu': schedules_9_tu,'schedules_11_tu': schedules_11_tu, 'schedules_14_tu': schedules_14_tu,'schedules_16_tu': schedules_16_tu,
                                            'schedules_9_w': schedules_9_w,'schedules_11_w': schedules_11_w, 'schedules_14_w': schedules_14_w,'schedules_16_w': schedules_16_w,
                                            'schedules_9_th': schedules_9_th,'schedules_11_th': schedules_11_th, 'schedules_14_th': schedules_14_th,'schedules_16_th': schedules_16_th,
                                            'schedules_9_f': schedules_9_f,'schedules_11_f': schedules_11_f, 'schedules_14_f': schedules_14_f,'schedules_16_f': schedules_16_f, 'courses': courses, 'timeslots': timeslots}
    if(request.method=='POST'):
        schedule_to_change = request.POST.get('cours')
        timeslot = request.POST.get('timing')
        if not schedule_to_change or not timeslot:
            context['error_message'] = 'Veuillez sélectionner un cours et un créneau horaire.'
            return render(request, 'consulter.html', context)
        schedule_to_change = Schedule.objects.get(pk = schedule_to_change)
        timeslot = TimeSlot.objects.get(pk=timeslot)
        schedule_victim = Schedule.objects.filter(time_slot = timeslot, course__group = schedule_to_change.course.group, week= schedule_to_change.week).first()
        

        if (not schedule_victim):
            schedule_to_change.time_slot = timeslot
            schedule_to_change.save()
            success_message = 'Changement du cours avec succès'
            context['success_message']= success_message
            return render(request, 'consulter.html', context)
        else:
            sch = Schedule.objects.filter(course__tutor =schedule_victim.course.tutor, time_slot =schedule_to_change.time_slot).first()
            if (sch):
                error_message = 'Impossible de faire ce changement'
                context['error_message']=error_message
                return render(request, 'consulter.html', context)
            else:
                if (schedule_victim.course.group.name.split(' ')[0]==schedule_to_change.course.group.name and len(schedule_victim.course.group.name.split(' '))!=1):
                    error_message = 'Impossible de faire ce changement'
                    context['error_message']=error_message
                    return render(request, 'consulter.html', context)
                else:
                    message = Message.objects.create(
                    sender=request.user,
                    receiver=schedule_victim.course.tutor,
                    subject="Demande de changement :",
                    body = f"Bonjour {schedule_victim.course.tutor.last_name}, \n\nJe souhaite qu'on échange nos cours. C'est-à-dire rendre votre cours '{schedule_victim.course.module.name}' pour le groupe {schedule_victim.course.group} le {timeslot.__str__()}. \n\nCordialement, \n{request.user.last_name}",

                    requires_response=True, schedule_sender = schedule_to_change, schedule_receiver=schedule_victim)
                    message.save()
                    confirm_link = f"/confirm-message/{message.id}/"
                    decline_link = f"/decline-message/{message.id}/"
                    message.confirmation_link = confirm_link
                    message.decline_link = decline_link
                    message.save()
                    message_attente= 'Veuillez attendre la confirmation du professeur concerné'
                    context['message_attente']= message_attente
                
                    return render(request, 'consulter.html', context)
            
    else:
        return render(request, 'consulter.html', context)

#fct that returns the non read messages for the user
def inbox(user):
    # Fetch unread messages for the logged-in user
    unread_messages = Message.objects.filter(receiver=user, is_read=False)
    # Mark fetched messages as read
    unread_messages.update(is_read=True)
    return unread_messages               

#for the javascript for checking new messages
def check_new_unread_messages(request):
    if not request.user.is_authenticated:
        return JsonResponse({'newRecord': []})
    unread_messages = Message.objects.filter(is_read=False, receiver=request.user)
    unread_message_data = [
        {
            'id': msg.id,
            'sender': msg.sender.username,
            'subject': msg.subject,
            'body': msg.body,
            'requires_response': msg.requires_response,
        }
        for msg in unread_messages
    ]
    return JsonResponse({'newRecord': unread_message_data})

# views.py
#for confirmation and decline 
# add the sousgroup contraint in sending the message

def confirm_message(request, message_id):
        message = get_object_or_404(Message, id=message_id)
        # Handle confirmation logic here
        # For example, update the schedule or notify the sender
        message.is_confirmation = True
        message.save()
        message_return = Message.objects.create(
                    sender=request.user,
                    receiver=message.sender,
                    subject="Confirmation :",
                    body = f"Bonjour {message.sender}, \n\n Votre demande de changement est acceptée '. \n\nCordialement, \n{request.user}",

                    requires_response=False  )
        message_return.save()
        return JsonResponse({'status': 'confirmed'})

def decline_message(request, message_id):
    
        message = get_object_or_404(Message, id=message_id)
        # Handle decline logic here
        message.is_confirmation = False
        message.save()
        message_return = Message.objects.create(
                    sender=request.user,
                    receiver=message.sender,
                    subject="Refus :",
                    body = f"Bonjour {message.sender}, \n\n Votre demande de changement est refusée '. \n\nCordialement, \n{request.user}",

                    requires_response=False  )
        message_return.save()
        return JsonResponse({'status': 'declined'})
  
def some_view(request):
    if 'HTTP_REFERER' in request.META:
        previous_url = request.META['HTTP_REFERER']
    else:
        previous_url = 'default/fallback/url/'  # Fallback URL if referer not available
    
    # Do something and redirect back
    return redirect(previous_url)


def sendcontact(request):
    if (request.method=='POST'):
        message_body = request.POST.get('sujet')
        messag_subject = request.POST.get('object')
        email = request.POST.get('email')
        receiver = Tutor.objects.filter(email = email).first()
        if receiver :
            message= Message.objects.create(
            sender = request.user,
            receiver = receiver,
            subject = messag_subject,
            body=message_body,
            requires_response = False
            )
            message.save()
            m = 'Message envoyé avec succés.'
            context={'message': m}
            return render(request, 'contact.html', context)
        else:
            m = 'Email incorrect ou utilisateurs non existant.'
            context={'message': m}
            return render(request, 'contact.html', context)
    return render(request , 'contact.html')