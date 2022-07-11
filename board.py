from __future__ import annotations
import math
from copy import copy
import random
import numpy as np

emojimode = 1

WCIRCLE = 0
WSQUARE = 1
BCIRCLE = 2
BSQUARE =3

def op_turn(turn):
    return turn^1
def piece_to_turn(piece):
    return [-1,-1,0,0,1,1][piece+2]
def square(turn):
    return 0+turn*2
def circle(turn):
    return 1+turn*2
def issquare(piece):
    return piece == WSQUARE or piece == BSQUARE
def iscircle(piece):
    return piece == BCIRCLE or piece == WCIRCLE
def inb(pos):
    return pos[0]>=0 and pos[0]< 8 and pos[1]>=0 and pos[1]<4


class PushFight:
    edges = ((2,0),(6,0),(0,1),(1,1),(7,1),(0,2),(6,2),(7,2),(1,3),(5,3))
    dirs = ((1,0),(0,1),(-1,0),(0,-1))
    edge_edge_cases = {(2,0),(6,0),(1,3),(5,3)}
    def __init__(self,board=None,turn=0,anchor=None):
        # -2 = invalid
        # -1 = empty
        # 0 = white circle
        # 1 = white square
        # 2= black circle
        # 3 = black square
        if  board is None:
            self.board = self.pboard_to_arr([[-2,-2,-1,1,3,-1,-1,-2],
                          [-1,-1,-1,0,2,3,-1,-1],
                          [-1,-1,1,0,2,-1,-1,-1],
                          [-2,-1,-1,1,3,-1,-2,-2]])
        else:
            self.board = board
        if anchor:
            self.anchor = anchor
        else:

            self.anchor = (-1,-1)
        self.turn =turn

    def pboard_to_arr(self,b):
        newb = np.zeros((4,8,6))
        for y in range(4):
            for x in range(8):
                newb[y][x][ b[y][x]+2 ]  =1

        return newb

    def __getitem__(self, pos):
        x, y =pos
        return np.argmax(self.board[y][x])-2
    def __setitem__(self,pos,value):
        self.board[pos[1]][pos[0]] =np.eye(6)[value+2]
    def __repr__(self):
        s = "\n\t\t_________________________________\n"

        for y in range(4):
            for x in range(8):
                if (x,y)==self.anchor:
                    s+="|"
                v = self[x,y]
                if emojimode==1:
                    s+= ["","-","⚪","⬜","⚫","⬛"][v+2]
                elif emojimode==0:
                    s+= ["","-","⚫","⬛","⚪","⬜"][v+2]
                else:
                    s += ["", "-", "WC", "WS", "BC", "BS"][v + 2]
                if (x,y)==self.anchor:
                    s+="|"
                s+="\t"
            s+="\n"
        return s+ "\t‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾\n"

    def push_locations(self,pos):
        for dir in PushFight.dirs:
            if self.anchor[1] == pos[1] and ((dir == (1, 0) and self.anchor[0] > pos[0]) or (
                    dir == (-1, 0) and self.anchor[0] < pos[0])):
                continue
            if self.anchor[0] == pos[0] and ((dir == (0, 1) and self.anchor[1] > pos[1]) or (
                    dir == (0, -1) and self.anchor[1] < pos[1])):
                continue
            x, y = pos
            x+=dir[0]
            y+=dir[1]
            if inb((x,y)):
                while self[x,y]!=1+self.turn*2:
                    yield (x,y)
                    if self[x,y]==-1:
                        break
                    x += dir[0]
                    y += dir[1]
                    if not inb((x,y)):
                        break
    def state(self):
        #THIS MUST BE CALLED ON PUSH TURN
        #-1 = keep going
        #1 = self.turn won!!!
        for edge in PushFight.edges:
            p = self[edge]
            pos = edge
            if piece_to_turn(p)!=self.turn and p!=-1:
                dirchoice = PushFight.dirs
                if edge in PushFight.edge_edge_cases:
                    dirchoice = ((1,0),(-1,0))
                for dir in dirchoice:

                    if self.anchor[1] == pos[1] and ((dir == (1, 0) and self.anchor[0] > pos[0]) or (
                            dir == (-1, 0) and self.anchor[0] < pos[0])):
                        continue
                    if self.anchor[0] == pos[0] and ((dir == (0, 1) and self.anchor[1] > pos[1]) or (
                            dir == (0, -1) and self.anchor[1] < pos[1])):
                        continue
                    x, y = pos
                    x+=dir[0]
                    y+=dir[1]
                    if inb((x,y)):
                        while self[x,y]!=1+self.turn*2:
                            if self[x,y]==-1:
                                break
                            x += dir[0]
                            y += dir[1]
                            if not inb((x,y)):
                                break
                        else:
                            return 1
        return -1




    def pieces(self,turn):
        for y in range(4):
            for x in range(8):
                v  = self[x,y]
                if piece_to_turn(v)==turn:
                    yield (v,(x,y))
    def squares(self,turn=-1):
        if turn !=-1:
            p = 1 if turn ==0 else 3
            for y in range(4):
                for x in range(8):
                    v  = self[x,y]
                    if v==p:
                        yield (v,(x,y))
        else:
            for y in range(4):
                for x in range(8):
                    v  = self[x,y]
                    if v==1 or v==3:
                        yield (v,(x,y))
    def circles(self,turn=-1):
        if turn!=-1:
            p = turn*2
            for y in range(4):
                for x in range(8):
                    v  = self[x,y]
                    if v==p:
                        yield (v,(x,y))
        else:
            for y in range(4):
                for x in range(8):
                    v  = self[x,y]
                    if v==0 or v==2:
                        yield (v,(x,y))
    def empty(self,pos):
        return self[pos]==-1
    def available_moves(self,pos):
        searched = set()
        dirs = ((1,0),(0,1),(-1,0),(0,-1))

        searched.add(pos)
        available_pos = [pos]
        todopos = [pos]
        while todopos:
            ogx,ogy = todopos.pop(0)
            for dir in dirs:
                y=ogy+dir[1]
                x=ogx+dir[0]


                if inb((x,y)) and self.empty((x,y)) and (x,y) not in searched:
                    todopos.append((x,y))
                    available_pos.append((x,y))
                    searched.add((x,y))

        return available_pos

    def __copy__(self):
        return PushFight(np.copy(self.board),self.turn,self.anchor)

    def available_pushes(self,pos):
        available_dirs = []
        dirs = ((1,0),(0,1),(-1,0),(0,-1))
        ogx,ogy = pos
        for dir in dirs:
            # check anchor. this will be my only comment
            # jk i will do more comments especially on my mcst
            if self.anchor[1] == pos[1] and ((dir == (1,0) and self.anchor[0]>pos[0]) or (dir == (-1,0) and self.anchor[0]<pos[0])):
                continue
            if self.anchor[0]==pos[0] and ((dir == (0,1) and self.anchor[1]>pos[1]) or (dir == (0,-1) and self.anchor[1]<pos[1])):
                continue


            x = ogx+dir[0]
            y = ogy+dir[1]
            if not inb((x,y)) or self.empty((x,y)):
                continue

            while inb((x,y)) and not self.empty((x,y)):
                x+=dir[0]
                y+=dir[1]
                if y<0 or y>3:
                    break
            else:
                if inb((x,y)):
                    available_dirs.append(dir)

        return available_dirs
    def make_move(self,ogpos,newpos):
        if ogpos!=newpos:
            self[newpos] = self[ogpos]
            self[ogpos] = -1

    def make_push(self,pos,dir):

        ogx, ogy = pos
        carry = self[pos]
        x= ogx+dir[0]
        y= ogy+dir[1]
        self.anchor = (x,y)
        self[pos] = -1
        prev = carry
        while inb((x,y)) and not self.empty((x,y)):

            prev = carry
            t = carry
            carry = self[x,y]
            self[x,y] = t

            x+=dir[0]
            y+=dir[1]
        if inb((x,y)) and self.empty((x,y)):
            self[x,y] = carry
            return -1
        elif not inb((x,y)):
            return piece_to_turn(prev)
        else:
            raise Exception("penis error: why did this happen")
    def random_move(self,moves):
        turn = self.turn
        if moves>=1:
            pieces = list(self.pieces(turn))
            piece,pos  = random.choice(pieces)
        while True:
            first_board = copy(self)
            if moves>=1:
                avail = self.available_moves(pos)

                first_board.make_move(pos,random.choice(avail))

            second_board = copy(first_board)
            if moves==2:
                piece2, pos2 = random.choice(list(first_board.pieces(self.turn)))
                move2 = random.choice(first_board.available_moves(pos2))
                second_board.make_move(pos2,move2)
            p,squarpos = random.choice(list(second_board.squares(turn)))
            if self.state()==1:
                return False
            avail_pushes = second_board.available_pushes(squarpos)

            if len(avail_pushes)==0:
                continue
            second_board.make_push(squarpos,random.choice(avail_pushes))
            self.board = second_board.board
            self.anchor = second_board.anchor
            self.turn = op_turn(self.turn)
            break


        return  True
    def permutation(self,turn,rounds):
        if rounds==0:
            return [self]
        perms = []
        for piece,pos in self.pieces(turn):
            for move in self.available_moves(pos):
                first_board = copy(self)
                first_board.make_move(pos,move)
                for piece2,pos2 in first_board.pieces(turn):
                    for move2 in first_board.available_moves(pos2):
                        second_board = copy(first_board)
                        second_board.make_move(pos2,move2)
                        for squarep, pos3 in second_board.pieces(turn):
                            if issquare(squarep):
                                for push in second_board.available_pushes(pos3):
                                    third_board = copy(second_board)
                                    third_board.make_push(pos3,push)
                                    perms += third_board.permutation(op_turn(turn), rounds - 1)
        return  perms



    # def random_game(self):

