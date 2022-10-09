'''
Versione del gioco "finale" dopo il corso su PyGame
1 - https://youtu.be/rdT_Z23YRAY
2 - https://youtu.be/xG4IKcAzMCw
3 - https://youtu.be/V3VuqFeJ1hc
ovvero con utilizzo di Sprites e gruppi di collisioni
e maggiore orientamento OOP
10-2022 - Aggiunta AI Orso
'''

from __future__ import annotations

from json.encoder import INFINITY
import os
import pygame
import time
import sys
import functools
import random
import pickle

# Temporary folder for PyInstaller
try:
    base_path = sys._MEIPASS
except AttributeError:
    base_path = os.path.abspath(".")

# Palette - RGB colors
BLACK = (0, 0, 0)

# Symbols for the board of game
BOARD_HUNTER_1 = '1'
BOARD_HUNTER_2 = '8'
BOARD_HUNTER_3 = '9'
BOARD_BEAR = '2'
BOARD_EMPTY = '_'
# Symbols for the board of policy
# Unlink dependency logic between board game and board policy
BOARD_HUNTER_POLICY = '1'

class BearGame:
    '''
    PyGame independent game class
    Class for logical board and game model
    21 positions:
    _ means empty;
    1-8-9 means hunters; 
    2 means bear;
    '''
    # Winner messages and settings
    HUNTERS_WIN = 'Hanno vinto i cacciatori!'
    BEAR_WINS = "Ha vinto l'orso, congratulazioni"    
    
    BOARD_POSITIONS = 21
    # Adjacent positions in the board, list index is the board  position
    ADJACENT_POSITIONS = [[1,2,3], #0
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

    def __init__(self, player_mode: int, max_bear_moves: int, hunter_starts: bool):
        # Start settings
        self.reset(player_mode, max_bear_moves, hunter_starts)
        # Reinforcement learning loading for Bear AI
        self._bear_player = Player("orso")
        self._bear_player.load_policy(
            os.path.join(base_path, "bear.policy")
        )

        
    def reset(self, player_mode: int, max_bear_moves: int, hunter_starts: bool) -> None:
        # Start and reset settings
        self._board = [BOARD_HUNTER_1, BOARD_HUNTER_2, BOARD_HUNTER_3, BOARD_EMPTY, BOARD_EMPTY, BOARD_EMPTY, BOARD_EMPTY,
                       BOARD_EMPTY, BOARD_EMPTY, BOARD_EMPTY, BOARD_EMPTY, BOARD_EMPTY, BOARD_EMPTY, BOARD_EMPTY,
                       BOARD_EMPTY, BOARD_EMPTY, BOARD_EMPTY, BOARD_EMPTY, BOARD_EMPTY, BOARD_EMPTY, BOARD_BEAR]
        # Init settings
        self._bear_position = 20
        self._bear_moves = 0
        self._hunter_starting_pos = -1
        # From external configuration
        self._is_hunter_turn = hunter_starts        
        self._max_bear_moves = max_bear_moves
        self.player_mode = player_mode
        self._winner = None
        self._last_move = None


    def get_bear_moves(self) -> int:
        '''
        Counter of bear moves
        '''
        return self._bear_moves


    def get_max_bear_moves(self) -> int:
        '''
        Max bear moves
        '''
        return self._max_bear_moves

    def get_board_position(self, position:int) -> str:
        '''
        Return the pown of the input position
        '''
        return self._board[position]

    def get_hunter_starting_pos(self) -> int:
        '''
        Return the hunter starting position
        '''
        return self._hunter_starting_pos
    
    def is_bear_winner(self) -> bool:
        '''Returns the winner in a string type for display purposes'''
        if not(self.get_possible_moves(self._bear_position)):
            return False
        if (self._bear_moves >= self._max_bear_moves):
            return True

    def game_over(self) -> bool:
        '''Check for game over'''
        if not(self.get_possible_moves(self._bear_position)):
            self._winner = BearGame.HUNTERS_WIN
            return True
        elif (self._bear_moves >= self._max_bear_moves):
            self._winner = BearGame.BEAR_WINS
            return True
        else:
            return False

    def is_hunter(self, selection:str) -> bool:
        '''Check if selection is an hunter'''
        return selection in [BOARD_HUNTER_1, BOARD_HUNTER_2, BOARD_HUNTER_3]

    def is_hunter_turn(self) -> bool:
        '''Check if is it the hunter turn'''
        return self._is_hunter_turn

    def manage_hunter_selection(self, sel:int) -> str:
        '''Input selection from user; return user message to display'''
        selected_hunter = ''
        # Pick up pawn (starting pos -1)
        if self._hunter_starting_pos == -1:
            if (not(self.is_hunter(self._board[sel]))):
                return "Seleziona un cacciatore!"
            else:
                self._hunter_starting_pos = sel
                return "Cacciatore, fa' la tua mossa!"
        else: # Finding final position for hunter
            if sel in self.get_possible_moves(self._hunter_starting_pos):
                selected_hunter = self._board[self._hunter_starting_pos]
                self._board[self._hunter_starting_pos] = BOARD_EMPTY
                self._board[sel] = selected_hunter
                self._hunter_starting_pos = -1
                self._is_hunter_turn = not(self._is_hunter_turn)
                return "Orso, scegli la tua mossa!"
            else: # Go back to picking stage
                self._hunter_starting_pos = -1
                return "Posizione non valida!"
    
    def manage_ai_hunter_selection(self) -> str:
        '''
        Implement stupid random logic
        '''
        # Simula il comportamento umano: prima sceglie il cacciatore
        if (self._hunter_starting_pos == -1):
            # Cerca le posizioni dei cacciatori
            # self._hunter_starting_pos = -1
            hunter_positions = []
            for x in range(self.BOARD_POSITIONS):
                if self._board[x] == BOARD_HUNTER_1 or self._board[x] == BOARD_HUNTER_2 or self._board[x] == BOARD_HUNTER_3:
                    hunter_positions.append(x)
            #print("Board", self._board)
            #print("Posizioni cacciatori", hunter_positions)
            # Sceglie cacciatore a caso
            random_hunter = random.randint(0,2)
            # Posizione del cacciatore
            stupid_hunter_selection = hunter_positions[random_hunter]
            # Verifica che abbia almeno una mossa disponibile... altrimenta va dagli altri
            move_options = len(self.get_possible_moves(stupid_hunter_selection))
            #print("Posizione cacciatore casuale", stupid_hunter_selection)
            while move_options <= 0:
                random_hunter = (random_hunter + 1) % 3
                stupid_hunter_selection = hunter_positions[random_hunter]
                #print("Posizione cacciatore casuale", stupid_hunter_selection)
                move_options = len(self.get_possible_moves(stupid_hunter_selection))
            self._hunter_starting_pos = stupid_hunter_selection
            #print(move_options, self._hunter_starting_pos)
            return "Cacciatore selezionato"
        # Poi la mossa
        else:
            # Seleziona la mossa causale
            # Move options
            move_options = len(self.get_possible_moves(self._hunter_starting_pos))
            # Select random move
            stupid_hunter_new_pos = self.get_possible_moves(self._hunter_starting_pos)[random.randint(0,move_options-1)]          
            # Selected hunter makes the move        
            hunter_to_move = self._board[self._hunter_starting_pos]
            self._board[self._hunter_starting_pos] = BOARD_EMPTY
            self._board[stupid_hunter_new_pos] = hunter_to_move
            self._hunter_starting_pos = -1
            self._is_hunter_turn = not(self._is_hunter_turn)
            time.sleep(1)
            return "Orso, scegli la tua mossa!"

    def get_bear_actions(self) -> list[(int, int)]:
        '''
        Return a list of tuples with starting pos and next possible move
        '''
        actions = []
        for adj in BearGame.ADJACENT_POSITIONS[self._bear_position]:
            if self._board[adj] == BOARD_EMPTY:
                actions.append((self._bear_position, adj))
        return actions

    def move_bear(self, new_position: int) -> None:
        '''
        Move bear to a random position
        '''
        self._last_move = (self._bear_position, new_position)
        if new_position in self.get_possible_moves(self._bear_position):
            self._board[self._bear_position] = BOARD_EMPTY
            self._board[new_position] = BOARD_BEAR
            self._bear_position = new_position
            self._bear_moves += 1
            self._is_hunter_turn = not self._is_hunter_turn
        else:
            print(self._last_move)
            raise ValueError("Orso non può muoversi qui!")

    def get_hash(self) -> str:
        '''
        Return a hash of the board
        '''
        board = self._board.copy()
        # normalize the hunter ids for the Reinforcement model
        # unlink dependency logic between board game and board policy
        for i in range(len(board)):
            if board[i] == BOARD_HUNTER_3 or board[i] == BOARD_HUNTER_2 or board[i] == BOARD_HUNTER_1:
                board[i] = BOARD_HUNTER_POLICY
        return ''.join(board)

    def undo_move(self) -> None:
        '''Undo the move'''
        self._is_hunter_turn = not self._is_hunter_turn
        target_position, starting_position = self._last_move  # contrario!
        self._board[starting_position] = BOARD_EMPTY
        if self._is_hunter_turn:
            self._board[target_position] = BOARD_HUNTER_1
        else:
            self._bear_moves -= 1
            self._bear_position = target_position
            self._board[target_position] = BOARD_BEAR
        self._last_move = None

    def move_player(self, start_pos, end_pos) -> str:
        '''
        Move player to a random position
        '''
        if self._is_hunter_turn:
            return self.move_hunter(start_pos, end_pos)
        else:
            return self.move_bear(end_pos)

    def manage_ai_smart_bear_selection(self) -> str:
        '''
        Implement AI logic
        '''
        bear_actions = self.get_bear_actions()
        action = self._bear_player.get_action(bear_actions, self)
        self.move_bear(action[1])
        return "L'orso intelligente ha mosso!"
    
    def manage_ai_bear_selection(self) -> str:
        '''
        Implement stupid random logic
        '''
        move_options = len(self.get_possible_moves(self._bear_position))
        stupid_bear_new_pos = self.get_possible_moves(self._bear_position)[random.randint(0,move_options-1)]
        #print(move_options, bear_pos)
        time.sleep(1)
        # Bear makes the move
        self._board[self._bear_position] = BOARD_EMPTY
        self._board[stupid_bear_new_pos] = BOARD_BEAR
        self._bear_moves += 1
        self._bear_position = stupid_bear_new_pos
        self._is_hunter_turn = not(self._is_hunter_turn)
        return "Seleziona uno dei cacciatori!"

    def manage_bear_selection(self,sel: int) -> str:
        '''Input selection from user; return user message to display'''
        if sel in self.get_possible_moves(self._bear_position):
            # Bear makes the move
            self._board[self._bear_position] = BOARD_EMPTY
            self._board[sel] = BOARD_BEAR
            self._bear_moves += 1
            self._bear_position = sel
            self._is_hunter_turn = not(self._is_hunter_turn)
            return "Seleziona uno dei cacciatori!"
        else:
            return "Posizione non valida..."
    
    def is_footprint_and_type(self, sel:int) -> tuple[bool, str]:
        '''
        Return a tuple:
        - if is a footprint
        - footprint type (HUNTER|BEAR), None if is not a footprint
        '''
        if self._is_hunter_turn:
            if self._hunter_starting_pos == -1:
                return (False, None)
            else:
                if sel in self.get_possible_moves(self._hunter_starting_pos):
                    return (True, "HUNTER")
                else:
                    return (False, None)
        else:
            if sel in self.get_possible_moves(self._bear_position):
                return (True, "BEAR")
            else:
                return (False, None)

    def get_possible_moves(self, position: int) -> list[int]:
        '''
        Returns the list with possible free positions
        '''
        moves = []
        #Check free positions
        for x in BearGame.ADJACENT_POSITIONS[position]:
            if self._board[x] == BOARD_EMPTY:
                moves.append(x)
        return moves

# Metodo per ottimizzare il caricamento degli assets
# "lru_cache" decorator saves recent images into memory for fast retrieval.
@functools.lru_cache()
def get_img(path):
    return pygame.image.load(path)

@functools.lru_cache()
def get_img_alpha(path):
    return pygame.image.load(path).convert_alpha()

class OrsoPyGame():
    # Create the window
    FINESTRA_X=1536
    FINESTRA_Y=864
    DIM_CASELLA = 80

    def __init__(self):
        # Initialize pygame
        pygame.init()
        #self.screen = pygame.display.set_mode((OrsoPyGame.FINESTRA_X, OrsoPyGame.FINESTRA_Y))
        self.screen = pygame.display.set_mode((OrsoPyGame.FINESTRA_X, OrsoPyGame.FINESTRA_Y), pygame.FULLSCREEN)
        pygame.display.set_caption("Gioco dell'orso")
        # set game clock
        self.clock = pygame.time.Clock()
        self._load_assets_menu()
        self._load_assets_game()
        # Gestione caselle: posizione e gruppo sprite
        self._caselle = [(730,0), (565,5), (900,5), #0,1,2
                    (730,135), (350,225), (730,225), #3,4,5
                    (1115,225), (315,385), (465,385), #6,7,8
                    (565,385), (730,385), (900,385), #9,10,11
                    (995,385), (1155,385), (350,565), #12,13,14
                    (730,565), (1115,565), (730,655), #15,16,17
                    (565,775), (900,775), (730,800)] #18.19.20
        # Creazione gruppo caselle
        self._lista_caselle = pygame.sprite.Group()
        for i,p in enumerate(self._caselle):
            #print(i,p)
            pos = CasellaGiocoOrso(i, self)
            # Definisco rect ma non image
            pos.rect = pygame.Rect(p[0],p[1], OrsoPyGame.DIM_CASELLA, OrsoPyGame.DIM_CASELLA)
            self._lista_caselle.add(pos)

    def _load_assets_game(self) -> None:
        '''Caricamento assets del gioco'''
        self.USCITA_IMG = get_img('images/back.png')
        self.USCITA_RECT = self.USCITA_IMG.get_rect()
        self.USCITA_RECT.center = (1355,675)
        self.ORSO_VINCE = get_img_alpha("images/Lorso-vince.png")
        self.CACCIATORI_VINCONO = get_img_alpha("images/Vincono-i-cacciatori.png")
        # Scacchiera
        self.BOARD_IMG = get_img('images/board.png')

    def _load_assets_menu(self) -> None:
        '''Caricamento assets menu'''
        # grafica titolo creata con https://textcraft.net/
        self.ORSO_IDLE_IMG = get_img('images/little-bear-idle.png')
        self.TRE_CACCIATORI_IMG = get_img('images/TreCacciatoriTurno.png')

        self.TITOLO = get_img_alpha("images/Gioco-dellorso.png")
        self.MENU_BACKGROUND = get_img("images/3d_board.png")

    def menu(self) -> None:
        '''
        Display main menu with PyGame
        '''
        pygame.mixer.music.load('sounds/intro.wav')
        pygame.mixer.music.play(-1)

        # Elementi di sfondo
        self.screen.blit(self.MENU_BACKGROUND, (0, 0))#
        self.screen.blit(self.TITOLO, (500,20))
        self.screen.blit(self.ORSO_IDLE_IMG, (250, 420))
        self.screen.blit(self.TRE_CACCIATORI_IMG, (1200, 420))
        
        # Creo gruppo sprite per menu
        self._menu_items = pygame.sprite.Group()
        self._m_inizio = OpzioneMenuInizioGioco(self)
        self._menu_items.add(self._m_inizio)
        self._m_uscita = OpzioneMenuUscita(self)
        self._menu_items.add(self._m_uscita)
        
        # Voci menu centrale
        # Opzione menu Player Vs AI
        self.OPZIONI_PLAYER_MODE = {
            10:"Gioca contro l'orso intelligente      ",
            20:'Gioca contro i cacciatori stupidi     ',
            30:'Gioca contro un amico                 ',
        }
        self._m_pl_mode = OpzioneMenuPlayerType(self.OPZIONI_PLAYER_MODE, 10, self, (580,350)) #305
        self._menu_items.add(self._m_pl_mode)
        # Opzione menu Mosse
        self.OPZIONI_MOSSE = {
            20:'Partita veloce (20 mosse)              ',
            30:'Partita standard (30 mosse)            ',
            40:'Partita classica (40 mosse)            '
        }
        self._m_mosse = OpzioneMenuNumeroMosse(self.OPZIONI_MOSSE, 30, self, (580,440))
        self._menu_items.add(self._m_mosse)
        # Opzione menu Turno
        self.OPZIONI_TURNO = {
            True:'Iniziano i cacciatori                ',
            False:"Inizia l'orso                       "
            }
        self._m_inizia_cacciatore = OpzioneMenuInizoTurno(self.OPZIONI_TURNO, True, self, (580,530)) 
        self._menu_items.add(self._m_inizia_cacciatore)

        self._pos_call = (0, 0)
        self._running = True
        while self._running:
            self._pos_call = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._running = False
                    self._quit()
                elif event.type == pygame.MOUSEBUTTONDOWN:                
                    self._pos_call = pygame.mouse.get_pos()
                    for m_item in self._menu_items:
                        if m_item.rect.collidepoint(self._pos_call):
                            m_item.action()
            # Aggiorna gli items di menu
            self._menu_items.update()
            self._menu_items.draw(self.screen)
            # Aggiorna lo screen
            pygame.display.update()

    def _quit(self):
        '''Uscita dal gioco'''
        pygame.time.delay(500)
        pygame.mixer.music.fadeout(500)
        pygame.mixer.music.stop()
        pygame.quit()
        sys.exit()

    def _menu_call(self):
        '''Richiamo menu'''
        pygame.time.delay(500)
        pygame.mixer.music.fadeout(500)
        self.menu()

    def game(self, player_mode: int, numero_mosse: int, inizia_cacciatore: bool):
        '''Gioco implementato con PyGame'''
        pygame.mixer.music.load('sounds/orso_music.ogg')
        pygame.mixer.music.play(-1)
        # Inizializza la scacchiera e il gioco
        self.gioco_orso = BearGame(player_mode, numero_mosse, inizia_cacciatore)
        self._msg = "L'orso vince facendo "+str(self.gioco_orso.get_max_bear_moves())+" mosse"
         # Creazione gruppo elementi di HUD
        self._hud = pygame.sprite.Group()
        self._h_turno = HudTurno(self)
        self._h_mosse = HudMosseOrso(self)
        self._h_msg = HudMessaggi(self)        
        self._hud.add(self._h_turno)
        self._hud.add(self._h_mosse)
        self._hud.add(self._h_msg)       
        # Inizializzazioni
        self._running = True
        self._pos_call = (0, 0)
        self._selezione = None   
        while self._running:
            # Se è turno AI deve procedere senza verificare click utente
            if (self.gioco_orso.player_mode == 10) and (not self.gioco_orso.is_hunter_turn()):
                #self._msg = self.gioco_orso.manage_ai_bear_selection()
                self._msg = self.gioco_orso.manage_ai_smart_bear_selection()
            if (self.gioco_orso.player_mode == 20) and (self.gioco_orso.is_hunter_turn()):
                self._msg = self.gioco_orso.manage_ai_hunter_selection()
            # Check eventi
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._running = False
                    self._menu_call()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self._pos_call = pygame.mouse.get_pos()
                    # Verifica se click su freccia per uscita
                    if self.USCITA_RECT.collidepoint(self._pos_call):
                        self._running = False
                        self._menu_call()
                    # Controlla click nelle caselle
                    for casella_cliccata in self._lista_caselle:
                        if casella_cliccata.rect.collidepoint(self._pos_call):
                            self._selezione = casella_cliccata.position
                            # Controlla e aggiorna gli spostamenti nella scacchiera
                            # Se click in posizione non corretta, ritorna solo un messaggio
                            if self.gioco_orso.player_mode == 30:                                
                                if (self.gioco_orso.is_hunter_turn()):
                                    self._msg = self.gioco_orso.manage_hunter_selection(self._selezione)
                                else:
                                    self._msg = self.gioco_orso.manage_bear_selection(self._selezione)
                            elif ((self.gioco_orso.player_mode == 10) and (self.gioco_orso.is_hunter_turn())):                                    
                                    self._msg = self.gioco_orso.manage_hunter_selection(self._selezione)
                            elif ((not self.gioco_orso.is_hunter_turn()) and (self.gioco_orso.player_mode == 20)):                                    
                                    self._msg = self.gioco_orso.manage_bear_selection(self._selezione)
            self.clock.tick(60)
            # Disegna la scacchiera
            self.screen.blit(self.BOARD_IMG, (0, 0))
            # Pannello uscita
            self.screen.blit(self.USCITA_IMG, (1250, 580))
            # Aggiorna le caselle
            self._lista_caselle.update()
            self._lista_caselle.draw(self.screen)
            # Aggiorna HUD
            self._hud.update()
            self._hud.draw(self.screen)
            # Check fine del gioco
            if self.gioco_orso.game_over():
                #self._msg = self.gioco_orso.get_winner_display()
                self._msg = self.gioco_orso._winner
                if self.gioco_orso.is_bear_winner():
                    pygame.mixer.Channel(1).play(pygame.mixer.Sound('sounds/orso_ride.wav'))
                    self.screen.blit(self.ORSO_VINCE, (580,380))
                else:
                    pygame.mixer.Channel(1).play(pygame.mixer.Sound('sounds/cacciatori_ridono.wav'))
                    self.screen.blit(self.CACCIATORI_VINCONO, (480,380))
            # Aggiornamento screen
            pygame.display.update()
            # Reset del gioco
            if self.gioco_orso.game_over():
                time.sleep(5)
                # Si inverte chi inizia
                inizia_cacciatore = not(inizia_cacciatore)
                if inizia_cacciatore:
                    self._msg = "Ricominciano i cacciatori"
                else:
                    self._msg = "Ricomincia l'orso"
                self.gioco_orso.reset(player_mode, numero_mosse, inizia_cacciatore)


# Classi opzioni di menu
class OpzioneMenu(pygame.sprite.Sprite):
    '''
    Classe generica di opzione menu, richiede
    - opzioni come dizionario valore:voce da visualizzare
    - valore iniziale di default
    - gioco orso
    - posizione del pannello di sfondo
    '''
    PANNELLO_UNO_IMG = get_img('images/buttonLong.png') #panel
    def __init__(self, opzioni: dict, default_value: object, game: OrsoPyGame, position: tuple):
        super().__init__()
        self.game = game
        self.LOBSTER_30 = pygame.font.Font('fonts/LobsterTwo-Regular.otf',30)
        # Iniziano i cacciatori è il default
        self.value = default_value
        self.opzioni = opzioni
        self.position = position

    def update(self):
        self.game.screen.blit(OpzioneMenuNumeroMosse.PANNELLO_UNO_IMG, self.position)
        self._text = self.LOBSTER_30.render(
            self.opzioni[self.value], 
            1, 
            BLACK)
        self.rect = self._text.get_rect()
        self.rect.x = self.position[0]+20
        self.rect.y = self.position[1]+25
        self.image = self._text

    def action(self):
        raise NotImplementedError("Action must be implemented by child class")


class OpzioneMenuInizoTurno(OpzioneMenu):
    def action(self):
        self.value = not(self.value)


class OpzioneMenuPlayerType(OpzioneMenu):
    def action(self):
        self.value += 10
        if self.value == 40:
            self.value = 10


class OpzioneMenuNumeroMosse(OpzioneMenu):
    def action(self):
        self.value += 10
        if self.value == 50:
            self.value = 20


class OpzioneMenuUscita(pygame.sprite.Sprite):
    '''Menu: uscita'''
    def __init__(self, game: OrsoPyGame):
        super().__init__()
        self.game = game
        self.ESCI_GIOCO = get_img('images/buttonLong.png')
        self.ESCI_GIOCO_STR = get_img_alpha("images/Esci-dal-gioco.png")


    def update(self):
        self.game.screen.blit(self.ESCI_GIOCO, (100, 680))
        self.rect = self.ESCI_GIOCO_STR.get_rect()
        self.rect.x = 170
        self.rect.y = 690
        self.image = self.ESCI_GIOCO_STR

    def action(self):
        self.game._running = False
        self.game._quit()
    

class OpzioneMenuInizioGioco(pygame.sprite.Sprite):
    '''Menu: inizio'''
    def __init__(self, game: OrsoPyGame):
        super().__init__()
        self.game = game
        self.INIZIA = get_img('images/buttonLong.png')
        self.INIZIA_STR = get_img_alpha("images/Inizia-a-giocare.png")


    def update(self):
        self.game.screen.blit(self.INIZIA, (1100, 680))
        self.rect = self.INIZIA_STR.get_rect()
        self.rect.x = 1140
        self.rect.y = 700
        self.image = self.INIZIA_STR

    def action(self):
        self.game._running = False
        pygame.time.delay(800)
        # fade out menu music
        pygame.mixer.music.fadeout(800)
        self.game.game(
            self.game._m_pl_mode.value,
            self.game._m_mosse.value, 
            self.game._m_inizia_cacciatore.value
        )
  

# Classi HUD di gioco
class HudTurno(pygame.sprite.Sprite):
    '''HUD: pannello per il turno'''
    ORSO_IDLE_IMG = get_img('images/little-bear-idle.png')
    TRE_CACCIATORI_IMG = get_img('images/TreCacciatoriTurno.png')
    
    PANNELLO_DUE_IMG = get_img('images/panel.png') #panel_due
 
    def __init__(self, game: OrsoPyGame):
        super().__init__()
        self.game = game
        self.LOBSTER_45 = pygame.font.Font('fonts/LobsterTwo-Regular.otf',45)

        self._turno_str = self.LOBSTER_45.render("Turno", 1, BLACK)

    def update(self): 
        # Inizializzazione Pannello turno, parte fissa
        self.game.screen.blit(HudTurno.PANNELLO_DUE_IMG, (1250, 80))        
        self.game.screen.blit(self._turno_str, (1300, 90))          
        if self.game.gioco_orso._is_hunter_turn:
            self.rect = HudTurno.TRE_CACCIATORI_IMG.get_rect()
            self.rect.x = 1265
            self.rect.y = 160
            self.image = HudTurno.TRE_CACCIATORI_IMG
        else:
            self.rect = HudTurno.ORSO_IDLE_IMG.get_rect()
            self.rect.x = 1320
            self.rect.y = 160
            self.image = HudTurno.ORSO_IDLE_IMG


class HudMosseOrso(pygame.sprite.Sprite):
    '''HUD: pannello per il contatore mosse orso'''
    PANNELLO_DUE_IMG = get_img('images/panel.png') #panel_due

    def __init__(self, game: OrsoPyGame):
        super().__init__()
        self.game = game
        self.LOBSTER_45 = pygame.font.Font('fonts/LobsterTwo-Regular.otf',45)
        self.LOBSTER_90 = pygame.font.Font('fonts/LobsterTwo-Regular.otf',90)
        # Pannello mosse orso
        self._mosse_str = self.LOBSTER_45.render("Mosse orso", 1, BLACK)     
            
    def update(self):
        self._mosse = self.LOBSTER_90.render(str(self.game.gioco_orso.get_bear_moves()), 1, BLACK)       
        self.game.screen.blit(HudMosseOrso.PANNELLO_DUE_IMG, (80, 80))  
        self.game.screen.blit(self._mosse_str, (90, 90))  
        self.rect = self._mosse.get_rect()
        self.rect.x = 145
        self.rect.y = 140
        self.image = self._mosse


class HudMessaggi(pygame.sprite.Sprite):
    '''HUD: pannello per i messaggi'''    
    PANNELLO_UNO_IMG = get_img('images/buttonLong.png') #panel

    def __init__(self, game: OrsoPyGame):
        super().__init__()
        self.game = game
        self.LOBSTER_30 = pygame.font.Font('fonts/LobsterTwo-Regular.otf',30)

    def update(self):
        self._text = self.LOBSTER_30.render(self.game._msg, 1, BLACK)
        self.game.screen.blit(self.PANNELLO_UNO_IMG, (40, 680))
        self.rect = self._text.get_rect()
        self.rect.x = 50
        self.rect.y = 705
        self.image = self._text


class CasellaGiocoOrso(pygame.sprite.Sprite):
    '''
    Oggetto casella del gioco
    Gestisce la visualizzazione di personaggi e orme
    '''
    # Static resources
    TRASPARENTE = pygame.Surface((80,80), pygame.SRCALPHA)

    ORSO_IMG = get_img('images/little-bear.png')
    ORSO_IDLE_IMG = get_img('images/little-bear-idle.png')
    ORSO_SEL_IMG = get_img('images/little-bear-sel.png')

    CACCIATORE_UNO_IMG = get_img('images/little-hunter1.png')
    CACCIATORE_UNO_IDLE_IMG = get_img('images/little-hunter1-idle.png')
    CACCIATORE_UNO_SEL_IMG = get_img('images/little-hunter1-sel.png')

    CACCIATORE_DUE_IMG = get_img('images/little-hunter2.png')
    CACCIATORE_DUE_IDLE_IMG = get_img('images/little-hunter2-idle.png')
    CACCIATORE_DUE_SEL_IMG = get_img('images/little-hunter2-sel.png')

    CACCIATORE_TRE_IMG = get_img('images/little-hunter3.png')
    CACCIATORE_TRE_IDLE_IMG = get_img('images/little-hunter3-idle.png')
    CACCIATORE_TRE_SEL_IMG = get_img('images/little-hunter3-sel.png')
        
    # Orme
    ORMA_ORSO_IMG = get_img('images/impronta_orso.png')
    ORMA_CACCIATORE_IMG = get_img('images/impronta_cacciatore.png')

    def __init__(self, position: int, game: OrsoPyGame):
        super().__init__()
        self.position = position
        self.game = game

    def update(self):
        '''Valorizza l'attributo image dello sprite'''
        # Disegna la pedine ottenendo la board dall'oggetto gioco
        bb = self.game.gioco_orso
        if bb.get_board_position(self.position) == BOARD_EMPTY:
            # Controllo se è orma
            is_orma, tipo_orma  = bb.is_footprint_and_type(self.position)            
            if is_orma:
                if tipo_orma == 'HUNTER':
                    self.image = CasellaGiocoOrso.ORMA_CACCIATORE_IMG
                else:
                    self.image = CasellaGiocoOrso.ORMA_ORSO_IMG                    
            else:
                self.image = CasellaGiocoOrso.TRASPARENTE
        # Verifica se è orso
        elif bb.get_board_position(self.position) == BOARD_BEAR:            
            if not bb.is_hunter_turn():
                self.image = CasellaGiocoOrso.ORSO_SEL_IMG
            else:
                self.image = CasellaGiocoOrso.ORSO_IMG
        # Verifica se è uno dei cacciatori
        elif bb.get_board_position(self.position) == BOARD_HUNTER_1:
            if (bb.get_hunter_starting_pos() == self.position):
                self.image = CasellaGiocoOrso.CACCIATORE_UNO_SEL_IMG
            else:
                if bb.is_hunter_turn():
                    self.image = CasellaGiocoOrso.CACCIATORE_UNO_IMG
                else:
                    self.image = CasellaGiocoOrso.CACCIATORE_UNO_IDLE_IMG
        elif bb.get_board_position(self.position) == BOARD_HUNTER_2:
            if (bb.get_hunter_starting_pos() == self.position):
                self.image = CasellaGiocoOrso.CACCIATORE_DUE_SEL_IMG
            else:
                if bb.is_hunter_turn():
                    self.image = CasellaGiocoOrso.CACCIATORE_DUE_IMG
                else:
                    self.image = CasellaGiocoOrso.CACCIATORE_DUE_IDLE_IMG
        elif bb.get_board_position(self.position) == BOARD_HUNTER_3:
            if (bb.get_hunter_starting_pos() == self.position):
                self.image = CasellaGiocoOrso.CACCIATORE_TRE_SEL_IMG
            else:
                if bb.is_hunter_turn():
                    self.image = CasellaGiocoOrso.CACCIATORE_TRE_IMG
                else:
                    self.image = CasellaGiocoOrso.CACCIATORE_TRE_IDLE_IMG


class Player:
    def __init__(self, name):
        self.name = name
        self.states_value = {}  # state -> value

    def get_action(self, actions, current_board: OrsoPyGame) -> tuple[int, int]:
        '''Return the action to take as tuple (startpos, endpos)'''
        value_max = -INFINITY
        for act in actions:
            current_board.move_player(act[0], act[1])
            state_value = self.states_value.get(current_board.get_hash())
            if (state_value is None):
                value = 0
            else:
                value = state_value

            if value >= value_max:
                value_max = value
                action = act

            current_board.undo_move()
        return action

    def print_value(self, board) -> None:
        print(
            f"{self.name}: {board.get_hash()} -> "
            f"{self.states_value.get(board.get_hash())}"
        )

    def load_policy(self, file) -> None:
        '''Load file with policy for reinforcement learning'''
        with open(file, 'rb') as file_read:
            data = pickle.load(file_read)
        # Policies are in states_value key
        self.states_value = (
            data if 'states_value' not in data else  # data legacy support
            data['states_value']
        )


# Main
if __name__ == "__main__":
    # Il gioco è richiamato da menu
    opg = OrsoPyGame()
    opg.menu()