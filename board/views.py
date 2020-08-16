from django.shortcuts import render, redirect
from django.http import HttpResponse
from board.models import Board, Player
from .forms import PlayersChoiceForm
from django.contrib import messages


def home(request):
	return render(request, 'board/date.html')

def resetGame(request):
	board = Board.objects.get(name="game")
	board.delete()

	board = Board.createAndInitBoard("game", 4)
	board.save()
	return redirect('/board/game')
	
def game(request):
	board = Board.objects.get(name="game")

	return render(request, 'board/test.html', {'grid': board.print_board(), 'nbTurns': board.nbTurns})

def moveDown(request, id):
	board=Board.objects.get(name="game")
	board.move(id, "down")

	return render(request, 'board/test.html', {'grid': board.print_board(), 'nbTurns': board.nbTurns})

def moveUp(request, id):
	board=Board.objects.get(name="game")
	board.move(id, "up")

	return render(request, 'board/test.html', {'grid': board.print_board(), 'nbTurns': board.nbTurns})
def moveLeft(request, id):
	board=Board.objects.get(name="game")
	board.move(id, "left")

	return render(request, 'board/test.html', {'grid': board.print_board(), 'nbTurns': board.nbTurns})

def moveRight(request, id):
	board=Board.objects.get(name="game")
	board.move(id, "right")

	return render(request, 'board/test.html', {'grid': board.print_board(), 'nbTurns': board.nbTurns})

def settings(request):
  if request.method == 'POST':
    form = PlayersChoiceForm(request.POST)

    if form.is_valid():
      print("Form is valid")

      p1 = form.cleaned_data.get('p1')
      p2 = form.cleaned_data.get('p2')

      print("p1 : " + str(p1))
      print("p2 : " + str(p2))

      print("Before if")
      
      if p1 == p2:
        messages.success(request, 'CANT PLAY WITH BOTH SAME PLAYER')
        return redirect('home')
      else:
        print("Entrée dans le else")
        board = Board.objects.get(name="game")
        
        board.p1 = p1
        board.p2 = p2

        print("Game(request)")
        return game(request)
  else: 
    form = PlayersChoiceForm()
  return render(request, 'users_auth/register.html', {'form': form})