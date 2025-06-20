from django.urls import path
from api.views import performance_view

urlpatterns=[
    path('performance_rating/',performance_view.submit_performance_rating,name='performance_rating'),
    path('team_feedback/',performance_view.submit_teammate_feedback,name='team_feedback')
]