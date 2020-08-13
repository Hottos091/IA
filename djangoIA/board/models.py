from django.db import models
from django.contrib.postgres.fields import ArrayField
from django import template
from random import randrange
import numpy as np
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
class Log(models.Model):
    id = models.AutoField(primary_key=True)
    details = models.CharField(max_length=255)

    def __str__(self):
        return self.details
class Board(models.Model):
    name = models.CharField(max_length=25)
    size = models.IntegerField(null=True)
    grid = ArrayField(ArrayField(models.IntegerField(null=True)), null=True)
    pos1 = ArrayField(models.IntegerField(null=True), null=True)
    pos2 = ArrayField(models.IntegerField(null=True), null=True)
    nbTurns = models.IntegerField(null=True)
    
    def __str__(self):
        return self.name

    def createAndInitBoard(name, size):
        board = Board()
        board.name = name
        board.size = size
        board.grid = [[0 for i in range(board.size)]for j in range(board.size)]
        board.grid[0][0] = 1
        board.grid[board.size-1][board.size-1] = 2
        board.pos1 = [0,0]
        board.pos2 = [7,7]
        board.nbTurns = 0
        return board

    def is_in_grid(self,node):
        return (0<=node[0]<=(self.size-1)) and (0<=node[1]<=(self.size-1))
    def get_neighbors(self,node,remove=None):
        neighbors = []
    
        neighbors.append([node[0]-1,node[1]]) if remove != "up" else ""     #up
        neighbors.append([node[0]+1,node[1]]) if remove != "down" else ""   #down
        neighbors.append([node[0],node[1]-1]) if remove != "left" else ""   #left
        neighbors.append([node[0],node[1]+1]) if remove != "right" else ""  #right
        
        finals=[]
        for nodeN in neighbors:
            if self.is_in_grid(nodeN):
                finals.append(nodeN)   #why not removed()? cause doesn't worke with some specific nodeNs ex: [9,-1]
        return finals
    
    def print_board(self):
        if not self.end():
           
            row_id = 0
            output = "<table>"
            grid = self.grid
            for row in self.grid:
                output+="<tr>"
                col_id = 0
                for entry in row:
                    output+="<td"
                    if([row_id, col_id] in [self.pos1]):
                        self.grid[row_id][col_id]=1
                        entry=1
                    elif([row_id, col_id] in [self.pos2]):
                        self.grid[row_id][col_id]=2
                        entry=2
                    if entry == 1:
                        output+= " class='joueur1'>"
                    elif entry ==2:
                        output+= " class='joueur2'>"
                    else:
                        output += ">"
                    if([row_id, col_id] in [self.pos1, self.pos2]):
                        output+= "|0|"
                    col_id+=1
                    output+="</td>"
                output+="</tr>"
                row_id+=1
            output+="</table>"
            self.grid = grid
            self.save()
            return output
        else:
            return "<p>Le match est terminé ! Veuillez réinitialiser le jeu !</p>"
            
            
             
    def check_capture(self,new_pos): #call only if move succesfull!
        
        if new_pos[0] in [0,self.size-1] or new_pos[1] in [0,self.size-1]:
            return True
        
       
    
    def capture(self,direction,new_pos):
        opposite ={"up":"down","down":"up","left":"right","right":"left"}
        
        id = self.grid[new_pos[0]][new_pos[1]]
        
        if id == 1:
            goal = self.pos2
        else:
            goal = self.pos1
            
        for node in self.get_neighbors(new_pos, opposite[direction]):
            captured,list_nodes=self.iscaptured(id,node,goal)
            if captured:
                for captured_node in list_nodes:
                    self.grid[captured_node[0]][captured_node[1]]= id
                    self.save()
            
        
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
    def move(self,id,direction):
        directions = {"up":[-1,0],"down":[1,0],"left":[0,-1],"right":[0,1]}
        coordMove = directions[direction]
        log = Log()

        if id == 1:
            pos = self.pos1
        else : 
            pos = self.pos2

        temp_pos = [pos[0]+coordMove[0], pos[1]+coordMove[1]]

        if (direction not in self.get_moves(id)):
            log.details += "\tERROR:MOUVEMENT EN DEHORS DE LA GRILLE"
        else:
            if id == 1:
                self.pos1 = temp_pos                
            else: 
                self.pos2 = temp_pos
            self.save()
            if self.check_capture(temp_pos):
                self.capture(direction,temp_pos)
                log.details += "\tTEMPPOS : " + str(temp_pos)
            
            log.details += "\tSUCCESS:MOUVEMENT AUTORISE"
            
        log.save()
        self.nbTurns+=1
        self.save()
    def get_nbTurns(self):
        return self.nbTurns
    def get_moves(self,id):
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

