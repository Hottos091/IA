from django.urls import path
from . import views

urlpatterns = [
    path('home', views.home, name='home'),
    path('game', views.game, name='game'),
    path('game/settings', views.settings, name='settings'),
    path('moveUp/<int:id>', views.moveUp, name='moveUp'),
    path('moveDown/<int:id>', views.moveDown, name='moveDown'),
    path('moveLeft/<int:id>', views.moveLeft, name='moveLeft'),
    path('moveRight/<int:id>', views.moveRight, name='moveRight'),
    path('game/resetGame', views.resetGame, name='reset'),
    path('settings', views.settings, name='settings')
]