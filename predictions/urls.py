from django.urls import path

from . import views

app_name = 'predictions'

urlpatterns = [
    path('mine/', views.my_predictions, name='my_predictions'),
    path('<int:match_id>/predict/', views.predict, name='predict'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('points/', views.manage_points, name='manage_points'),
    path('leader-taunt/', views.leader_taunt, name='leader_taunt'),
]
