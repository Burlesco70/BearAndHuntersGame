import sys
from typing import List

class BearBoardCell:
    HUNTER = '1'
    BEAR = '2'
    NONE = '_'


class BearBoard:
    def __init__(self) -> None:
        '''
        Initial position of the pawns
        '''
        self.__cells = [BearBoardCell.NONE] * 21
        self.__cells[0] = self.__cells[1] = self.__cells[2] = BearBoardCell.HUNTER
        self.__bear_position = 20
        self.__cells[self.__bear_position] = BearBoardCell.BEAR

    def get_bear_position(self) -> int:
        return self.__bear_position
    
    def is_hunter_position(self, position) -> bool:
        return self.__cells[position] == BearBoardCell.HUNTER

    def move(self, starting_position, target_position, is_hunter_turn) -> None:
        '''
        Moves pawn
        '''
        self.__cells[starting_position] = BearBoardCell.NONE
        if is_hunter_turn:
            self.__cells[target_position] = BearBoardCell.HUNTER
        else:
            self.__bear_position = target_position
            self.__cells[target_position] = BearBoardCell.BEAR

    def possible_moves(self, position) -> List[int]:
        '''
        Return possible moves (adjacent free positiion)
        '''        
        #Adjacent locations
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
            if self.__cells[x] == BearBoardCell.NONE:
                moves.append(x)
        return moves        

    def __str__(self) -> None:
        '''
        Very basic print of itself
        '''
        return ''.join(("            ",self.__cells[0], "                          0            \n",
            "        ", self.__cells[1], "       ", self.__cells[2], "                  1       2        \n",
            "            ",self.__cells[3],"            ","             "," 3","            \n",
            "  ",self.__cells[4],"         ",self.__cells[5],"         ",self.__cells[6],"      4         5         6  \n",
            self.__cells[7],"   ",self.__cells[8],"   ",self.__cells[9],"   ",self.__cells[10],"   ",self.__cells[11],"    ",self.__cells[12],"   ",self.__cells[13], " 7   8   9  10  11  12  13\n",
            "  ",self.__cells[14],"         ",self.__cells[15],"         ",self.__cells[16],"     14        15        16\n",
            "            ",self.__cells[17],"                         17            \n",
            "        ",self.__cells[18],"       ",self.__cells[19],"                 18      19        \n",
            "            ",self.__cells[20],"                         20            \n"))

class BearGame:
    MAX_BEAR_MOVES=30
    BEAR_STARTS=True

    def __init__(self) -> None:
        self.board = BearBoard()
        self.bear_moves = 1
        self.is_hunter_turn = False if self.BEAR_STARTS else True
        self.winner = None
        print(self.board)
    
    def is_over(self) -> bool:
        '''
        Conditions for end of game
        '''
        # Moves for bear to win
        is_over = False
        if (not self.is_hunter_turn) and (not self.board.possible_moves(self.board.get_bear_position())):
            is_over = True
            self.winner = "HUNTER"
            print("The BEAR is surrounded by the hunders...")
        if (self.bear_moves > self.MAX_BEAR_MOVES):
            is_over = True
            self.winner = "BEAR"
            print(f"Bear moves are {self.MAX_BEAR_MOVES}.\nThe BEAR has escaped...")
        return is_over        

    def game_loop(self) -> None:
        '''
        Game loop for the game
        - Move request (2 requests for hunters, 1 request for bear)
        - Checks for valid move
        - Move
        - Show board changes
        '''
        while not self.is_over():
            # Asymmetric turn: hunter choose pawn first
            if self.is_hunter_turn:
                print("Hunter is playing")
                try:
                    # Must be integer
                    starting_pos = int(input(" Enter position you want to pick from (0-20):\n").strip())
                    # Between 0 and 20
                    if starting_pos < 0 or starting_pos > 20:
                        print("Number out of range")
                        raise ValueError
                    # Belonging to hunter
                    if not self.board.is_hunter_position(starting_pos):
                        print("Not your pawn")
                        raise ValueError 
                except KeyboardInterrupt:
                    print('\nGame aborted.')
                    sys.exit(0)
                except ValueError:
                    print("Please enter only valid hunter position in the board (0-20)")
                    continue
            # Bear's turn
            else:
                print("Bear is playing move n. ",self.bear_moves)
                starting_pos = self.board.get_bear_position()
            # Target position
            try:
                target_pos = int(input(f"Enter target adjacent position {self.board.possible_moves(starting_pos)} you want to go to: \n").strip())
                if target_pos not in self.board.possible_moves(starting_pos):
                    raise ValueError
            except KeyboardInterrupt:
                print('\nGame aborted.')
                sys.exit(0)                
            except ValueError:
                print(f"Please enter only valid adjacent target position in the board {self.board.possible_moves(starting_pos)}")
                continue
            # Make the move
            if not self.is_hunter_turn:
                self.bear_moves += 1
            self.board.move(starting_pos, target_pos, self.is_hunter_turn)              
            # Change turn           
            self.is_hunter_turn = not self.is_hunter_turn
            # Show changes
            print(self.board)


if __name__ == "__main__":
    bg  = BearGame()
    bg.game_loop()
    print(f"GAME OVER!\n{bg.winner} WINS")