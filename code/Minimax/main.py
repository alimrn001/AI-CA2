import random
import time
import turtle
import numpy as np
import sys

class OthelloUI:
    def __init__(self, board_size=6, square_size=60):
        self.board_size = board_size
        self.square_size = square_size
        self.screen = turtle.Screen()
        self.screen.setup(self.board_size * self.square_size + 50, self.board_size * self.square_size + 50)
        self.screen.bgcolor('white')
        self.screen.title('Othello')
        self.pen = turtle.Turtle()
        self.pen.hideturtle()
        self.pen.speed(0)
        turtle.tracer(0, 0)

    def draw_board(self, board):
        self.pen.penup()
        x, y = -self.board_size / 2 * self.square_size, self.board_size / 2 * self.square_size
        for i in range(self.board_size):
            self.pen.penup()
            for j in range(self.board_size):
                self.pen.goto(x + j * self.square_size, y - i * self.square_size)
                self.pen.pendown()
                self.pen.fillcolor('green')
                self.pen.begin_fill()
                self.pen.setheading(0)
                for _ in range(4):
                    self.pen.forward(self.square_size)
                    self.pen.right(90)
                self.pen.penup()
                self.pen.end_fill()
                self.pen.goto(x + j * self.square_size + self.square_size / 2,
                              y - i * self.square_size - self.square_size + 5)
                if board[i][j] == 1:
                    self.pen.fillcolor('white')
                    self.pen.begin_fill()
                    self.pen.circle(self.square_size / 2 - 5)
                    self.pen.end_fill()
                elif board[i][j] == -1:
                    self.pen.fillcolor('black')
                    self.pen.begin_fill()
                    self.pen.circle(self.square_size / 2 - 5)
                    self.pen.end_fill()

        turtle.update()


