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

    currentPlayerId = board.nbTurns%2 + 1
    if currentPlayerId == 1:
        currentPlayer = board.p1
        isCurrentPlayerAI = board.p1.isAI
    else: 
        currentPlayer = board.p2
        isCurrentPlayerAI = board.p2.isAI

    if isCurrentPlayerAI:
        best_ai_move = currentPlayer.ai.get_move(board)
        print("===============BEST MOVE================ : " +str(best_ai_move))



    print(f"Player 1 : {board.p1} - Player 2 : {board.p2}")

    return render(request, 'board/test.html', {'grid': board.print_board(), 'nbTurns': board.nbTurns})


def moveDown(request, id):
    board = Board.objects.get(name="game")
    board.move(id, "down")

    return render(request, 'board/test.html', {'grid': board.print_board(), 'nbTurns': board.nbTurns})


def moveUp(request, id):
    board = Board.objects.get(name="game")
    board.move(id, "up")

    return render(request, 'board/test.html', {'grid': board.print_board(), 'nbTurns': board.nbTurns})


def moveLeft(request, id):
    board = Board.objects.get(name="game")
    board.move(id, "left")

    return render(request, 'board/test.html', {'grid': board.print_board(), 'nbTurns': board.nbTurns})


def moveRight(request, id):
    board = Board.objects.get(name="game")
    board.move(id, "right")

    return render(request, 'board/test.html', {'grid': board.print_board(), 'nbTurns': board.nbTurns})


def settings(request):
    if request.method == 'POST':
        form = PlayersChoiceForm(request.POST)

        if form.is_valid():
            p1 = form.cleaned_data.get('p1')
            p2 = form.cleaned_data.get('p2')
            print("p1 : " + str(p1))
            print("p2 : " + str(p2))
            if p1 == p2:
                messages.success(request, 'You cannot play with both the same player')
                return redirect('home')
            else:
                if(p1.isAI):
                    print("P1 AI is starting...")
                    p1.ai.player = 1
                    p1.ai.save()
                    p1.save()
                    print("Started.")
                if(p2.isAI):
                    print("P2 AI is starting...")
                    p2.ai.player = 2
                    p2.ai.save()
                    p2.save()
                    print("Started.")

            board = Board.objects.get(name="game")

            board.p1 = p1
            board.p2 = p2
            board.save()
            return game(request)
    else:
        form = PlayersChoiceForm()
        return render(request, 'users_auth/register.html', {'form': form})
