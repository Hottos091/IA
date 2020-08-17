from django import forms
from board.models import Player


class NewPlayerForm(forms.Form):
    CHOICES = [('1', 'Human'), ('2', 'AI')]

    nickname = forms.CharField(label='Nickname', max_length=150)
    player_type = forms.ChoiceField(widget=forms.RadioSelect, choices=CHOICES)


class EditPlayerForm(forms.Form):
    CHOICES = [('1', 'Human'), ('2', 'AI')]

    players = forms.ModelChoiceField(queryset=Player.objects.all())
    new_nickname = forms.CharField(label='New nickname', max_length=150)
    new_player_type = forms.ChoiceField(widget=forms.RadioSelect, choices=CHOICES)
