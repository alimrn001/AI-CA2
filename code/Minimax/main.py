import random
import time
import turtle
import numpy as np
import sys
import copy

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
        num_of_human_possible_moves, num_of_ai_possible_moves = 0, 0
        heuristic = 0

        for i in range(0, 5) :
            for j in range (0, 5) :
                if(self.board[i][j] == -1) :
                    ai_tiles += 1
                elif(self.board[i][j] == 1):
                    human_tiles += 1

        if(human_tiles + ai_tiles == 36) :
            if(human_tiles > ai_tiles) :
                return sys.maxsize * (1)
            elif(human_tiles < ai_tiles) :
                return -sys.maxsize * (1)
            else :
                return 0 # match draw case

        heuristic += (human_tiles - ai_tiles)*1
        
        for i in range(0, 10, 5) :
            for j in range(0, 10, 5) :
                if(self.board[i][j] == 1) :
                    human_corners += 1
                elif(self.board[i][j] == -1) :
                    ai_corners += 1

        heuristic += 5*(human_corners - ai_corners) * 1 #coeff can be more than 5 too !
        
        num_of_human_possible_moves = len(self.get_valid_moves(1))
        num_of_ai_possible_moves = len(self.get_valid_moves(-1))

        heuristic += 3*(num_of_human_possible_moves - num_of_ai_possible_moves)

        return heuristic
        
    def minimax(self, depth) :
    
        if(depth==0) :
            returnedVal = (self.get_heuristic(), None)
            return returnedVal
        
        final_move_human, final_move_cpu = None, None

        if(self.current_turn == 1) :
            max_res = -sys.maxsize
            for move in self.get_valid_moves(1) :
                new_board = copy.deepcopy(self.board)
                new_turn = copy.deepcopy(self.current_turn)
                
                new_state = Othello(False, depth)
                new_state.board = new_board
                new_state.current_turn = new_turn
                
                new_state.make_move(self.current_turn,move)
                new_state.current_turn = -self.current_turn
                max_temp = new_state.minimax(depth-1)[0]
                if(max_temp >= max_res) :
                    max_res, final_move_human = max_temp, move
            return max_res, final_move_human

        else :
            min_res = sys.maxsize
            for move in self.get_valid_moves(-1) :
                new_board = copy.deepcopy(self.board)
                new_turn = copy.deepcopy(self.current_turn)
                
                new_state = Othello(False, depth)
                new_state.board = new_board
                new_state.current_turn = new_turn
                
                new_state.make_move(self.current_turn, move)
                new_state.current_turn = -self.current_turn
                min_temp = new_state.minimax(depth-1)[0]
                if(min_temp <= min_res) : 
                    min_res, final_move_cpu = min_temp, move
            return min_res, final_move_cpu
    
    def pruning_minimax(self, depth, max_val, min_val) : #alpha -> max_val , beta -> min_val
        if(depth==0) :
            returnedVal = (self.get_heuristic(), None)
            return returnedVal
        
        final_move_human, final_move_cpu = None, None

        if(self.current_turn == 1) :
            max_res = -sys.maxsize
            for move in self.get_valid_moves(1) :
                new_board = copy.deepcopy(self.board)
                new_turn = copy.deepcopy(self.current_turn)
                new_state = Othello(False, depth)
                new_state.board = new_board
                new_state.current_turn = new_turn
                new_state.make_move(self.current_turn,move)
                new_state.current_turn = -self.current_turn
                
                max_temp = new_state.pruning_minimax(depth-1, max_val, min_val)[0]
                if(max_temp >= max_res) :
                    max_res, final_move_human = max_temp, move
                if(max_res >= min_val) :
                    break
                max_val = max(max_val, max_res)

            return max_res, final_move_human

        else :
            min_res = sys.maxsize
            for move in self.get_valid_moves(-1) :
                new_board = copy.deepcopy(self.board)
                new_turn = copy.deepcopy(self.current_turn)
                new_state = Othello(False, depth)
                new_state.board = new_board
                new_state.current_turn = new_turn
                new_state.make_move(self.current_turn, move)
                new_state.current_turn = -self.current_turn

                min_temp = new_state.pruning_minimax(depth-1, max_val, min_val)[0]
                if(min_temp <= min_res) : 
                    min_res, final_move_cpu = min_temp, move
                if(min_res <= max_val) :
                    break

                min_val = min(min_val, min_res)
            return min_res, final_move_cpu

    def get_cpu_move(self):
        moves = self.get_valid_moves(-1)
        if len(moves) == 0:
            return None
        move = random.choice(moves)        
        return move

    def get_human_move(self):
        # TODO
        if(self.prune) :
            move = self.pruning_minimax(self.minimax_depth, max_val=-sys.maxsize, min_val=sys.maxsize)
        else :    
            move = self.minimax(self.minimax_depth)
            
        return move

    def terminal_test(self):
        return len(self.get_valid_moves(1)) == 0 and len(self.get_valid_moves(-1)) == 0

    def play(self):
        winner = None
        while not self.terminal_test():
            if self.ui:
                self.ui.draw_board(self.board)
            if self.current_turn == 1:
                move = self.get_human_move()
                if move[1] != None:
                    self.make_move(self.current_turn, move[1])
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