class Node(models.Model):
    idNode = models.AutoField(primary_key=True)
    typeNode = models.CharField(max_length=20, null=True)
    up = models.IntegerField(null=True)
    down = models.IntegerField(null=True)
    left = models.IntegerField(null=True)
    right = models.IntegerField(null=True)
    p1 = models.DecimalField(max_digits=18, decimal_places=16)
    p2 = models.DecimalField(max_digits=18, decimal_places=16)
    draw = models.DecimalField(max_digits=18, decimal_places=16)

    def __str__(self):
        return str(self.idNode)




class Tree:
    """def __init__(self):
        if os.path.isfile('./tree.ia'):
            with open('./tree.ia', 'rb') as file:
                self.nodes = pickle.load(file)
        else:
            self.nodes={}
            #self.nodes = {id:{"type":type,"up":None,"down":None,"left":None,"right":None}} #0 saved struct
    """
    def initiate(self,board):
        self.objects.get_or_create(node_id=0)
            #ID = 0 car premier généré
        #print(self.nodes)
    
    def save(self):
        pickle.dump( self.nodes,open('./tree.ia', 'wb'))
        
        
    def get_node(self,id):
        return self.nodes[id]
    def get_child_node_id(self,id,direction):
        return self.nodes[id][direction]
    def add_node(self,direction,current_board,current_player):
        
        parent_id = current_board.get_id()
        
        if direction in ["up","down","left","right"] and not self.nodes[parent_id][direction]:
            
            temp_board = copy.deepcopy(current_board)
            temp_board.move(current_player,direction)
            
            child_id = temp_board.get_id()
            
            self.nodes[parent_id][direction]=child_id
            
            if not child_id in self.nodes:
                type = 0
                if temp_board.end():
                    type = temp_board.get_winner()
                
                self.nodes[child_id]={"type":type,"up":None,"down":None,"left":None,"right":None,"p1":0,"p2":0,"draw":0} #creation of the newest node
                
    def add_dead_end_node(self,direction,current_board):
        
        parent_id = current_board.get_id()
        
        if direction in ["up","down","left","right"] and not self.nodes[parent_id][direction]:
            self.nodes[parent_id][direction]="-1" #initiate a dead_end_node
        
    
    def get_ways(self,id):
        node = self.nodes[id]
        ways = []
        
        for direction in node: #skips the type
            if direction == "type":
                continue
                
                
            if node[direction] and node[direction] != "-1":
                ways.append(node[direction])
            elif not node[direction]:
                ways.append(None) #add an empty child (must be accounted)
                
        return ways
    
    
    def get_rates(self,id):
        """ways = self.get_ways(id)
        nb_ways = len(self.get_ways(id))
        win_rate_1 = 0.
        win_rate_2 = 0.
        draw_rate = 0.
        unknown_rate = 0.
        
        if id in checked_nodes:
            return win_rate_1,win_rate_2,draw_rate,unknown_rate
        
        checked_nodes.append(id)
        
        
        for child_id in ways:
            if not child_id:
                unknown_rate+=1
            else:
                child = self.nodes[child_id]
                if child["type"] == 1:
                    win_rate_1+=1
                elif child["type"] == 2:
                    win_rate_2+=1
                elif child["type"] == 3:
                    draw_rate+=1
                    
                elif child["type"] == 0:
                    rates=self.get_rates(child_id,checked_nodes)
                    win_rate_1+=rates[0]
                    win_rate_2+=rates[1]
                    draw_rate+=rates[2]
                    unknown_rate+=rates[3]
        
        return win_rate_1,win_rate_2,draw_rate,unknown_rate
        """
        
        current = self.nodes[id]
        
        return current["p1"],current["p2"],current["draw"]
    
    def Qfunction(self,current_id,direction,id):
        return self.nodes[current_id][direction][:-4].count(str(id)) - current_id[:-4].count(str(id))
        
    
    def get_move(self,parent_id,child_id):
        for direction in self.nodes[parent_id]:
            if direction == "type":
                continue
            if self.nodes[parent_id][direction] == child_id:
                return direction
            
    def add_value(self,path,winner):
        trad_winner = {3:"draw",1:"p1",2:"p2"}
        for node in path:
            self.nodes[node][trad_winner[winner]]+=1

    
