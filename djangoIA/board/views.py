from django.shortcuts import render, redirect
from django.http import HttpResponse
from board.models import Board

def home(request):
	return HttpResponse("""
			<h1>IA VS. Human</h1>

		""")

def resetGame(request):
	board = Board.objects.get(name="game")
	board.delete()

	board = Board.createAndInitBoard("game", 8)
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