from django.urls import path
from . import views

app_name = 'letters'
urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('letters/', views.letters, name='letters'),
    path('letters/<int:letter_id>/', views.letter_detail, name='letter_detail'),
]
