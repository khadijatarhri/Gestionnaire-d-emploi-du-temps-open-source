from django.urls import include, path, re_path
from . import views

from .views import confirm_message, decline_message
urlpatterns = [
    path('',views.home, name='home'),
    path('login/',include('people.urls')),
    path('save_department/', views.save_department, name='save_department'),
    re_path(r'^aide$', views.aide, name="aide"),
    re_path(r'^contact/$', views.contact, name="contact"),
    re_path(r'^add_tutor/$', views.add_tutor, name='add_tutor'),
    re_path(r'^success_page/$', views.success_page, name='success_page'),
    path('ajout/', views.ajouter, name='ajout'),
    path('message/confirm/<int:message_id>/', confirm_message, name='confirm_message'),
    path('message/decline/<int:message_id>/', decline_message, name='decline_message'),
    path('check-new-unread-messages/', views.check_new_unread_messages, name='check_new_unread_messages'),
    path('sendcontact/', views.sendcontact, name='sendcontact'),
]
