from django import forms
from board.models import Player

class PlayersChoiceForm(forms.Form):
  p1 = forms.ModelChoiceField(queryset=Player.objects.all())
  p2 = forms.ModelChoiceField(queryset=Player.objects.all())