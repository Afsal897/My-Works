from django.urls import path
from api.views import performance_view

urlpatterns=[
    path('performance_rating/',performance_view.submit_performance_rating,name='performance_rating'),
    path('edit_performance_rating/',performance_view.edit_performance_rating,name='edit_performance_rating'),
    path('delete_performance_rating/',performance_view.delete_performance_rating,name='delete_performance_rating'),
    path('team_feedback/',performance_view.submit_teammate_feedback,name='team_feedback'),
    path('edit_teammate_feedback/',performance_view.edit_teammate_feedback,name='edit_teammate_feedback'),
    path('delete_teammate_feedback/',performance_view.delete_teammate_feedback,name='delete_teammate_feedback'),
    path('list_performance_ratings/',performance_view.list_performance_ratings,name='list_performance_ratings'),
    path('list_teammate_feedback/',performance_view.list_teammate_feedback,name='list_teammate_feedback')
]