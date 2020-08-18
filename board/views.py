from django.shortcuts import render, redirect
from django.http import HttpResponse
from board.models import Board, Player
from .forms import PlayersChoiceForm
from django.contrib import messages
import time


def home(request):
    return render(request, 'board/home.html')


def resetGame(request):
    board = Board.objects.get(name="game")
    p1 = board.p1
    p2 = board.p2
    board.delete()

    board = Board.create_and_init_board("game", 4)
    board.p1 = p1
    board.p2 = p2
    board.save()

    return redirect('/board/game')

def game(request):
    board_set = Board.objects.filter(name="game")
    if len(board_set) < 1:
        last_board = Board.objects.latest('date')
        board = Board.create_and_init_board("game", 4)
        board.save()
        messages.success(request, last_board.get_winner_name())
        return redirect('/board/home')
    else:
        board = board_set[0]

    if board.p1 and board.p2:
        currentPlayerId = board.nbTurns%2 + 1
        if currentPlayerId == 1:
            currentPlayer = board.p1
            isCurrentPlayerAI = board.p1.isAI
        else:
            currentPlayer = board.p2
            isCurrentPlayerAI = board.p2.isAI

        if isCurrentPlayerAI:
            best_ai_move = currentPlayer.ai.get_move(board)
            print("===============BEST MOVE================ : " + str(best_ai_move))
            board.move(currentPlayerId, str(best_ai_move))
            time.sleep(0.5)
        
            


        print(f"Player 1 : {board.p1} - Player 2 : {board.p2}")

    return render(request, 'board/test.html', {'grid': board.print_board(), 'nbTurns': board.nbTurns, 'board': board})

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
                messages.error(request, 'You cannot play with both the same player')
                return redirect('/board/game/settings')
            else:
                if(p1.isAI):
                    print("P1 AI is starting...")
                    print("========P1======", p1.ai,"================")
                    p1.initAI(1)
                    print("======P1========", p1.ai,"================")


                    

                    print("Started.")
                if(p2.isAI):
                    print("P2 AI is starting...")
                    print("=======P2=======", p2.ai,"================")
                    p2.initAI(2)
                    print("=======P2=======", p2.ai,"================")

                    print("Started.")

            board_set = Board.objects.filter(name="game")
            if len(board_set) < 1:
                board = Board.create_and_init_board("game", 4)
                board.save()
            else:
                board = board_set[0]

            board.p1 = p1
            board.p2 = p2
            board.save()
            return redirect('game')
    else:
        form = PlayersChoiceForm()
        return render(request, 'board/settings.html', {'form': form})

    