class filler_AI:
    def __init__(self):
        self.tree = Tree()
        self.checked_nodes = [] #will contain all the checked nodes, avoid recalculing done nodes
    def fill(self,board_size):
        board = Board.objects.get(name="game")
        self.tree.initiate(board)  #init the tree if needed
        
        
        
        self.initiate_nodes(board,1) #initiate the first nodes
        
        
        current_node_id = board.get_id()
        self.checked_nodes.append(current_node_id) #adds the node to the checked nodes
        
        for direction in ["up","down","left","right"]:
            
            child_id = self.tree.nodes[current_node_id][direction]
            
            if not child_id: #if node doesn't exist, initate it (will be automaticly liked to the current node)
                
                self.tree.add_node(direction,board,self.id)
                child_id = self.tree.nodes[current_node_id][child_key]
            
            if child_id == "-1":
                continue
                
            copy_board = copy.deepcopy(board)
            
            self.inspect(copy_board,direction,2)
            
        #print(self.tree.nodes)
    
    
    def inspect(self,board,direction,player_id):
        
        board.move(player_id%2+1,direction) #move in the copy board
        
        self.initiate_nodes(board,player_id) #initiate the first nodes
        
        current_node_id = board.get_id()
        self.checked_nodes.append(current_node_id) #adds the node to the checked nodes
        
        for direction in ["up","down","left","right"]:
            
            child_id = self.tree.nodes[current_node_id][direction]
            
            if not child_id: #if node doesn't exist, initate it (will be automaticly liked to the current node)
                
                self.tree.add_node(direction,board,self.id)
                child_id = self.tree.nodes[current_node_id][child_key]
            
            if child_id == "-1" or child_id in self.checked_nodes or not '0' in child_id[0:board.size**2]: #dead-end,already checked node,ended board.
                continue
            
            self.checked_nodes.append(child_id) #now this node has been checked
            
            
            copy_board = copy.deepcopy(board)
            
            self.inspect(copy_board,direction,player_id%2+1)
            
    
    
    def initiate_nodes(self,board,id_to_add,move=None): #id to add is the id for the nodes we are looking to add
        
        temp_board = copy.deepcopy(board) #lets copy the board to avoid changes
        
        if move:
            temp_board.move(id_to_add%2+1,move)
        
        current_node_id = temp_board.get_id()
        
        for direction in ["up","down","left","right"]:     #first, checks for the dead ends
            
            if direction not in temp_board.get_moves(id_to_add) and not self.tree.nodes[current_node_id][direction]:
                self.tree.add_dead_end_node(direction,temp_board)
                
            elif not self.tree.nodes[current_node_id][direction] :
                self.tree.add_node(direction,temp_board,id_to_add)
            
            
    
    
class AI:
    def __init__(self):
        self.tree = Tree()
    
    def start(self,id,mode,board):
        self.id = id
        self.mode = mode #"game","learning"
        self.path = []
        
        if board.get_id()not in self.tree.nodes: #makes sure the starting node is in the tree
            self.tree.initiate(board)        
        
            
    def get_move(self,board,last_move=None):
        
        board = copy.deepcopy(board)  #just for safety
        
        current_node_id = board.get_id()
        
        self.path.append(current_node_id)
        
        
        self.initiate_nodes(board,self.id)
 
        
        rates={}

        for child_key in self.tree.nodes[current_node_id]:
             
            if child_key in ["type","p1","p2","draw"]: #skips type
                continue
            
            
            child_id = self.tree.nodes[current_node_id][child_key]
            
            if not child_id: #if node doesn't exist, initate it (will be automaticly liked to the current node)
                
                self.tree.add_node(child_key,board,self.id)
                child_id = self.tree.nodes[current_node_id][child_key]
            
            elif child_id == "-1":
                continue
                
            #print(child_id)
            win_rate_1,win_rate_2,draw_rate = self.tree.get_rates(child_id)
            
            #print("IA",self.id," ",child_id ,"(",child_key,"):",win_rate_1,",",win_rate_2,",",draw_rate)
            rates[child_key]=[win_rate_1,win_rate_2,draw_rate]
            
        #should be put in a Vfunction()
        
        values={}
        for child_dir in rates:
            if self.id == 1:
                values[child_dir]=self.tree.Qfunction(current_node_id,child_dir,self.id)*((rates[child_dir][0]+10)/(sum(rates[child_dir])+10))
            else:
                values[child_dir]=self.tree.Qfunction(current_node_id,child_dir,self.id)*((rates[child_dir][1]+10)/(sum(rates[child_dir])+10))
            
            
        
            
        best_dir = next(iter(values))
        
        for direction in values:
            if values[best_dir]<values[direction]:
                best_dir = direction
                
        #print(best_dir)
        #print(self.tree.nodes[current_node_id][best_dir])
                
        self.path.append(self.tree.nodes[current_node_id][best_dir])
        
        
        #initiate next possible nodes
        
        
        self.initiate_nodes(board,(self.id%2+1),best_dir)

        return best_dir
    
    def initiate_nodes(self,board,id_to_add,move=None): #id to add is the id for the nodes we are looking to add
        
        temp_board = copy.deepcopy(board) #lets copy the board to avoid changes
        
        if move:
            temp_board.move(id_to_add%2+1,move)
        
        current_node_id = temp_board.get_id()
        
        for direction in ["up","down","left","right"]:     #first, checks for the dead ends
            
            if direction not in temp_board.get_moves(id_to_add) and not self.tree.nodes[current_node_id][direction]:
                self.tree.add_dead_end_node(direction,temp_board)
                
            elif not self.tree.nodes[current_node_id][direction] :
                self.tree.add_node(direction,temp_board,id_to_add)
                
    
    def save(self,winner):
        self.tree.add_value(self.path,winner)
        self.tree.save()
        
