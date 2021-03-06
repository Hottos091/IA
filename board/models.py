from django.db import models
from django.contrib.postgres.fields import ArrayField
from django import template
from random import randrange
from django.contrib import messages
from django.shortcuts import redirect
from datetime import date
import datetime
import numpy as np
import pickle
import time
import os
import copy
import random


def get_lowest(open_set):
    lowest = open_set[0]
    for node in open_set[1:]:
        if node[2]+node[3] < lowest[2]+lowest[3]:
            lowest = node
    return lowest
        

def get_twin_node(match,set):
    for node in set:
        if node[0] == match[0] and node[1] == match[1]:
            return node
    return [-1, 0, 999999, 99999]  # set to inf inf don't exist, theorical max = 13 for 8x8


class Log(models.Model):
    id = models.AutoField(primary_key=True)
    details = models.CharField(max_length=255)

    def __str__(self):
        return self.details


class Player(models.Model):
    nickname = models.CharField(max_length=30)
    totalGames = models.IntegerField(null=True)
    isAI = models.BooleanField(default=True)
    ai = models.ForeignKey('AI', related_name="AI", on_delete=models.CASCADE, null=True)
    custom_lr = models.FloatField(null=True)
    custom_dr = models.FloatField(null=True)

    def __str__(self):
        return self.nickname+' : totalGames='+str(self.totalGames)+', AI : '+str(self.isAI)+' - AI DESC : '+str(self.ai)

    def init_ai(self, player_id):
        if(self.custom_dr or self.custom_lr):
            self.ai.start(player_id, self.custom_dr, 4, self.custom_lr)
        else:
            self.ai.start(player_id)

        self.ai.save()
        self.save()

        


