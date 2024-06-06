from django import forms
from django.contrib.auth.forms import UserCreationForm
from people.models import Tutor

from django.db import transaction
from base.models import Schedule, TutorAvailability, TimeSlot


class AddTutorForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Required. Enter a valid email address.')
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=150)
    subject = forms.CharField(max_length=255, required=False)
    department = forms.CharField(max_length=7, initial='gl')

    class Meta(UserCreationForm.Meta):
        model = Tutor
        fields = ['email', 'first_name', 'last_name', 'subject', 'department']

    @transaction.atomic
    def save(self):
        tutor = super().save(commit=False)
        tutor.is_admin = False  # Assuming tutors are considered administrators
        tutor.subject = self.cleaned_data['subject']
        tutor.department = self.cleaned_data['department']
        tutor.username = self.generate_username()  # Set username
        tutor.password = 'pass'
        tutor.save()
        return tutor

    def generate_username(self):
        first_name = self.cleaned_data.get('first_name')
        last_name = self.cleaned_data.get('last_name')
        # Concatenate first name and last name and return as username
        return (first_name + last_name).lower()  # Convert to lowercase for consistency



class ChangeCourseTimeForm(forms.Form):
    current_time_slot = forms.ModelChoiceField(queryset=TimeSlot.objects.all(), widget=forms.HiddenInput())
    new_time_slot = forms.ModelChoiceField(queryset=TimeSlot.objects.all())
    
class PreferenceForm(forms.ModelForm):
    class Meta:
        model = TutorAvailability
        fields = ['time_slot', 'availability']