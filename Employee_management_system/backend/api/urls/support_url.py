from django.urls import path
from api.views import support_view

urlpatterns=[
    path('submit_resignation/', support_view.submit_resignation, name="submit_resignation"),
    path('withdraw_resignation/',support_view.withdraw_resignation, name='withdraw resignation'),
    path('notification/',support_view.create_notification, name='notification'),
    path('get_my_notifications/',support_view.get_my_notifications, name='get_my_notifications'),
    path('list_resignations/',support_view.list_resignations, name='list_resignations'),
]