def str_to_board(st):
    x = 2
    y=  0
    b = PushFight()
    for v in st:
        if v=='\n':
            y+=1
            x=[2,0,0,1][y]
        elif v in ["-","⚪","⬜","⚫","⬛"]:
            b[x,y]={"-":-1,"⚪":0,"⬜":1,"⚫":2,"⬛":3}[v]
            x+=1
        elif v=="|" and b.anchor==(-1,-1):
            b.anchor = (x,y)
    return b

    # def __repr__(self):
class MonteCarloTree:
    def __init__(self,player,head):
        self.player = player
        self.head = head
    def __repr__(self):
        return str(self.head)
def float_eq(a, b, rel_tol=1e-09, abs_tol=0.0):
    return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)

class MonteCarloNode:
    DELETE_ME = None
    def __init__(self,board: PushFight,step,turn,tree:MonteCarloTree,parent: MonteCarloNode,index:int):
        #steps
        #0 = first move
        #1 = second move
        #2 = push (you can skip to this)
        self.board = board
        self.step = step
        self.turn = turn
        self.babies  = []
        self.iswinner = None
        self.visits = 0
        self.tree = tree
        self.score = 0
        self.probability = 1
        self.parent = parent
        self.index = index
    def rollout(self):
        v = self.rollout_helper()
        self.create_babies()
        return v
    def rollout_helper(self):
        if self.step==2:
            if self.iswinner==None:
                self.iswinner = self.board.state()
            if self.iswinner==1:
                return 1
            pushes = []
            for piece,pos in self.board.squares(self.turn):
                pushes += [(pos,x) for x in self.board.available_pushes(pos)]
            if len(pushes)==0:
                return MonteCarloNode.DELETE_ME
            c = copy(self.board)
            ch = random.choice(pushes)
            c.make_push(ch[0],ch[1])
            c.turn = op_turn(self.turn)

            while c.random_move(2):
                pass
            return 1 if c.turn==self.tree.player else -1
        elif self.step==1:
            c = copy(self.board)
            if c.random_move(1):
                return 1 if c.turn == self.tree.player else -1
            while c.random_move(2):
                pass
            return 1 if c.turn == self.tree.player else -1
        elif self.step==0:
            c = copy(self.board)
            while c.random_move(2):
                pass

            print("win!!!")
            print(c.turn)
            print(c)
            return 1 if c.turn == self.tree.player else -1
            
        else:
            raise Exception("uh oh oopsie poopies?!?!?")

    def uct(self):
        if self.visits==0:
            add = 0

        else:
            add = self.score/self.visits
        return add+ self.probability*1.4142*math.sqrt(math.log(self.parent.visits)/(self.visits+1))

    def highests_uct(self):
        max_nodes = []
        max_value = -99999
        for baby in self.babies:
            uct = baby.uct()

            if float_eq(uct, max_value):
                max_nodes.append(baby)
            elif uct > max_value:
                max_value = uct
                max_nodes = [baby]
        return max_nodes

    def deletion(self,index):
        self.babies.pop(index)
        for i in range(index,len(self.babies)):
            self.babies[i].index = i
    def selection(self):
        self.visits += 1
        if len(self.babies) == 0:

            print("what da dog doing??")

        baby =random.choice(self.highests_uct())

        baby.visits += 1

        if len(baby.babies)==0:
            if baby.iswinner:
                score = 1 if baby.turn == self.tree.player else -1
                baby.score+=score
                self.score +=score
                return score
            score = baby.rollout()
            if score==MonteCarloNode.DELETE_ME:
                self.parent.deletion(self.index)
                return 0
            baby.score+=score
            self.score+=score
            return score
        score = baby.selection()
        self.score+=score
        return score

    def create_babies(self):
        if self.iswinner==1:
            raise Exception("??? que el paso new mexico")
        if self.step ==0 or self.step==-1:
            for piece, pos in self.board.pieces(self.turn):
                for mov in self.board.available_moves(pos):
                    c = copy(self.board)
                    c.make_move(pos,mov)
                    self.babies.append(MonteCarloNode(c,self.step+1,self.turn,self.tree,self,len(self.babies)-1))
        elif self.step==1:
            for piece, pos in self.board.squares(self.turn):
                for push in self.board.available_pushes(pos):
                    c = copy(self.board)
                    c.make_push(pos,push)
                    c.turn = op_turn(self.turn)
                    n =MonteCarloNode(c,2,self.turn,self.tree,self,len(self.babies)-1)
                    if c.state()==1:
                        n.iswinner = True
                    self.babies.append(n)
        elif self.step==2:
            for piece, pos in self.board.pieces(op_turn(self.turn)):
                for mov in self.board.available_moves(pos):
                    c = copy(self.board)
                    c.turn  = op_turn(self.turn)
                    c.make_move(pos,mov)
                    self.babies.append(MonteCarloNode(c,0,op_turn(self.turn),self.tree,self,len(self.babies)-1))
        else:
            raise Exception("down in el paso my life would be worthless")
    def __str__(self):
        return f"<{self.visits} {self.score} {self.board} {self.babies}>"
    def __repr__(self):
        return f"<{self.visits} {self.score} {self.board}>"
