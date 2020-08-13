from django.db import models
from django.contrib.postgres.fields import ArrayField
from django import template
from colorama import Fore, Back, Style
from random import randrange
import pickle
import os
import copy
import time
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
    return [-1,0,999999,99999] #set to inf inf don't exist, theorical max = 13 for 8x8
        

class Board(models.Model):
    size = models.IntegerField
    grid = ArrayField(
        ArrayField(
            models.IntegerField,
            size=8,
        ),
    )
    pos1 = ArrayField(
        models.IntegerField,
        size = 2,
    )
    pos2 = ArrayField(
        models.IntegerField,
        size = 2,
    )

    def __init__(self,size):
        self.size = size
        self.grid = [[0 for i in range(size)]for j in range(size)]
        self.pos1 = [0,0]
        self.pos2 = [size-1,size-1]
        self.grid[0][0] = 1
        self.grid[size-1][size-1] = 2

    def __str__(self):
        return "ouais"
    
       
    def is_in_grid(self,node):
        return (0<=node[0]<=(self.size-1)) and (0<=node[1]<=(self.size-1))
    
    def get_neighbors(self,node,remove=None):
        neighbors = []
    
        neighbors.append([node[0]-1,node[1]]) if remove != "up" else ""     #up
        neighbors.append([node[0]+1,node[1]]) if remove != "down" else ""   #down
        neighbors.append([node[0],node[1]-1]) if remove != "left" else ""   #left
        neighbors.append([node[0],node[1]+1]) if remove != "right" else ""  #right
        
        finals=[]
        for node in neighbors:
            if self.is_in_grid(node):
                finals.append(node)   #why not removed()? cause doesn't worke with some specific nodes ex: [9,-1]
        return finals
    
    def print_board(self):
        row_id = 0
        for row in self.grid:
            output=""
            col_id = 0
            for entry in row:
                if self.pos1 == [row_id,col_id] or self.pos2 == [row_id,col_id]:
                    txt = '|O|'
                else:
                    txt = '   '
            
                if entry == 1:
                    output+= Back.BLUE+txt+Style.RESET_ALL
                elif entry ==2:
                    output+= Back.RED+txt+Style.RESET_ALL
                else:
                    output+= txt
                if col_id<self.size-1:
                    output+= Back.BLACK+' '+Style.RESET_ALL
                col_id+=1
            return(output)
            if row_id<self.size-1:
                print(Back.BLACK+(' '*(4*self.size-1))+Style.RESET_ALL)
            row_id+=1
    
    
    def printBoard(self):
        row_id = 0
        totalOutput = ""
        for row in self.grid:
            output=""
            col_id = 0
            for entry in row:
                if self.pos1 == [row_id,col_id] or self.pos2 == [row_id,col_id]:
                    txt = '|O|'
                else:
                    txt = '   '
            
                if entry == 1:
                    output+= Back.BLUE+txt+Style.RESET_ALL
                elif entry ==2:
                    output+= Back.RED+txt+Style.RESET_ALL
                else:
                    output+= txt
                if col_id<self.size-1:
                    output+= Back.BLACK+' '+Style.RESET_ALL
                col_id+=1
            print(output)
            totalOutput +=output
            if row_id<self.size-1:
                test = Back.BLACK+(' '*(4*self.size-1))+Style.RESET_ALL
                print(Back.BLACK+(' '*(4*self.size-1))+Style.RESET_ALL)
                totalOutput+='\n'+test+'\n'
            row_id+=1
        return totalOutput
    



    def get_moves(self, direction):
        directions = {"up":[0,-1],"down":[0,1],"left":[-1,0],"right":[1,0]}
        #directions = {"up":[-1,0],"down":[1,0],"left":[0,-1],"right":[0,1]}
        return directions[direction]

    def move(self,id,direction):
        #Direction is received as an array of characters. I translate it into a string to use it easier
        log = "\nCoordonnées de base : " + str(self.pos2) + "\n"
        directionString = ''.join(direction)
        coordMove = self.get_moves(directionString)
        log += "CoordMove : " + str(coordMove) + "\n"
        #if not direction in self.get_moves(self, id):
        #    raise Exception("invalid direction given")
        #directions = {"up":[-1,0],"down":[1,0],"left":[0,-1],"right":[0,1]}
        log += "Changement de position du joueur : \n"

        new_pos = 0 #initiate variable out of scope

        if id == 2:
            log+= "Calcul coord : " + str(self.pos2[0]) + "+" +  str(coordMove[0]) + "\n"
            log+= "Calcul coord : " + str(self.pos2[1]) + "+" +  str(coordMove[1]) + "\n"

            self.pos2[0]+=coordMove[0]
            self.pos2[1]+=coordMove[1]
            new_pos = self.pos2

            log += "New pos : " + str(new_pos) +  "\n"
        else:
            self.pos2 = [self.pos2[0]+directions[direction][0] , self.pos2[1]+directions[direction][1]]
            self.grid[self.pos2[0]][self.pos2[1]]= id
            new_pos = self.pos2
            
        log += "Changement effectué.\n"
        log+= "Vérification des captures\n"
        if self.check_capture(direction,new_pos):
            log += "Capture en cours...\n"
            self.capture(direction,new_pos)
            log += "Capture terminée.\n"

        log += str(self.pos2) + "\n"
        board.save()
        return log



    def moveLeft():
        Board.move(boardTest, 1, "left");
    def moveRight():
        Board.move(boardTest, 1, "right");
    def moveUp():
        Board.move(boardTest, 1, "up");
    def moveDown():
        Board.move(boardTest, 1, "down");
    
    
