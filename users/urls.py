from django.urls import path
from . import views

app_name = 'users'
urlpatterns = [
    path('<int:pk>/', views.UserDetailView.as_view(), name='user'),
]
