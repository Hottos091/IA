from django.shortcuts import render, redirect
from .forms import NewPlayerForm
from django.contrib import messages
from board.models import Player, AI

# Create your views here.
def register(request):
  if request.method == 'POST':
    form = NewPlayerForm(request.POST)

    if form.is_valid():
      nickname = form.cleaned_data.get('nickname')
      player_type = form.cleaned_data.get('player_type')

      print("(str)Player TYPE : " + str(player_type))
      print("Type Player TYPE : " + str(type(player_type)))
      new_player = Player(nickname=nickname, totalGames=0)
      if player_type == "2":
        print(" THIS DUDE AN AI ")
        ai = AI()
        ai.start(2)
        ai.save()

        new_player.isAI = True
        new_player.ai = ai
        
        new_player.ai.save()
        new_player.save()
      else:
        new_player.isAI = False
      

      print(new_player)
      new_player.save()

      print("New Player is now saved in DB")
      messages.success(request, f'Player created : {nickname} !')
      return redirect('home')
  else: 
    form = NewPlayerForm()
  return render(request, 'users_auth/register.html', {'form': form})
