from django.urls import path
from . import views
urlpatterns = [
    path('register/', views.user_registration_view, name='user_register'),
    path('login/', views.user_login_view, name='user_login'),
]
