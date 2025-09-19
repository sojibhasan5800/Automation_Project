
from django.urls import path,include
from . import views


urlpatterns = [
   path('' , views.tictac_home , name="tictac_home"),
   path('play/<room_code>' , views.tictac_play , name="play"),

]
