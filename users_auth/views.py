from django.shortcuts import render, redirect
from .forms import NewPlayerForm
from django.contrib import messages
from board.models import Player

# Create your views here.
def register(request):
  if request.method == 'POST':
    form = NewPlayerForm(request.POST)

    if form.is_valid():
      print("Form is valid")

      nickname = form.cleaned_data.get('nickname')
      player_type = form.cleaned_data.get('player_type')

      print("(str)Player TYPE : " + str(player_type))
      print("Type Player TYPE : " + str(type(player_type)))
      new_player = Player(nickname=nickname, totalGames=0)
      if player_type == "2":
        new_player.isAI = True
      else:
        new_player.isAI = False

      new_player.save()
      print("New Player is now saved in DB")
      messages.success(request, f'Player created : {nickname} !')
      return redirect('home')
  else: 
    form = NewPlayerForm()
  return render(request, 'users_auth/register.html', {'form': form})
