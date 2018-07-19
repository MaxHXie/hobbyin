from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('terms_of_use/', views.terms_of_use, name="terms_of_use"),
    path('instructors/<str:hobby_name>/', views.instructors, name="instructors"),
    path('profile/', views.my_profile, name="my_profile"),
    path('profile/<int:user_id>/', views.profile_with_user, name="profile_with_user"),
    path('profile/<int:user_id>/<str:hobby>/', views.profile_with_user_hobby, name="profile_with_user_hobby"),
    path('edit_profile/', views.edit_profile, name="edit_profile"),
    path('settings/', views.settings, name="settings"),
    path('logout/', views.logout, name="logout"),
]
