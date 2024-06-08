from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404

from django.contrib.auth.decorators import login_required
from datetime import datetime
#for the choice of the promo
from .models import TrainingProgramme
from base.views import timetable_view, apply_schedule_to_weeks

from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.contrib import messages

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

import json

from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

import json

#for the messagerie 
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from .forms import ChangeCourseTimeForm, PreferenceForm

from datetime import time

from .models import Tutor
from base.models import Module, TutorModule,TimeSlot,Schedule, TutorAvailability, Day, Message, Room, Group

# Create your views here.
def login_page(request):
    error_message = False
    if request.method == "POST":
        department = request.session.get('selected_department')
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_admin == True :
                login(request, user)
                # Redirect to appropriate page after successful login
                return redirect(reverse('chef'))
            elif user.is_admin == False:
                login(request, user)
            return redirect(reverse('prof'))
        else:
            error_message = "Invalid username or password."
            return render(request, 'login.html', {'error_message': error_message})
    else:
        return render(request, 'login.html')

@login_required
def chef_interface(request):
    return render(request, 'chef.html')

@login_required
def prof_interface(request):
    return render(request, 'Prof.html')


def logout_page (request):
     logout(request)
     messages.success(request,("You Were Logged Out !!"))
     return redirect(reverse('home'))

def generer_chef(request): 
    training_programs = TrainingProgramme.objects.all()

    context = {'training_programs':training_programs}      
    return render(request, 'options.html',context)


def ajouter(request):
    return render(request, 'ajouter_chef.html')

def generate_edt_view(request):
    if (request.method == 'POST'):
        week = request.POST['week']
        program_id = request.POST['promo']
        #timetable_view(request, int(week+1), program_id)
        return consulter(request,int(week))
    else:
        return generer_chef(request)


def consulter(request, week):
    training_programs = TrainingProgramme.objects.all()
    schedules_9_m = Schedule.objects.filter(training_program= '1',week= week, time_slot__day__day='m', time_slot__start_time=time(9,0))
    schedules_11_m = Schedule.objects.filter(training_program= '1',week= week, time_slot__day__day='m', time_slot__start_time=time(11,0))
    schedules_14_m = Schedule.objects.filter(training_program= '1',week= week, time_slot__day__day='m', time_slot__start_time=time(14,0))
    schedules_16_m = Schedule.objects.filter(training_program= '1',week= week, time_slot__day__day='m', time_slot__start_time=time(16,0))
    schedules_9_tu = Schedule.objects.filter(training_program= '1',week= week, time_slot__day__day='tu', time_slot__start_time=time(9,0))
    schedules_11_tu = Schedule.objects.filter(training_program= '1',week= week, time_slot__day__day='tu', time_slot__start_time=time(11,0))
    schedules_14_tu = Schedule.objects.filter(training_program= '1',week= week, time_slot__day__day='tu', time_slot__start_time=time(14,0))
    schedules_16_tu = Schedule.objects.filter(training_program= '1',week= week, time_slot__day__day='tu', time_slot__start_time=time(16,0))
    schedules_9_w = Schedule.objects.filter(training_program= '1',week= week, time_slot__day__day='w', time_slot__start_time=time(9,0))
    schedules_11_w = Schedule.objects.filter(training_program= '1',week= week, time_slot__day__day='w', time_slot__start_time=time(11,0))
    schedules_14_w = Schedule.objects.filter(training_program= '1',week= week, time_slot__day__day='w', time_slot__start_time=time(14,0))
    schedules_16_w = Schedule.objects.filter(training_program= '1',week= week, time_slot__day__day='w', time_slot__start_time=time(16,0))
    schedules_9_th = Schedule.objects.filter(training_program= '1',week= week, time_slot__day__day='th', time_slot__start_time=time(9,0))
    schedules_11_th = Schedule.objects.filter(training_program= '1',week= week, time_slot__day__day='th', time_slot__start_time=time(11,0))
    schedules_14_th = Schedule.objects.filter(training_program= '1',week= week, time_slot__day__day='th', time_slot__start_time=time(14,0))
    schedules_16_th = Schedule.objects.filter(training_program= '1',week= week, time_slot__day__day='th', time_slot__start_time=time(16,0))
    schedules_9_f = Schedule.objects.filter(training_program= '1',week= week, time_slot__day__day='f', time_slot__start_time=time(9,0))
    schedules_11_f = Schedule.objects.filter(training_program= '1',week= week, time_slot__day__day='f', time_slot__start_time=time(11,0))
    schedules_14_f = Schedule.objects.filter(training_program= '1',week= week, time_slot__day__day='f', time_slot__start_time=time(14,0))
    schedules_16_f = Schedule.objects.filter(training_program= '1',week= week, time_slot__day__day='f', time_slot__start_time=time(16,0))
    context= {'schedules_9_m': schedules_9_m,'schedules_11_m': schedules_11_m, 'schedules_14_m': schedules_14_m,'schedules_16_m': schedules_16_m,
                                            'schedules_9_tu': schedules_9_tu,'schedules_11_tu': schedules_11_tu, 'schedules_14_tu': schedules_14_tu,'schedules_16_tu': schedules_16_tu,
                                            'schedules_9_w': schedules_9_w,'schedules_11_w': schedules_11_w, 'schedules_14_w': schedules_14_w,'schedules_16_w': schedules_16_w,
                                            'schedules_9_th': schedules_9_th,'schedules_11_th': schedules_11_th, 'schedules_14_th': schedules_14_th,'schedules_16_th': schedules_16_th,
                                            'schedules_9_f': schedules_9_f,'schedules_11_f': schedules_11_f, 'schedules_14_f': schedules_14_f,'schedules_16_f': schedules_16_f,'training_programs':training_programs}
    return render(request, 'options.html', context)
    