class Othello:
    def __init__(self, ui, minimax_depth=1, prune=True):
        self.size = 6
        self.ui = OthelloUI(self.size) if ui else None
        self.board = [[0 for _ in range(self.size)] for _ in range(self.size)]
        self.board[int(self.size / 2) - 1][int(self.size / 2) - 1] = self.board[int(self.size / 2)][
            int(self.size / 2)] = 1
        self.board[int(self.size / 2) - 1][int(self.size / 2)] = self.board[int(self.size / 2)][
            int(self.size / 2) - 1] = -1
        self.current_turn = random.choice([1, -1])
        self.minimax_depth = minimax_depth
        self.prune = prune

    def get_winner(self):
        white_count = sum([row.count(1) for row in self.board])
        black_count = sum([row.count(-1) for row in self.board])
        if white_count > black_count:
            return 1
        elif white_count < black_count:
            return -1
        else:
            return 0

    def get_valid_moves(self, player):
        moves = set()
        for i in range(self.size):
            for j in range(self.size):
                if self.board[i][j] == 0:
                    for di in [-1, 0, 1]:
                        for dj in [-1, 0, 1]:
                            if di == 0 and dj == 0:
                                continue
                            x, y = i, j
                            captured = []
                            while 0 <= x + di < self.size and 0 <= y + dj < self.size and self.board[x + di][
                                    y + dj] == -player:
                                captured.append((x + di, y + dj))
                                x += di
                                y += dj
                            if 0 <= x + di < self.size and 0 <= y + dj < self.size and self.board[x + di][
                                    y + dj] == player and len(captured) > 0:
                                moves.add((i, j))
        return list(moves)

    def make_move(self, player, move):
        i, j = move
        self.board[i][j] = player
        for di in [-1, 0, 1]:
            for dj in [-1, 0, 1]:
                if di == 0 and dj == 0:
                    continue
                x, y = i, j
                captured = []
                while 0 <= x + di < self.size and 0 <= y + dj < self.size and self.board[x + di][y + dj] == -player:
                    captured.append((x + di, y + dj))
                    x += di
                    y += dj
                if 0 <= x + di < self.size and 0 <= y + dj < self.size and self.board[x + di][y + dj] == player:
                    for (cx, cy) in captured:
                        self.board[cx][cy] = player

    def get_heuristic(self) :
        ai_tiles, human_tiles = 0, 0
        ai_corners, human_corners = 0, 0
        ai_loose_rows_num, human_loose_rows_num = 0, 0
        heuristic = 0

        for i in range(0, 5) :
                for j in range (0, 5) :
                    if(self.board[i][j] == -1) :
                        ai_tiles += 1
                    elif(self.board[i][j] == 1):
                        human_tiles += 1

        if(human_tiles + ai_tiles == 36) :
                if(human_tiles > ai_tiles) :
                    return sys.maxsize * (self.current_turn)
                elif(human_tiles < ai_tiles) :
                    return -sys.maxsize * (self.current_turn)
                else :
                    return 0 # match draw case

        heuristic += (human_tiles - ai_tiles)*self.current_turn
        
        for i in range(0, 10, 5) :
            for j in range(0, 10, 5) :
                if(self.board[i][j] == 1) :
                    human_corners += 1
                elif(self.board[i][j] == -1) :
                    ai_corners += 1

        heuristic += 5*(human_corners - ai_corners) * self.current_turn
        
        if(self.board[0][0] == 0) :
            if(self.board[1][0] == -1 and self.board[5][0] == 1) :
                ai_loose_rows_num += 1
            elif(self.board[1][0] == 1 and self.board[5][0] == -1) :
                human_loose_rows_num += 1
            
            if(self.board[0][1] == -1 and self.board[0][5] == 1):
                ai_loose_rows_num += 1
            elif(self.board[0][1] == 1 and self.board[0][5] == -1):
                human_loose_rows_num += 1

            if(self.board[1][1] == -1 and self.board[5][5] == 1):
                ai_loose_rows_num += 1
            if(self.board[1][1] == 1 and self.board[5][5] == -1):
                human_loose_rows_num += 1

        if(self.board[0][5] == 0) :
            if(self.board[1][5] == -1 and self.board[5][5] == 1) :
                ai_loose_rows_num += 1
            elif(self.board[1][5] == 1 and self.board[5][5] == -1) :
                human_loose_rows_num += 1
            
            if(self.board[0][4] == -1 and self.board[0][0] == 1):
                ai_loose_rows_num += 1
            elif(self.board[0][4] == 1 and self.board[0][0] == -1):
                human_loose_rows_num += 1

            if(self.board[1][4] == -1 and self.board[5][0] == 1):
                ai_loose_rows_num += 1
            if(self.board[1][4] == 1 and self.board[5][0] == -1):
                human_loose_rows_num += 1

        if(self.board[5][0] == 0) :
            if(self.board[4][0] == -1 and self.board[0][0] == 1) :
                ai_loose_rows_num += 1
            elif(self.board[4][0] == 1 and self.board[0][0] == -1) :
                human_loose_rows_num += 1
            
            if(self.board[5][1] == -1 and self.board[5][5] == 1):
                ai_loose_rows_num += 1
            elif(self.board[5][1] == 1 and self.board[5][5] == -1):
                human_loose_rows_num += 1

            if(self.board[4][1] == -1 and self.board[0][5] == 1):
                ai_loose_rows_num += 1
            if(self.board[4][1] == 1 and self.board[0][5] == -1):
                human_loose_rows_num += 1
            
        if(self.board[5][5] == 0) :
            if(self.board[5][4] == -1 and self.board[5][0] == 1) :
                ai_loose_rows_num += 1
            elif(self.board[5][4] == 1 and self.board[5][0] == -1) :
                human_loose_rows_num += 1
            
            if(self.board[4][5] == -1 and self.board[0][5] == 1):
                ai_loose_rows_num += 1
            elif(self.board[4][5] == 1 and self.board[0][5] == -1):
                human_loose_rows_num += 1

            if(self.board[4][4] == -1 and self.board[0][0] == 1):
                ai_loose_rows_num += 1
            if(self.board[4][4] == 1 and self.board[0][0] == -1):
                human_loose_rows_num += 1

        heuristic += 10*(ai_loose_rows_num - human_loose_rows_num)*self.current_turn

        return heuristic
        
    def get_cpu_move(self):
        moves = self.get_valid_moves(-1)
        if len(moves) == 0:
            return None
        return random.choice(moves)

    def get_human_move(self):
        # TODO
        raise NotImplementedError

    def terminal_test(self):
        return len(self.get_valid_moves(1)) == 0 and len(self.get_valid_moves(-1)) == 0

    def play(self):
        winner = None
        while not self.terminal_test():
            if self.ui:
                self.ui.draw_board(self.board)
            if self.current_turn == 1:
                move = self.get_human_move()
                if move:
                    self.make_move(self.current_turn, move)
            else:
                move = self.get_cpu_move()
                if move:
                    self.make_move(self.current_turn, move)
            self.current_turn = -self.current_turn
            if self.ui:
                self.ui.draw_board(self.board)
                time.sleep(1)
        winner = self.get_winner()
        return winner


othello = Othello(True)
othello.board = [
    [-1, 1 , 1 ,  1 ,  1 ,  0],
    [1 , 1 ,-1 , -1 , -1 ,  1],
    [1 , 1 , 0 , -1 , -1 ,  1],
    [1 , 0 ,-1 ,  1 ,  0 ,  1],
    [1 ,-1 , 0 ,  0 ,  0 ,  1],
    [1 , 1 , 1 ,  1 ,  1 , -1]
]
othello.current_turn=1
print (othello.get_heuristic())