# b = str_to_board("""		⚪	⬜	-	    ⬛	-
# ⚪	⬜	⬜	-	-	-	-	-
# ⚫	-	|⬛|	-	-	⬛	-	-
# 	-	-	-	-	⚫			""")
# b.turn = 0
# print(b)
# print(b.permutation(0,1))
b=PushFight()
b.turn = 0
score = 0
for i in range(100):
    c = copy(b)
    while c.random_move(3):
        pass
    print(c)
    score+= 1 if c.turn==1 else -1

print(score)
# p  =b.permutation(0,1)
# print(p)
# print(len(p))
# print(b.available_moves((5,1)))
# # while True:
# #     b.random_move(1)
# #     print(b)
# b.turn = 1
# t = MonteCarloTree(1,None)
# n = MonteCarloNode(b,-1,1,t,None,0)
# t.head = n
# n.create_babies()
# for i in range(100):
#     n.selection()
# print(t)
# for i in range(20):
#     n.selection()
# print(t)
# m = -1
# mb = None
# for x in n.babies:
#     if x.visits>m:
#         m = x.visits
#         mb = x
# print(mb)
# m = -99
# mb = None
# for x in n.babies:
#     if x.score>m:
#         m = x.score
#         mb = x
# print(mb)
# print(n)
# while True:
#     print(b.random_move())
#     print(b)