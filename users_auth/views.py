from django.shortcuts import render, redirect
from .forms import NewPlayerForm, EditPlayerForm
from django.contrib import messages
from board.models import Player, AI


def register(request):
    if request.method == 'POST':
        form = NewPlayerForm(request.POST)

        if form.is_valid():
            nickname = form.cleaned_data.get('nickname')
            player_type = form.cleaned_data.get('player_type')

            new_player = Player(nickname=nickname, totalGames=0)
            if player_type == "2":
                if(request.POST['dr']):
                    dr = float(request.POST['dr'])
                    new_player.custom_dr = dr
                if(request.POST['lr']):
                    lr = float(request.POST['lr'])
                    new_player.custom_lr = lr
                
                ai = AI()
                new_player.ai = ai

                new_player.init_ai(0)
                new_player.ai = ai

                ai.save()
                new_player.isAI = True
                new_player.save()
            else:
                new_player.isAI = False
            new_player.save()

            print("New player is now saved in DB")
            messages.success(request, f'Player created : {nickname} !')
            return redirect('home')
    else:
        form = NewPlayerForm()
    return render(request, 'users_auth/register.html', {'form': form})

def edit(request):
    if request.method == 'POST':
        form = EditPlayerForm(request.POST)

        if form.is_valid():
            updated_player = form.cleaned_data.get('players')
            updated_player.nickname = form.cleaned_data.get('new_nickname')
            
            updated_player_type = form.cleaned_data.get('player_type')
            if updated_player_type == "2":
                if(request.POST['dr']):
                    dr = float(request.POST['dr'])
                    updated_player.custom_dr = dr
                if(request.POST['lr']):
                    lr = float(request.POST['lr'])
                    updated_player.custom_lr = lr

                ai = AI()
                updated_player.ai = ai


                updated_player.init_ai(0)
                updated_player.ai = ai

                updated_player.isAI = True
            else:
                updated_player.isAI = False
                if(updated_player.ai != None):
                    updated_player.ai.delete()
                    updated_player.ai = None

            updated_player.save()

            print("Player has been updated into the DB")
            messages.success(request, f'Player updated: {updated_player.nickname} !')
            return redirect('home')
    else:
        form = EditPlayerForm()
    return render(request, 'users_auth/register.html', {'form': form})

