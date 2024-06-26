# -*- coding: utf-8 -*-

# This file is part of the FlOpEDT/FlOpScheduler project.
# Copyright (c) 2017
# Authors: Iulian Ober, Paul Renaud-Goud, Pablo Seban, et al.
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public
# License along with this program. If not, see
# <http://www.gnu.org/licenses/>.
# 
# You can be released from the requirements of the license by purchasing
# a commercial license. Buying such a license is mandatory as soon as
# you develop activities involving the FlOpEDT/FlOpScheduler software
# without disclosing the source code of your own applications.

from django import forms
from people.models import Tutor


class ContactForm(forms.Form):
    sender = forms.EmailField(label='Votre adresse mail :', widget=forms.EmailInput(attrs={'class': 'form-field'}))
    recipient = forms.CharField(
        label='Destinataire :',
        max_length=4,
        help_text="Acronyme : 4 caractères max", widget=forms.TextInput(attrs={'class': 'form-field'}))
    subject = forms.CharField(
        label='Sujet du mail :',
        max_length=100,
        help_text="100 caractères max", widget=forms.TextInput(attrs={'class': 'form-field'}))
    message = forms.CharField(label='Corps du mail :',
                              max_length=2000,
                              widget=forms.Textarea(attrs={'class': 'form-field'}))

    def clean_recipient(self):
        recipient = self.cleaned_data['recipient']
        if not Tutor.objects.filter(username=recipient).exists():
            raise forms.ValidationError("Cette personne n'existe pas.")
        return recipient
