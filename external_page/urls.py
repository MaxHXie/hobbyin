from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('instructors/<str:hobby_name>/', views.instructors, name="instructors"),
    path('profile/<int:instructor_id>', views.profile, name="profile"),
]
