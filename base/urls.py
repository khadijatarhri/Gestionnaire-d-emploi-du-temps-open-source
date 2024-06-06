from django.urls import include, path, re_path
from . import views
from people.views import submit_availability

urlpatterns = [
    path('',views.home, name='home'),
    path('login/',include('people.urls')),
    path('save_department/', views.save_department, name='save_department'),
    re_path(r'^aide$', views.aide, name="aide"),
    re_path(r'^contact/$', views.contact, name="contact"),
    re_path(r'^add_tutor/$', views.add_tutor, name='add_tutor'),
    re_path(r'^success_page/$', views.success_page, name='success_page'),
    path('ajout/', views.ajouter, name='ajout'),

]
