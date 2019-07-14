from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

app_name = 'letters'
urlpatterns = [
                  path('', views.index, name='index'),
                  path('login/', views.login, name='login'),
                  path('logout/', views.logout, name='logout'),
                  path('letters/', views.letters, name='letters'),
                  path('letters/<int:student_id>/<int:letter_id>/', views.letter_detail, name='letter_detail'),
                  path('letters/<int:student_id>/<int:letter_id>/confirm/', views.letter_detail, {'confirmation': True},
                       name='letter_confirm'),
                  path('letters/results/<int:letter_id>/', views.letter_result, name='letter_result')
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# Allow uploaded files to be served as static files. Should be changed when going into production.
