def is_over(game_board, bear_moves, is_hunter_turn, bear_position):
    '''
    Conditions for end of game
    '''
    # Moves for bear to win
    MAX_BEAR_MOVES = 30
    is_over = False
    if (not is_hunter_turn) and (not possible_moves(game_board, bear_position)):
        is_over = True
        print("Hunters WIN")
    if (bear_moves > MAX_BEAR_MOVES):
        print("Bear WINS")
        is_over = True
    return is_over


def possible_moves(board, position):
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
        if board[x] == '_':
            moves.append(x)
    return moves
    
def print_board(game_board):
    '''
    Very basic print of the board with pawns
    '''
    print("            "+game_board[0]+"            ","             "+"0"+"            ")
    print("        "+game_board[1]+"       "+game_board[2]+"         ","        "+"1"+"       "+"2"+"        ")
    print("            "+game_board[3]+"            ","             "+"3"+"            ")
    print("  "+game_board[4]+"         "+game_board[5]+"         "+game_board[6]+"   ","  "+"4"+"         "+"5"+"         "+"6"+"  ")
    print(""+game_board[7]+"   "+game_board[8]+"   "+game_board[9]+"   "+game_board[10]+"   "+game_board[11]+"    "+game_board[12]+"   "+game_board[13]+"",
          ""+"7"+"   "+"8"+"   "+"9"+"  "+"10"+"  "+"11"+"  "+"12"+"  "+"13"+"")
    print("  "+game_board[14]+"         "+game_board[15]+"         "+game_board[16]+"   "," "+"14"+"        "+"15"+"        "+"16"+"")
    print("            "+game_board[17]+"            ","            "+"17"+"            ")
    print("        "+game_board[18]+"       "+game_board[19]+"        ","        "+"18"+"      "+"19"+"        ")
    print("            "+game_board[20]+"            ","            "+"20"+"            ")
    
def main():
    '''
    The game implementation
    '''
    print("THE GAME OF THE BEAR")
    # init board
    game_board = ['_'] * 21
    # init hunter
    game_board[0] = game_board[1] = game_board[2] = '1'
    # init bear position
    bear_position = 20
    game_board[bear_position] = '2'
    # Hunter starts
    is_hunter_turn = True
    # Bear moves counter
    bear_moves = 1
    # Show the board
    print_board(game_board)
    # Game loop
    while not is_over(game_board,bear_moves,is_hunter_turn, bear_position):
        # Asymmetric turn: hunter choose pawn first
        if is_hunter_turn:
            print("Hunter is playing")
            try:
                # Must be integer
                starting_pos = int(input(" Enter position you want to pick from (0-20): \n").strip())
                # Between 0 and 20
                if starting_pos < 0 or starting_pos > 20:
                    print("Number out of range")
                    raise Exception
                # Belonging to hunter
                if (game_board[starting_pos] != '1'):
                    print("Not your pawn")
                    raise Exception 
            except:
                print("Please enter only valid fields from board (0-20)")
                continue
        # Bear's turn
        else:
            print("Bear is playing move n. ",bear_moves)
            starting_pos = bear_position
        # Target position
        try:
            target_pos = int(input(" Enter target position you want to go to: \n").strip())
            if target_pos not in possible_moves(game_board,starting_pos):
                raise Exception
        except:
            print("Please enter only valid fields from board (0-20)")
            continue
        # Make the move
        game_board[starting_pos] = '_'
        if is_hunter_turn:
            game_board[target_pos] = '1'
        else:
            bear_moves += 1
            bear_position = target_pos
            game_board[target_pos] = '2'
        # Change turn
        is_hunter_turn = not is_hunter_turn
        # Show changes
        print_board(game_board)

if __name__ == "__main__":
    main()