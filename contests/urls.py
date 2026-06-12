from django.urls import path

from . import views

app_name = 'contests'

urlpatterns = [
    path('', views.groups, name='groups'),
    path('create/', views.create_group, name='create_group'),
    path('<int:group_id>/join/', views.request_join, name='request_join'),
    path('requests/<int:membership_id>/approve/', views.approve_membership, name='approve_membership'),
    path('requests/<int:membership_id>/reject/', views.reject_membership, name='reject_membership'),
]
