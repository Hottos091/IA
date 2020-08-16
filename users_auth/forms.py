from django import forms

class NewPlayerForm(forms.Form):
  CHOICES = [('1', 'Human'), ('2', 'AI')]

  nickname = forms.CharField(label='Nickname', max_length=40)
  player_type = forms.ChoiceField(widget=forms.RadioSelect, choices=CHOICES)
