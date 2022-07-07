from copy import copy

import numpy as np
WCIRCLE = 0
WSQUARE = 1
BCIRCLE = 2
BSQUARE =3
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
    def __init__(self,board=None,turn=0):
        # -2 = invalid
        # -1 = empty
        # 0 = white circle
        # 1 = white square
        # 2= black circle
        # 3 = black square
        if not board:
            self.board = self.pboard_to_arr([[-2,-2,-1,1,3,-1,-1,-2],
                          [-1,-1,-1,0,2,3,-1,-1],
                          [-1,-1,1,0,2,-1,-1,-1],
                          [-2,-1,-1,1,3,-1,-2,-2]])
        else:
            self.board = board
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
        self.board[pos[1]][pos[0]] =np.eye(6)[value]
    def __repr__(self):
        s = ""
        for y in range(4):
            for x in range(8):
                v = self[x,y]
                s+= ["","-","⚫","⬛","⚪","⬜"][v+2]
                s+="\t"
            s+="\n"
        return s
    def pieces(self,turn):
        for y in range(4):
            for x in range(8):
                v  = self[x,y]
                if self[x,y]>=0+turn*2:
                    yield (v,(x,y))

    def empty(self,pos):
        return self[pos]==-1
    def search_from_pos(self,pos):
        searched = set()
        dirs = ((1,0),(0,1),(-1,0),(0,-1))
        available_pos = [pos]
        todopos = [pos]
        while todopos:
            ogx,ogy = todopos[0]
            for dir in dirs:
                y=ogy+dir[1]
                x=ogx+dir[0]
                if inb((x,y)) self.empty((x,y)):
                    todopos.append((x,y))
                    available_pos.append((x,y))
        return available_pos
    def __copy__(self):
        return PushFight(np.copy(self.board),self.turn)

    def available_moves(self,pos):
        piece = self[pos]
        if iscircle(piece):
            return self.search_from_pos(pos)
        elif issquare(piece):
            avail = self.search_from_pos()


    # def __repr__(self):
b=PushFight()
print(b)