class Board(models.Model):
    name = models.CharField(max_length=150)
    size = models.IntegerField(null=True)
    grid = ArrayField(ArrayField(models.IntegerField(null=True)), null=True)
    pos1 = ArrayField(models.IntegerField(null=True), null=True)
    pos2 = ArrayField(models.IntegerField(null=True), null=True)
    p1 = models.ForeignKey('Player', related_name="player1", null=True, on_delete=models.CASCADE)
    p2 = models.ForeignKey('Player', related_name="player2", null=True, on_delete=models.CASCADE)
    nbTurns = models.IntegerField(null=True)
    date = models.DateTimeField(null=True)
    
    def __str__(self):
        return self.name+'('+str(self.size)+')'

    def create_and_init_board(name, size):
        board = Board()
        board.name = name
        board.size = size
        board.reset_board()
        return board

    def reset_board(self):
        self.grid = [[0 for i in range(self.size)] for j in range(self.size)]
        self.grid[0][0] = 1
        self.grid[self.size - 1][self.size - 1] = 2
        self.pos1 = [0, 0]
        self.pos2 = [self.size - 1, self.size - 1]
        self.nbTurns = 0

    def is_in_grid(self, node):
        return (0 <= node[0] <= (self.size - 1)) and (0 <= node[1] <= (self.size - 1))

    def get_neighbors(self, node, remove=None):
        neighbors = []

        neighbors.append([node[0] - 1, node[1]]) if remove != "up" else ""  # up
        neighbors.append([node[0] + 1, node[1]]) if remove != "down" else ""  # down
        neighbors.append([node[0], node[1] - 1]) if remove != "left" else ""  # left
        neighbors.append([node[0], node[1] + 1]) if remove != "right" else ""  # right

        finals = []
        for node in neighbors:
            if self.is_in_grid(node):
                finals.append(node)  # why not removed()? cause doesn't worke with some specific nodes ex: [9,-1]
        return finals
    
    def print_board(self):
        if not self.end():
           
            row_id = 0
            output = "<table align='center'>"
            grid = self.grid
            for row in self.grid:
                output += "<tr>"
                col_id = 0
                for entry in row:
                    output += "<td"
                    if[row_id, col_id] in [self.pos1]:
                        self.grid[row_id][col_id] = 1
                        entry = 1
                    elif[row_id, col_id] in [self.pos2]:
                        self.grid[row_id][col_id] = 2
                        entry = 2
                    if entry == 1:
                        output += " class='joueur1'>"
                    elif entry == 2:
                        output += " class='joueur2'>"
                    else:
                        output += ">"
                    if[row_id, col_id] in [self.pos1, self.pos2]:
                        output += "|0|"
                    col_id += 1
                    output += "</td>"
                output += "</tr>"
                row_id += 1
            output += "</table>"
            self.grid = grid
            self.save()
            return output
        else:
            return self.end_game()

    def end_game(self):
        self.p1.totalGames += 1
        self.p2.totalGames += 1
        if self.p1.isAI:
            self.p1.ai.end(self)
            self.p1.ai.save()
        if self.p2.isAI:
            self.p2.ai.end(self)
            self.p2.ai.save()

        self.p1.save()
        self.p2.save()
        
        date = datetime.datetime.now()
        self.date = date
        self.name = ' '.join([self.p1.nickname, self.p2.nickname, str(date)])

        self.save()

    def move(self, id, direction):

        if direction not in self.get_moves(id):
            raise Exception("invalid direction given")
        directions = {"up": [-1, 0], "down": [1, 0], "left": [0, -1], "right": [0, 1]}

        if id == 1:
            self.pos1 = [self.pos1[0] + directions[direction][0], self.pos1[1] + directions[direction][1]]
            self.grid[self.pos1[0]][self.pos1[1]] = id
            new_pos = self.pos1
        else:
            self.pos2 = [self.pos2[0] + directions[direction][0], self.pos2[1] + directions[direction][1]]
            self.grid[self.pos2[0]][self.pos2[1]] = id
            new_pos = self.pos2

        if self.check_capture(direction, new_pos):
            self.capture(direction, new_pos)
        
        self.nbTurns += 1

    def check_capture(self, direction, new_pos):  # call only if move succesfull!

        if new_pos[0] in [0, self.size - 1] or new_pos[1] in [0, self.size - 1]:
            return True

        if direction == "up":  # improvement possible
            id1 = self.grid[new_pos[0] - 1][new_pos[1] - 1]
            id2 = self.grid[new_pos[0] - 1][new_pos[1]]
            id3 = self.grid[new_pos[0] - 1][new_pos[1] + 1]
        elif direction == "down":
            id1 = self.grid[new_pos[0] + 1][new_pos[1] - 1]
            id2 = self.grid[new_pos[0] + 1][new_pos[1]]
            id3 = self.grid[new_pos[0] + 1][new_pos[1] + 1]
        elif direction == "left":
            id1 = self.grid[new_pos[0] - 1][new_pos[1] - 1]
            id2 = self.grid[new_pos[0]][new_pos[1] - 1]
            id3 = self.grid[new_pos[0] + 1][new_pos[1] - 1]
        elif direction == "right":
            id1 = self.grid[new_pos[0] - 1][new_pos[1] + 1]
            id2 = self.grid[new_pos[0]][new_pos[1] + 1]
            id3 = self.grid[new_pos[0] + 1][new_pos[1] + 1]

        return self.grid[new_pos[0]][new_pos[1]] in [id1, id2, id3]

    def capture(self, direction, new_pos):
        opposite = {"up": "down", "down": "up", "left": "right", "right": "left"}

        id = self.grid[new_pos[0]][new_pos[1]]

        if id == 1:
            goal = self.pos2
        else:
            goal = self.pos1

        for node in self.get_neighbors(new_pos, opposite[direction]):
            captured, list_nodes = self.iscaptured(id, node, goal)
            if captured:
                for captured_node in list_nodes:
                    self.grid[captured_node[0]][captured_node[1]] = id

    def iscaptured(self, id, start, goal):
        # node struct: [coorY,coorX,G,H]
        # F = G+H
        # G = cost from the start node
        # H = heuristic cost ton the destination node
        start.append(0)
        start.append((start[0] - goal[0]) ** 2 + (start[1] - goal[1]) ** 2)
        open_set = [start]
        closed_set = []

        while open_set:
            current = get_lowest(open_set)
            if (current[0] == goal[0] and current[1] == goal[1]) or self.grid[current[0]][current[1]] not in [0, id]:  # look if arrived at destination or reach other player's territory
                return False, []  # found the target, not captured

            open_set.remove(current)
            closed_set.append(current)
            for node in self.get_neighbors(current):
                if get_twin_node(node, closed_set)[0] != -1 or self.grid[node[0]][node[1]] == id:  # skips, innacssible squarres and already checkeds ones
                    continue
                current_G = current[2] + 1

                twin = get_twin_node(node, open_set)
                if current_G < twin[3]:
                    node.append(current_G)
                    node.append((node[0] - goal[0]) ** 2 + (node[1] - goal[1]) ** 2)

                    if twin[0] != -1:
                        open_set.remove(twin)
                    open_set.append(node)

        # Open set is empty but goal was never reached
        return True, closed_set

    def end(self):
        for row in self.grid:
            for entry in row:
                if entry == 0:
                    return False
        return True

    def get_winner(self):
        owned = 0
        win_score = int(self.size ** 2 / 2)
        for row in self.grid:
            for entry in row:
                if entry == 1:
                    owned += 1
        if owned > win_score:
            return 1
        elif owned < win_score:
            return 2
        else:
            return 3
    
    def get_winner_name(self):
        winner = self.get_winner()

        output = "Victory goes to "
        if int(winner) == 1:
            output += self.p1.nickname
        elif int(winner) == 2:
            output += self.p2.nickname
        else:
            output = f"The two players ({self.p1.nickname} and {self.p2.nickname}) are even !"
        
        self.p1.save()
        self.p2.save()
        return output

    def get_moves(self, id):
        output = []
        if id == 1:
            pos = self.pos1
        else:
            pos = self.pos2

        temp_pos = [pos[0] - 1, pos[1]]
        if self.is_in_grid(temp_pos) and self.grid[temp_pos[0]][temp_pos[1]] in [0, id]:
            output += ["up"]

        temp_pos = [pos[0] + 1, pos[1]]
        if self.is_in_grid(temp_pos) and self.grid[temp_pos[0]][temp_pos[1]] in [0, id]:
            output += ["down"]

        temp_pos = [pos[0], pos[1] - 1]
        if self.is_in_grid(temp_pos) and self.grid[temp_pos[0]][temp_pos[1]] in [0, id]:
            output += ["left"]

        temp_pos = [pos[0], pos[1] + 1]
        if self.is_in_grid(temp_pos) and self.grid[temp_pos[0]][temp_pos[1]] in [0, id]:
            output += ["right"]

        return output

    def get_intresting_moves(self, id):
        output = []
        if id == 1:
            pos = self.pos1
        else:
            pos = self.pos2

        temp_pos = [pos[0] - 1, pos[1]]
        if self.is_in_grid(temp_pos) and self.grid[temp_pos[0]][temp_pos[1]] in [0]:
            output += ["up"]

        temp_pos = [pos[0] + 1, pos[1]]
        if self.is_in_grid(temp_pos) and self.grid[temp_pos[0]][temp_pos[1]] in [0]:
            output += ["down"]

        temp_pos = [pos[0], pos[1] - 1]
        if self.is_in_grid(temp_pos) and self.grid[temp_pos[0]][temp_pos[1]] in [0]:
            output += ["left"]

        temp_pos = [pos[0], pos[1] + 1]
        if self.is_in_grid(temp_pos) and self.grid[temp_pos[0]][temp_pos[1]] in [0]:
            output += ["right"]

        if output:
            return output
        else:
            return self.get_moves(id)

    def get_id(self):
        out = ""

        for row in self.grid:
            for elem in row:
                out += str(elem)
        for elem in self.pos1 + self.pos2:
            out += str(elem)
        return out

    def get_reward(self, player_id):
        reward = 0
        for row in self.grid:
            for entry in row:
                if entry == player_id:
                    reward += 1
                else:
                    reward -= 1
        return reward


