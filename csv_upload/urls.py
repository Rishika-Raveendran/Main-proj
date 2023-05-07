from django.urls import path
from . import views

urlpatterns = [
    path('', views.upload_csv, name='upload_csv'),
    path('<str:pk>/', views.upload_csv, name='upload_csv'),
    
]
