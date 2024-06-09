from django.urls import path, re_path
from . import views



from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy


from base.views import filter_display, send_message

urlpatterns = [
    path('', views.login_page, name='login'),
    path('logout', views.logout_page, name='logout'),
    path('chef/', views.chef_interface, name='chef'),
    path('prof/', views.prof_interface, name='prof'),
    re_path(r'^password-reset/$',auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html', email_template_name='registration/password_reset_email.html',success_url=reverse_lazy('password_reset_done')),name='passwourd_reset'),
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
    
    path('consulter/', filter_display, name='consulter'),
    path('modify/', send_message, name='modify'),
    
    path('forgot/', views.password_change, name='password_change'),
    path('chef/notifications/', views.notifications, name='notifications'),
    path('prof/notifications/', views.notifications, name='notifications'),
    path('mark_as_read/<int:message_id>/', views.mark_as_read, name='mark_as_read'),
    path('confirm_message/<int:message_id>/', views.confirm_message, name='confirm_message'),
    path('decline_message/<int:message_id>/', views.decline_message, name='decline_message'),
    path('check_new_messages/', views.check_new_messages, name='check_new_messages'),
    path('select_week_and_course/', views.select_week_and_course, name='select_week_and_course'),
    path('load_courses/', views.load_courses, name='load_courses'),
    path('stype/', views.semaine_type, name='stype'),

]
