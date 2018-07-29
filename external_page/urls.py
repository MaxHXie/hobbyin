from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('terms_of_use/', views.terms_of_use, name="terms_of_use"),
    path('integrity/', views.integrity, name="integrity"),
    path('instructors/<str:hobby_name>/', views.instructors, name="instructors"),
    path('profile/', views.my_profile, name="my_profile"),
    path('profile/<int:user_id>/', views.profile_with_user, name="profile_with_user"),
    path('profile/<int:user_id>/<str:hobby>/', views.profile_with_user_hobby, name="profile_with_user_hobby"),
    path('edit_profile/', views.edit_profile, name="edit_profile"),
    path('settings/', views.settings, name="settings"),
    path('logout/', views.logout, name="logout"),
    path('instructor_signup/', views.InstructorSignUp.as_view(), name='instructor_signup'),
    path('customer_signup/', views.CustomerSignUp.as_view(), name='customer_signup'),
    path('send_instructor_message/<int:user_id>/<str:hobby>/', views.send_instructor_message, name='send_instructor_message'),
    path('follow/', views.follow_instructor, name="follow_instructor"),
    path('unfollow/', views.unfollow_instructor, name="unfollow_instructor"),
]
