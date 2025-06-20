from django.urls import path
from api.views import support_view

urlpatterns=[
    path('submit_resignation/', support_view.submit_resignation, name="submit_resignation"),
    path('notification/',support_view.create_notification, name='notification')
]