class AI(models.Model):
    player = models.IntegerField(null=True)
    transitions = ArrayField(ArrayField(models.CharField(null=True, max_length=150)), null=True)
    discovery_rate = models.FloatField(null=True, default=1.0)
    learning_rate = models.FloatField(null=True, default=1.0)

    def __str__(self):
        return f"Player ID : {self.player} - DR : {self.discovery_rate} - LR : {self.learning_rate}"

    def start(self, player_id, discovery_rate=0.5, board_size=4, learning_rate=0):
        self.transitions = []
        self.player = player_id
        self.discovery_rate = discovery_rate or 0.5

        if learning_rate and learning_rate > 0:
            self.learning_rate = learning_rate
        else:
            self.learning_rate = get_learning_rate(board_size)

    def get_move(self, board):
        # first, add the new transition
        new_state = board.get_id()
        if not self.transitions:
            self.transitions = []
            # this is used cause of django giving a null for an empty list
        index = len(self.transitions)
        if index != 0:
            transition = self.transitions[index - 1]
            transition[1] = new_state
            self.transitions[index - 1] = transition

        # then, prepare the next transition
        new_transition = [new_state, None]
        self.transitions.append(new_transition)

        # After, chose between discovery or Action
        moves = board.get_moves(self.player)

        if random.random() < self.discovery_rate:
            # Discovery: Choose randomly between available moves
            self.save()
            moves = board.get_intresting_moves(self.player)
            return moves[randrange(len(moves))]

        # Action: Retreive the reward for the available moves
        best_move = None
        worste_reward = None
        for move in moves:
            copy_board = copy.deepcopy(board)
            copy_board.move(self.player, move)
            new_id = copy_board.get_id()
            state = get_state(new_id)
            if state:
                reward = state.get_reward()
                if not worste_reward:
                    worste_reward = reward
                    best_move = move
                elif reward < worste_reward:
                    worste_reward = reward
                    best_move = move
        if not best_move:
            moves = board.get_intresting_moves(self.player)
            best_move = moves[randrange(len(moves))]
        self.save()
        return best_move
        # Action: return the value with the LOWEST reward
        # As we went the opposite side to have the baddest possible state

    def end(self, board):
        # first, we finalise the transitions
        self.transitions = self.transitions[:-1]
        index = len(self.transitions)
        transition = self.transitions[index - 1]
        last_state = transition[1]

        # then, we add the first reward.
        final_state = get_state(last_state)
        if not final_state:
            final_state = State(state_id=last_state, board_size=board.size)
            final_state.set_reward(board.get_reward(self.player))
            final_state.save()

        next_state = final_state
        # after, we start to back spread.
        for i in range(len(self.transitions) - 1, -1, -1):
            transition = self.transitions[i]
            previous_state = get_state(transition[0])
            if not previous_state:
                previous_state = State(state_id=transition[0], board_size=board.size)
            previous_state.value_function(self.learning_rate, next_state.get_reward())
            previous_state.save()
            next_state = previous_state


class State(models.Model):
    state_id = models.CharField(max_length=150, primary_key=True, default=-1)
    reward = models.FloatField(null=True, default=0.0)
    board_size = models.IntegerField(null=True, default=4)

    def get_reward(self):
        return self.reward

    def set_reward(self, reward):
        self.reward = reward

    def value_function(self, learning_rate, new_reward):
        self.reward = self.reward + (learning_rate * new_reward)


def get_state(id):
    result = State.objects.filter(state_id=id)
    if len(result) > 0:
        return result[0]
    return False


def get_learning_rate(board_size):
    # this is an appreciation of a dynamic learning rate
    # could be optimised by storing the number of created state for each board size
    return len(State.objects.filter(board_size=board_size)) / ((board_size ** 2) ** 3)


def dumbIA(board, id):
    moves = board.get_intresting_moves(id)
    if not moves:
        moves = board.get_moves(id)
    return moves[randrange(len(moves))]
