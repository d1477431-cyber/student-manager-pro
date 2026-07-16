from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.index, name='index'),
    path('add/', views.add_student, name='add_student'),
    path('edit/<int:matricule>/', views.edit_student, name='edit_student'),
    path('delete/<int:matricule>/', views.delete_student, name='delete_student'),
]