def dumbIA(board,id):
    moves = board.get_intresting_moves(id)
    if moves == []:
        moves = board.get_moves(id)
    return moves[randrange(len(moves))]
        
            
        
        

def start(size = 8,playType = 0,nb_train=1):#only versus for now
    
    
    if playType == 0:  #AI VS PLAYER
        ai = AI()
        player_turn = 2
        board = Board(size)
        ai.start(1,"learning",board)
        board.print_board() #to replaced with the display fonction
        ai_order = ai.get_move(board,None)
        board.move(1,ai_order)
        board.print_board()
        
        while not board.end():
            order = input("Player %d, where do you want to move?"%player_turn)
            while order not in board.get_moves(player_turn):
                order = input("Wrong move Player %d, where do you want to move?"%player_turn)
            board.move(player_turn,order)
            board.print_board()
            #ai_turn (only if theire is still moves to do)
            if not board.end():
                ai_order = ai.get_move(board,order)
                board.move(1,ai_order)
                board.print_board()
                
        ai.save(board.get_winner())
        
        print(ai.tree.nodes[x] for x in ai.tree.nodes)
        print("the winner is Player %d!"% board.get_winner()) #will display 3 in case of draw
    
    elif playType == 1:     #AI VS DUMB AI
        start = time.time()
        wins = {1:0,2:0,3:0}
        ai = AI()
        
        for i in range (nb_train):
            print("Game ",i)
            board = Board(size)
            ai.start(1,"game",board)
            ai_order = ai.get_move(board,None)
            board.move(1,ai_order)
        
            while not board.end():
                order = dumbIA(board,2)
                board.move(2,order)
                #ai_turn (only if theire is still mives to do)
                if not board.end():
                    ai_order = ai.get_move(board,order)
                    board.move(1,ai_order)
                
            ai.save(board.get_winner())
            
            board.print_board()
        
            print(ai.tree.nodes[x] for x in ai.tree.nodes)
            print("the winner is Player %d!"% board.get_winner()) #will display 3 in case of draw
            wins[board.get_winner()]+=1
            
        end = time.time()
        print(nb_train,"simulations runned for:",end - start)
        print(wins)
    
    
    elif playType == 2:   #AI VS AI
        start = time.time()
        wins = {1:0,2:0,3:0}
        
        #avoid loading the tree every time
        ai = AI()
        ai2 = AI()
        
        
        for i in range (nb_train):
            print("Game ",i)
            ai.start(1,"game")
            ai2.start(2,"game")
            board = Board(size)
            ai_order = ai.get_move(board,None)
            board.move(1,ai_order)
        
            while not board.end():
                ai2_order = ai2.get_move(board,ai_order)
                board.move(2,ai2_order)
                #ai_turn (only if theire is still mives to do)
                if not board.end():
                    ai_order = ai.get_move(board,ai2_order)
                    board.move(1,ai_order)
                else:
                    print(ai2_order)
                    ai.set_defeat(board,ai2_order)
                
            ai.save()
            
            #no need to save ai2, ai learns for both p1 and p2
            
            board.print_board()
        
            print(ai.tree.nodes[x] for x in ai.tree.nodes)
            print("the winner is Player %d!"% board.get_winner()) #will display 3 in case of draw
            wins[board.get_winner()]+=1
            
        end = time.time()
        print(nb_train,"simulations runned for:",end - start)
        print(wins)