"""
    def check_capture(self,direction,new_pos): #call only if move succesfull!
        
        if new_pos[0] in [0,self.size-1] or new_pos[1] in [0,self.size-1]:
            return True
        
        if direction == "up":    #improvement possible
            id1 = self.grid[new_pos[0]-1][new_pos[1]-1]
            id2 = self.grid[new_pos[0]-1][new_pos[1]]
            id3 = self.grid[new_pos[0]-1][new_pos[1]+1]
        elif direction == "down":
            id1 = self.grid[new_pos[0]+1][new_pos[1]-1]
            id2 = self.grid[new_pos[0]+1][new_pos[1]]
            id3 = self.grid[new_pos[0]+1][new_pos[1]+1]
        elif direction == "left":
            id1 = self.grid[new_pos[0]-1][new_pos[1]-1]
            id2 = self.grid[new_pos[0]][new_pos[1]-1]
            id3 = self.grid[new_pos[0]+1][new_pos[1]-1]
        elif direction == "right":
            id1 = self.grid[new_pos[0]-1][new_pos[1]+1]
            id2 = self.grid[new_pos[0]][new_pos[1]+1]
            id3 = self.grid[new_pos[0]+1][new_pos[1]+1]
            
        return self.grid[new_pos[0]][new_pos[1]] in [id1,id2,id3]
    
    def capture(self,direction,new_pos):
        opposite ={"up":"down","down":"up","left":"right","right":"left"}
        
        id = self.grid[new_pos[0]][new_pos[1]]
        
        if id == 1:
            goal = self.pos2
        else:
            goal = self.pos1
            
        for node in self.get_neighbors(new_pos,opposite[direction]):
            captured,list_nodes=self.iscaptured(id,node,goal)
            if captured:
                for captured_node in list_nodes:
                    self.grid[captured_node[0]][captured_node[1]]= id
            
        
    def iscaptured(self,id,start,goal):
        #node struct: [coorY,coorX,G,H]
        #F = G+H
        #G = cost from the start node
        #H = heuristic cost ton the destination node
        start.append(0)
        start.append((start[0]-goal[0])**2+(start[1]-goal[1])**2)
        open_set = [start]
        closed_set = []

        while open_set != []:
            current = get_lowest(open_set)
            if (current[0] == goal[0] and current[1] == goal[1]) or self.grid[current[0]][current[1]]not in [0,id]: #look if arrived at destination or reach other player's territory
                return False,[] #found the target, not captured

            open_set.remove(current)
            closed_set.append(current)
            for node in self.get_neighbors(current):
                if get_twin_node(node,closed_set)[0]!=-1 or self.grid[node[0]][node[1]] == id: #skips, innacssible squarres and already checkeds ones
                    continue
                current_G = current[2]+1
                
                twin = get_twin_node(node,open_set)
                if current_G < twin[3]:
                    node.append(current_G)
                    node.append((node[0]-goal[0])**2+(node[1]-goal[1])**2)
                    
                    if twin[0] != -1:
                        open_set.remove(twin)
                    open_set.append(node)

        # Open set is empty but goal was never reached
        return True,closed_set
    
    def end(self):
        for row in self.grid:
            for entry in row:
                if entry == 0:
                    return False
        return True
    
    def get_winner(self):
        owned=0
        win_score = int(self.size**2/2)
        for row in self.grid:
            for entry in row:
                if entry == 1:
                    owned+=1
        if owned >win_score:    
            return 1
        elif owned <win_score:
            return 2
        else:
            return 3
    
    def get_moves_ia(self,id, third):
        output = []
        if id == 1:
            pos = self.pos1
        else:
            pos = self.pos2
            
        temp_pos = [pos[0]-1,pos[1]]
        if self.is_in_grid(temp_pos)and self.grid[temp_pos[0]][temp_pos[1]] in [0,id]:
            output+=["up"]
            
        temp_pos = [pos[0]+1,pos[1]]
        if self.is_in_grid(temp_pos)and self.grid[temp_pos[0]][temp_pos[1]] in [0,id]:
            output+=["down"]
            
        temp_pos = [pos[0],pos[1]-1]
        if self.is_in_grid(temp_pos)and self.grid[temp_pos[0]][temp_pos[1]] in [0,id]:
            output+=["left"]
            
        temp_pos = [pos[0],pos[1]+1]
        if self.is_in_grid(temp_pos)and self.grid[temp_pos[0]][temp_pos[1]] in [0,id]:
            output+=["right"]
            
        return output
    
    
    def get_intresting_moves(self,id):
        output = []
        if id == 1:
            pos = self.pos1
        else:
            pos = self.pos2
            
        temp_pos = [pos[0]-1,pos[1]]
        if self.is_in_grid(temp_pos)and self.grid[temp_pos[0]][temp_pos[1]] in [0]:
            output+=["up"]
            
        temp_pos = [pos[0]+1,pos[1]]
        if self.is_in_grid(temp_pos)and self.grid[temp_pos[0]][temp_pos[1]] in [0]:
            output+=["down"]
            
        temp_pos = [pos[0],pos[1]-1]
        if self.is_in_grid(temp_pos)and self.grid[temp_pos[0]][temp_pos[1]] in [0]:
            output+=["left"]
            
        temp_pos = [pos[0],pos[1]+1]
        if self.is_in_grid(temp_pos)and self.grid[temp_pos[0]][temp_pos[1]] in [0]:
            output+=["right"]
            
        return output
    
    def get_id(self):
        out = ""
        
        for row in self.grid:
            for elem in row:
                out += str(elem)
        for elem in self.pos1+self.pos2:
            out += str(elem)
        return out
    
    def getBoard():
        return boardTest

"""