def apply_edt_view(request):
    if (request.method == 'POST'):
        schedule_week = request.POST['week']
        program_id = request.POST['promo2']
        starting_week = request.POST['starting_week']
        ending_week = request.POST['ending_week']
        apply_schedule_to_weeks(request, program_id,schedule_week,starting_week,ending_week)

def ajouter_prof(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        department = request.POST['selected-option_d_ap']

        tutor = Tutor.objects.create(username=username, email=email, department=department)
        tutor.set_password('pwd')
        try:
            tutor.save()
            success_message = 'Professeur créé avec succès'
            return render(request, 'ajouter_chef.html', {'success_message1': success_message})
        except Exception as e:
            error_message = 'Erreur lors de la création du professeur! Essayez encore une fois.'
            return render(request, 'ajouter_chef.html', {'error_message1': error_message})

def ajouter_module(request):
    if request.method == 'POST':
        name = request.POST['name']
        department = request.POST['selected-option_d_am']
        filiere = request.POST['selected-option_f_am']
        niveau = request.POST['annee']

        module = Module(name=name, training_program=filiere + ' ' + niveau, department=department)
        try:
            module.save()
            success_message = 'Module créé avec succès'
            return render(request, 'ajouter_chef.html', {'success_message2': success_message})
        except Exception as e:
            error_message = 'Erreur lors de la création du module! Essayez encore une fois.'
            return render(request, 'ajouter_chef.html', {'error_message2': error_message})

def supprimer_prof(request):
    if request.method == 'POST':
        email = request.POST['username']
        try:
            tutor = Tutor.objects.get(email=email)
            modules = TutorModule.objects.filter(tutor=tutor)
            if modules.exists():
                return render(request, 'ajouter_chef.html', {'error_message3': 'Impossible de supprimer le professeur!'})
            else:
                tutor.delete()
                return render(request, 'ajouter_chef.html', {'success_message3': 'Professeur supprimé avec succès'})
        except Tutor.DoesNotExist:
            error_message = 'Professeur non existant'
            return render(request, 'ajouter_chef.html', {'error_message3': error_message})

def supprimer_module(request):
    if request.method == 'POST':
        name = request.POST['name']
        try:
            module = Module.objects.get(name=name)
            period = TutorModule.objects.filter(module=module)
            if period.exists():  # Normally you should check if the period is not finished
                return render(request, 'ajouter_chef.html', {'error_message4': 'Impossible de supprimer le module!'})
            else:
                module.delete()
                return render(request, 'ajouter_chef.html', {'success_message4': 'Module supprimé avec succès'})
        except Module.DoesNotExist:
            error_message = 'Module non existant'
            return render(request, 'ajouter_chef.html', {'error_message4': error_message})


#messagerie view :

@login_required
def semaine_type(request):
    timeslots = TimeSlot.objects.all()
    preferences = TutorAvailability.objects.filter(tutor=request.user)
    if request.method == 'POST':
        for timeslot in timeslots:
            availability = request.POST.get(str(timeslot.id))
            if availability:
                preference, created = TutorAvailability.objects.get_or_create(tutor=request.user, time_slot=timeslot)
                if (availability == 'red'):
                    preference.availability = 0
                elif(availability == 'yellow'):
                    preference.availability = 0.5
                else:
                    preference.availability = 1
                preference.save()
        return redirect('semaine_type')
    return render(request, 'semaine_type.html', {'timeslots': timeslots, 'preferences': preferences})

@login_required
def modify(request): #hadi modifier
    courses = Schedule.objects.filter(course__tutor=request.user)
    if request.method == 'POST':
        current_timeslot_id = request.POST.get('current_timeslot')
        new_timeslot_id = request.POST.get('new_timeslot')
        current_timeslot = get_object_or_404(TimeSlot, id=current_timeslot_id)
        new_timeslot = get_object_or_404(TimeSlot, id=new_timeslot_id)
        course_to_change = get_object_or_404(Schedule, course__tutor=request.user, time_slot=current_timeslot)
        
        conflicting_course = Schedule.objects.filter(time_slot=new_timeslot).first()
        if conflicting_course:
            subject = "Course Schedule Change Confirmation"
            body = f"User {request.user.username} wants to change their course to your time slot : {new_timeslot.start_time} : {new_timeslot.end_time}. Do you approve?"
            confirmation_link = reverse('confirm_change', args=[urlsafe_base64_encode(force_bytes(conflicting_course.id)), urlsafe_base64_encode(force_bytes(course_to_change.id))])
            decline_link = reverse('decline_change', args=[urlsafe_base64_encode(force_bytes(course_to_change.id))])
            
            message = Message.objects.create(
                sender=request.user,
                receiver=conflicting_course.course.tutor,
                subject=subject,
                body=body,
                related_course=course_to_change.course.module.name,
                is_confirmation=True,
                confirmation_link=confirmation_link,
                decline_link=decline_link
            )
            message.save()
            return redirect('inbox')
        else:
            course_to_change.time_slot = new_timeslot
            course_to_change.save()
            return redirect('course_detail', course_id=course_to_change.id)
    return render(request, 'filtered_display.html', {'courses': courses})

@login_required
def confirm_change(request, encoded_conflicting_course_id, encoded_course_id):
    conflicting_course_id = force_str(urlsafe_base64_decode(encoded_conflicting_course_id))
    course_id = force_str(urlsafe_base64_decode(encoded_course_id))
    conflicting_course = get_object_or_404(Schedule, id=conflicting_course_id)
    course = get_object_or_404(Schedule, id=course_id)
    
    course.time_slot = conflicting_course.time_slot
    course.save()

    confirmation_message = Message.objects.create(
        sender=request.user,
        receiver=course.course.tutor,
        subject="Course Schedule Change Approved",
        body="Your course schedule change has been approved.",
        related_course=course.course.module.name,
        is_confirmation=False
    )
    confirmation_message.save()

    return redirect('inbox')

@login_required
def decline_change(request, encoded_course_id):
    course_id = force_str(urlsafe_base64_decode(encoded_course_id))
    course = get_object_or_404(Schedule, id=course_id)
    
    decline_message = Message.objects.create(
        sender=request.user,
        receiver=course.course.tutor,
        subject="Course Schedule Change Declined",
        body="Your course schedule change has been declined.",
        related_course=course.course.module.name,
        is_confirmation=False
    )
    decline_message.save()

    return redirect('inbox')

@login_required
def inbox(request):
    messages = request.user.received_messages.all()
    return render(request, 'inbox.html', {'messages': messages})

@login_required
def read_message(request, message_id):
    message = get_object_or_404(Message, id=message_id)
    if message.receiver == request.user:
        message.is_read = True
        message.save()
        return render(request, 'read_message.html', {'message': message})
    else:
        return redirect('inbox')
    



@login_required
@csrf_exempt
def submit_availability(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user = request.user

            for item in data:
                day_code = item['day']
                time_slot = item['time']
                status = item['status']
                availability = 1 if status == 'disponible' else 0.5 if status == 'unsure' else 0

                # Extracting start and end time from the time slot
                start_time_str, end_time_str = time_slot.split(' - ')
                start_time = datetime.strptime(start_time_str, '%H:%M').time()
                end_time = datetime.strptime(end_time_str, '%H:%M').time()

                # Getting the Day object
                day = Day.objects.get(day=day_code)

                # Getting or creating the TimeSlot object
                time_slot_obj, created = TimeSlot.objects.get_or_create(day=day, start_time=start_time, end_time=end_time)

                # Update or create the availability entry
                TutorAvailability.objects.update_or_create(
                    tutor=user,
                    time_slot=time_slot_obj,
                    availability=availability,
                )

            return JsonResponse({'success': True, 'message': 'Availability updated successfully.'})

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Invalid JSON data.'}, status=400)
        except Day.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Invalid day.'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)

    return redirect('ajout')


# forgot password

def password_change (request):
    return render(request, 'forgot_password.html')


#modifier

def modifier_view(request):
    training_program = TrainingProgramme.objects.all()
    tutors = Tutor.objects.all()
    groups = Group.objects.all()
    modules = Module.objects.all()
    rooms = Room.objects.all()
    weeks = [i for i in range (1,53)]
    schedules = Schedule.objects.all()

    week = request.GET.get('week')
    if week:
        schedules = schedules.filter(week=week)
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
                                            'schedules_9_f': schedules_9_f,'schedules_11_f': schedules_11_f, 'schedules_14_f': schedules_14_f,'schedules_16_f': schedules_16_f}
    return render(request, 'consulter.html', context)

#3 try for the message notificationn

@login_required
def notifications(request):
    messages = Message.objects.filter(receiver=request.user)
    return render(request, 'notifications.html', {'messages': messages})

@login_required
def mark_as_read(request, message_id):
    message = get_object_or_404(Message, id=message_id, receiver=request.user)
    message.is_read = True
    message.save()
    return redirect('notifications')

@login_required
def check_new_messages(request):
    new_messages = Message.objects.filter(receiver=request.user, is_read=False).exists()
    return JsonResponse({'new_messages': new_messages})

def confirm_message(request, message_id):
    message = get_object_or_404(Message, id=message_id, receiver=request.user)
    if request.method == 'POST':
        message.is_read = True
        message.is_confirmation = True
        message.save()
        # Create a confirmation message
        Message.objects.create(
            sender=request.user,
            receiver=message.sender,
            body=f"Votre demande :'{message.body}' a été confirmée.",
            is_read=False,
            related_course=message.related_course,
        )
        # Swap time slots
        if message.schedule_sender and message.schedule_receiver:
            message.schedule_receiver.time_slot, message.schedule_sender.time_slot = (
                message.schedule_sender.time_slot, 
                message.schedule_receiver.time_slot
            )
            message.schedule_receiver.save()
            message.schedule_sender.save()

        return JsonResponse({"status": "confirmed"})
    return JsonResponse({"error": "Invalid request"}, status=400)

@login_required
def decline_message(request, message_id):
    message = get_object_or_404(Message, id=message_id, receiver=request.user)
    if request.method == 'POST':
        message.is_read = True
        message.is_confirmation = False
        message.save()
        # Create a decline message
        Message.objects.create(
            sender=request.user,
            receiver=message.sender,
            body=f"Votre demande :'{message.body}' a été refusée.",
            is_read=False,
            related_course=message.related_course,
        )
        return JsonResponse({"status": "declined"})
    return JsonResponse({"error": "Invalid request"}, status=400)



#decaler 
def load_courses(request):
    week = request.GET.get('week')
    courses = []
    message = ""
    if week:
        try:
            schedules = Schedule.objects.filter(week=week, course__tutor=request.user)
            courses = [{'schedule': {
                'id': schedule.id,
                'course': {
                    'module': {'name': schedule.course.module.name},
                    'group': schedule.course.group.name
                },
                'time_slot': str(schedule.time_slot)
            }} for schedule in schedules]
        except Schedule.DoesNotExist:
            message = "La semaine sélectionnée n'existe pas."
    return JsonResponse({'courses': courses, 'message': message}, safe=False)

def select_week_and_course(request):
    message = ""
    if request.method == 'POST':
        schedule_id = request.POST.get('course')
        target = request.POST.get('s1')
        try:
            schedule = Schedule.objects.get(pk=schedule_id)
            schedule.week = target
            schedule.save()
            Message.objects.create(
                sender=request.user,
                receiver=Tutor.objects.get(is_admin=True, training_program=schedule.training_program),
                subject='De {}, Décalage de cours :'.format(request.user),
                body='Décalage du cours {} du group {} le {}, de la semaine : {} à la semaine {} pour le professeur : {}'.format(
                    schedule.course.module.name, schedule.course.group, schedule.time_slot.__str__(), schedule.week, target, schedule.course.tutor)
            )
            message = 'Cours décalé avec succès'
        except Schedule.DoesNotExist:
            message = "L'horaire sélectionné n'existe pas."
    return render(request, 'decaler.html', {'message': message})