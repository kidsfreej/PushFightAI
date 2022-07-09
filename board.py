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
        s = "\t\t_________________________________\n"

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
    def pieces(self,turn):
        for y in range(4):
            for x in range(8):
                v  = self[x,y]
                if piece_to_turn(v)==turn:
                    yield (v,(x,y))

    def empty(self,pos):
        return self[pos]==-1
    def available_moves(self,pos):
        searched = set()
        dirs = ((1,0),(0,1),(-1,0),(0,-1))

        searched.add(pos)
        available_pos = []
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
                if inb((x,y)) or piece_to_turn(self[x-dir[0]*3,y-dir[1]*3])!=piece_to_turn(self[pos]):
                    available_dirs.append(dir)
                else:
                    c = copy(self)
                    c.make_push(pos,dir)

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

    def random_move(self):
        b  =random.choice(self.permutation(self.turn,1))
        self.board = b.board
        self.anchor =  b.anchor
    
        self.turn =op_turn(self.turn)
    def permutation(self,turn,rounds):
        if rounds==0:
            return [self]
        perms = []
        for piece,pos in self.pieces(turn):
            if iscircle(piece):
                for move in self.available_moves(pos):
                    first_board = copy(self)
                    first_board.make_move(pos,move)
                    for piece2,pos2 in first_board.pieces(turn):
                        if iscircle(piece2):
                            for move2 in first_board.available_moves(pos2):
                                second_board = copy(first_board)
                                second_board.make_move(pos2,move2)
                                for squarep, pos3 in second_board.pieces(turn):
                                    if issquare(squarep):
                                        for push in second_board.available_pushes(pos3):
                                            third_board = copy(second_board)
                                            third_board.make_push(pos3,push)
                                            # print(second_board)
                                            perms += third_board.permutation(op_turn(turn), rounds - 1)
                                            
                        else:
                            for push in first_board.available_pushes(pos2):
                                second_board = copy(first_board)
                                second_board.make_push(pos2,push)
                                perms += second_board.permutation(op_turn(turn), rounds - 1)
                                
            else:
                for push in self.available_pushes(pos):
                    first_board = copy(self)
                    first_board.make_push(pos,push)
                    perms+=first_board.permutation(op_turn(turn),rounds-1)
                    

        return perms
    # def random_game(self):


    # def __repr__(self):
b=PushFight()
print(b)
b.random_move()
print(b)
b.random_move()
print(b)
b.random_move()
print(b)
b.random_move()
print(b)
# b.random_move()
# print(b)
# print(b.available_pushes((1,2)))
# print(b.make_push((1,2),(-1,0)))
# print(b)
# print(b.available_pushes((1,2)))
# print(b.permutation(0,1))
# print(b)
# print(b.available_pushes((6,1)))
# print(b.permutation(0,2))
# d = b.available_pushes((3
# ,0))[0]
# print(d)
# print(b.make_push((3,0),d))
# print(b)
