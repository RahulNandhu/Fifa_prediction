from django.urls import path

from . import views

app_name = 'matches'

urlpatterns = [
    path('', views.upcoming, name='upcoming'),
    path('create/', views.create_fixture, name='create_fixture'),
    path('<int:fixture_id>/publish/', views.publish_fixture, name='publish_fixture'),
    path('<int:fixture_id>/edit/', views.edit_fixture, name='edit_fixture'),
    path('<int:fixture_id>/delete/', views.delete_fixture, name='delete_fixture'),
    path('match/<int:match_id>/unpublish/', views.unpublish_match, name='unpublish_match'),
    path('results/', views.submit_results, name='submit_results'),
]
