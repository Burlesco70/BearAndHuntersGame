# This is a variant of the Tic Tac Toe recipe given in the easyAI library

from easyAI import TwoPlayersGame, AI_Player, Negamax
from easyAI.Player import Human_Player

class GameController(TwoPlayersGame):
    def __init__(self, players):
        # Define the players
        self.players = players
        # Define who starts the game
        self.nplayer = 1 
        # Define the board
        self.board = ['1', '1', '1', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '2']
        self.bear_position = 20
        self.max_bear_moves = 40
        # Hunter starts
        self.is_hunter_turn = True
        # Bear moves counter
        self.bear_moves = 1        
    
    # Define possible moves
    def possible_moves(self, position):
        # Adjacent locations, index is position
        adjacent = [[1,2,3], #0
                [0,3,4],
                [0,3,6], #2
                [0,1,2,5],
                [1,7,8], #4
                [3,9,10,11],
                [2,12,13], #6
                [4,8,14],
                [7,4,14,9], #8
                [8, 10,5,15],
                [5,9,11,15],#10
                [5,10,15,12],
                [11,6,16,13],#12
                [6,12,16],
                [7,8,18],#14
                [9,10,11,17],
                [12,13,19], #16
                [15,18,19,20],
                [14,17,20], #18
                [16, 17, 20],
                [18, 17, 19]]
        moves = []
        #Check free positions
        for x in adjacent[position]:
            if self._board[x] == '_':
                moves.append(x)
        return moves        
    
    # Make a move
    def make_move(self, starting_position, target_position):
        self.board[starting_position] = '_'
        if self.is_hunter_turn:
            self.board[target_position] = '1'
        else:
            self.bear_moves += 1
            self.bear_position = target_position
            self.board[target_position] = '2'
        # Change turn
        self.is_hunter_turn = not self.is_hunter_turn    
        #assegna il valore della posizione a player
        self.board[int(move) - 1] = self.nplayer

    # Does the opponent have three in a line?
    def loss_condition(self):
        MAX_BEAR_MOVES = 10
        return (self.bear_moves > MAX_BEAR_MOVES)
        
    # Check if the game is over
    def is_over(self):
        # Moves for bear to win
        
        # Combinations for bear to loose, one for each edge position
        # index ease'0,','1', '2', '3', '4', '5', '6', '7', '8', '9', '10, '11, '12, '13  '14, '15, '16, '17, '18, '19, '20
        BEAR_KO = [['2', '1', '1', '1', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_'], # Bear in 0
           ['1', '_', '2', '1', '_', '_', '1', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_'], # Bear in 2
           ['_', '_', '1', '_', '_', '_', '2', '_', '_', '_', '_', '_', '1', '1', '_', '_', '_', '_', '_', '_', '_'], # Bear in 6
           ['_', '_', '_', '_', '_', '_', '1', '_', '_', '_', '_', '_', '1', '2', '_', '_', '1', '_', '_', '_', '_'], # Bear in 13
           ['_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '1', '1', '_', '_', '2', '_', '_', '1', '_'], # Bear in 16
           ['_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '1', '1', '_', '2', '1'], # Bear in 19
           ['_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '1', '1', '1', '2'], # Bear in 20
           ['_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '1', '_', '_', '1', '2', '_', '1'], # Bear in 18
           ['_', '_', '_', '_', '_', '_', '_', '1', '1', '_', '_', '_', '_', '_', '2', '_', '_', '_', '1', '_', '_'], # Bear in 14
           ['_', '_', '_', '_', '1', '_', '_', '2', '1', '_', '_', '_', '_', '_', '1', '_', '_', '_', '_', '_', '_'], # Bear in 7
           ['_', '1', '_', '_', '2', '_', '_', '1', '1', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_'], # Bear in 4
           ['1', '2', '_', '1', '1', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_'], # Bear in 1
          ]
        return (self.board in BEAR_KO) or self.loss_condition()
        
    # Show current position
    def show(self):
        # print board
        print("            "+self.board[0]+"            ","             "+"0"+"            ")
        print("        "+self.board[1]+"       "+self.board[2]+"        ","         "+"1"+"       "+"2"+"        ")
        print("            "+self.board[3]+"            ","             "+"3"+"            ")
        print("  "+self.board[4]+"         "+self.board[5]+"         "+self.board[6]+"  ","   "+"4"+"         "+"5"+"         "+"6"+"  ")
        print(""+self.board[7]+"   "+self.board[8]+"   "+self.board[9]+"   "+self.board[10]+"   "+self.board[11]+"   "+self.board[12]+"   "+self.board[13]+"",
              " "+"7"+"   "+"8"+"   "+"9"+"  "+"10"+"  "+"11"+"  "+"12"+"  "+"13"+"")
        print("  "+self.board[14]+"         "+self.board[15]+"         "+self.board[16]+"  ","  "+"14"+"        "+"15"+"        "+"16"+"")
        print("            "+self.board[17]+"            ","            "+"17"+"            ")
        print("        "+self.board[18]+"       "+self.board[19]+"        ","        "+"18"+"      "+"19"+"        ")
        print("            "+self.board[20]+"            ","            "+"20"+"            ")
                 
    # Compute the score
    def scoring(self):
        return -100 if self.loss_condition() else 0

if __name__ == "__main__":
    # Define the algorithm
    algorithm = Negamax(7)

    # Start the game
    GameController([Human_Player(), AI_Player(algorithm)]).play()

