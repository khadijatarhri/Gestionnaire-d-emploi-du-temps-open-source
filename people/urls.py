from django.urls import path, re_path
from . import views



from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy

from .views import semaine_type, modify, confirm_change, decline_change, inbox, read_message
from base.views import filter_display

urlpatterns = [
    path('', views.login_page, name='login'),
    path('logout', views.logout_page, name='logout'),
    path('chef/', views.chef_interface, name='chef'),
    path('prof/', views.prof_interface, name='prof'),
    re_path(r'^password-reset/$',auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html', email_template_name='registration/password_reset_email.html',success_url=reverse_lazy('password_reset_done')),name='password_reset'),
    path('password_reset/done/',auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'),name='password_reset_done'),
    path('reset/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'),name='password_reset_confirm'),
    path('reset/done/',auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'),name='password_reset_complete'),
    path('chef/generate_edt/', views.generate_edt_view, name='generate_edt'),
    path('chef/generer', views.generate_edt_view, name='generer'),
    path('chef/apply_edt/', views.apply_edt_view, name='apply_edt'),
    path('chef/ajouter', views.ajouter, name = 'ajouter'),
    path('chef/ajouter/ajouter_prof', views.ajouter_prof, name='creer_prof'),
    path('chef/ajouter/ajouter_module', views.ajouter_module, name='creer_module'),
    path('chef/ajouter/supprimer_prof', views.supprimer_prof, name='supprimer_prof'),
    path('chef/ajouter/supprimer_module', views.supprimer_module, name='supprimer_module'),
    path('semaine_type/', semaine_type, name='semaine_type'),
    path('consulter/', filter_display, name='consulter'),
    path('modify/', modify, name='modify'),
    path('confirm_change/<str:encoded_conflicting_course_id>/<str:encoded_course_id>/', confirm_change, name='confirm_change'),
    path('decline_change/<str:encoded_course_id>/', decline_change, name='decline_change'),
    path('inbox/', inbox, name='inbox'),
    path('message/<int:message_id>/', read_message, name='read_message'),
]