####### playing game #######
othello = Othello(True, 5, prune=True)
winner = othello.play()
print('winned by : ',winner)

###### depth = 1 without pruning ######

# stime = time.time()
# numOfHumanWins = 0
# for i in range(200) :
#     othello = Othello(False, 1, False)
#     winner = othello.play()
#     if(winner==1) :
#         numOfHumanWins += 1
# print('minimax simulation without pruning and with depth = 1 and total 200 executions')
# print('human win ratio : ', (numOfHumanWins/200)*100, '%')
# print("time taken :\n--- %s seconds ---" % (time.time() - stime))
# print('\n-----------------------------------\n')


###### depth = 3 without pruning ######

# stime = time.time()
# numOfHumanWins = 0
# for i in range(100) :
#     othello = Othello(False, 3, False) 
#     winner = othello.play()
#     if(winner==1) :
#         numOfHumanWins += 1
# print('minimax simulation without pruning and with depth = 3 and total 100 executions')
# print('human win ratio : ', (numOfHumanWins/100)*100, '%')
# print("time taken :\n--- %s seconds ---" % (time.time() - stime))
# print('\n-----------------------------------\n')

###### depth = 5 without pruning ######

# stime = time.time()
# numOfHumanWins = 0
# for i in range(10) :
#     othello = Othello(False, 5, False) 
#     winner = othello.play()
#     if(winner==1) :
#         numOfHumanWins += 1
# print('minimax simulation without pruning and with depth = 5 and total 10 executions')
# print('human win ratio : ', (numOfHumanWins/10)*100, '%')
# print("time taken :\n--- %s seconds ---" % (time.time() - stime))
# print('\n-----------------------------------\n')



###### depth = 1 with pruning ######

# stime = time.time()
# numOfHumanWins = 0
# for i in range(200) :
#     othello = Othello(False, 1, True) #alpha-betta pruning
#     winner = othello.play()
#     if(winner==1) :
#         numOfHumanWins += 1
# print('minimax simulation with pruning and with depth = 1 and total 200 executions')
# print('human win ratio : ', (numOfHumanWins/200)*100, '%')
# print("time taken :\n--- %s seconds ---" % (time.time() - stime))
# print('\n-----------------------------------\n')


###### depth = 3 with pruning ######

# stime = time.time()
# numOfHumanWins = 0
# for i in range(100) :
#     othello = Othello(False, 3, True) 
#     winner = othello.play()
#     if(winner==1) :
#         numOfHumanWins += 1
# print('minimax simulation without pruning and with depth = 3 and total 100 executions')
# print('human win ratio : ', (numOfHumanWins/100)*100, '%')
# print("time taken :\n--- %s seconds ---" % (time.time() - stime))
# print('\n-----------------------------------\n')


###### depth = 5 with pruning ######

# stime = time.time()
# numOfHumanWins = 0
# for i in range(10) :
#     othello = Othello(False, 5, True) #alpha-betta pruning
#     winner = othello.play()
#     if(winner==1) :
#         numOfHumanWins += 1
# print('minimax simulation with pruning and with depth = 5 and total 10 executions')
# print('human win ratio : ', (numOfHumanWins/10)*100, '%')
# print("time taken :\n--- %s seconds ---" % (time.time() - stime))
# print('\n-----------------------------------\n')

###### depth = 7 with pruning ######

# stime = time.time()
# numOfHumanWins = 0
# for i in range(10) :
#     othello = Othello(False, 7, True) #alpha-betta pruning
#     winner = othello.play()
#     if(winner==1) :
#         numOfHumanWins += 1
# print('minimax simulation with pruning and with depth = 7 and total 10 executions')
# print('human win ratio : ', (numOfHumanWins/10)*100, '%')
# print("time taken :\n--- %s seconds ---" % (time.time() - stime))
# print('\n-----------------------------------\n')

