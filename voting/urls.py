from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('vote/', views.ballot, name='ballot'),
    path('results/', views.results, name='results'),
    path('register/', views.register, name='register'),
]