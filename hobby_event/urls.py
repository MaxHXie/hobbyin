from django.urls import path, include
from . import views

urlpatterns = [
    path('create_event/', views.create_event, name="create_event"),
    path('event_terminal/<int:event_id>/', views.create_event_terminal, name="create_event_terminal"),
    path('single_event/<int:event_id>/', views.single_event, name="single_event"),
    path('all_events/', views.all_events, name="all_events"),
    path('edit_event/<int:event_id>/', views.edit_event, name="edit_event"),
    path('my_events/', views.my_events, name="my_events"),
    path('event_participators/<int:event_id>/', views.event_participators, name="event_participators"),
    path('hide_show_event/<int:event_id>/', views.hide_show_event, name="hide_show_event"),
    path('signup_for_event/<int:event_id>', views.signup_for_event, name="signup_for_event")
]
